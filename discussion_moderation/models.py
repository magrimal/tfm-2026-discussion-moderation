"""Domain models and pipeline types.

Pydantic models and dataclasses shared across the facilitation
system. Agent-specific dependency types live in their respective
agent modules.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel

from discussion_moderation.constants import (
    ActionCategory,
    DiscourseQuality,
    DiscussionState,
    DiscussionTrajectory,
    FacilitationRole,
    InquiryPhase,
    ParticipationBalance,
)

if TYPE_CHECKING:
    from discussion_moderation.config import Settings
    from discussion_moderation.tools.history import ThreadHistoryStore
    from discussion_moderation.tools.protocols import LMSBackend


# --- Domain models ---


class Comment(BaseModel):
    """A single post in a discussion thread.

    Generic across platforms. Fields common to any asynchronous
    discussion system. Platform-specific backends populate the
    optional fields when available.

    Attributes:
        username: Display name of the author.
        body: Plain-text post content.
        created_at: When the post was submitted.
        author_label: Role label shown next to the author name,
            e.g. "Instructor" or "Community TA". None for students.
        endorsed: Whether this post is marked as an accepted answer
            (relevant for question-type threads).
        abuse_flagged: Whether the post has been flagged for review
            by participants or the platform.
        vote_count: Number of upvotes or likes received.
        replies: Nested replies to this post. Preserves the thread
            tree structure provided by the platform.
    """

    username: str
    body: str
    created_at: datetime
    author_label: str | None = None
    endorsed: bool = False
    abuse_flagged: bool = False
    vote_count: int = 0
    replies: list["Comment"] = []


Comment.model_rebuild()


class DiscussionThread(BaseModel):
    """A discussion thread with pedagogical context.

    Generic across platforms. Core fields cover what any
    asynchronous discussion platform provides. Backends are
    responsible for populating the fields they can fill.
    learning_objectives is our addition for facilitation context
    and is injected from course metadata when available.

    Attributes:
        id: Platform-assigned thread identifier.
        course_id: Course this thread belongs to.
        title: Thread title as shown to participants.
        created_at: When the thread was opened.
        learning_objectives: Pedagogical goals for this discussion.
            Optional: populated from course metadata by the caller,
            not from the thread itself.
        children: Top-level posts in the thread, including the
            opening post. Each post may contain nested replies.
        thread_type: "discussion" for open-ended threads,
            "question" for threads expecting a correct answer.
        last_activity_at: Most recent post or edit timestamp.
            More reliable than inferring from children timestamps
            when provided by the platform.
        closed: Whether the thread is closed to new posts.
        has_endorsed: Whether a question-type thread has an
            accepted answer. When True, intervention is likely
            unnecessary.
    """

    id: str
    course_id: str
    title: str
    created_at: datetime
    learning_objectives: list[str] = []
    children: list[Comment] = []
    thread_type: str = "discussion"
    last_activity_at: datetime | None = None
    closed: bool = False
    has_endorsed: bool = False


class CourseContext(BaseModel):
    """Course-level context for prompt parameterization.

    Fields follow the Open edX course API (course blocks endpoint).
    """

    course_id: str
    display_name: str
    module_topic: str
    audience_level: str
    language: str = "en"


# --- Agent output types ---


class ClassificationResult(BaseModel):
    """Phase 1a output: discussion state detection.

    Attributes:
        state: The detected discussion state (primary label).
        trajectory: Temporal engagement pattern of the thread.
        participation_balance: Participation structure across
            contributors (distributed, dominated, or instructor-
            centered).
        discourse_quality: Whether posts are substantive,
            formulaic, or mixed.
        inquiry_phase: Where the thread sits in the Practical
            Inquiry Model (Garrison et al. 2001).
        reasoning: Free-text explanation of the classification.
            Forwarded to downstream agents to inform technique
            selection.
    """

    state: DiscussionState
    trajectory: DiscussionTrajectory
    participation_balance: ParticipationBalance
    discourse_quality: DiscourseQuality
    inquiry_phase: InquiryPhase
    reasoning: str


class InterventionDecision(BaseModel):
    """Phase 1b output: whether to intervene and why.

    Attributes:
        should_intervene: Whether the pipeline should generate
            a facilitation response.
        reasoning: Explanation of the intervention decision,
            including timing and trajectory factors. Forwarded
            to the role agent to inform technique selection.
    """

    should_intervene: bool
    reasoning: str


class RoleSelection(BaseModel):
    """Phase 2 output: which facilitation role to activate."""

    role: FacilitationRole
    reasoning: str


class FacilitationResponse(BaseModel):
    """Phase 3 output: the generated facilitation intervention.

    Attributes:
        response_text: The intervention content. Posted to the thread
            when post_to_thread is True; routed to the instructor
            privately when False (e.g. instructor_escalation).
        technique_used: Name of the technique from the repertoire.
        action_category: The action category selected.
        confidence: Self-assessed confidence (0.0 to 1.0).
        reasoning: Justification for technique selection.
        post_to_thread: Whether to post response_text to the
            discussion thread. False means the content is for the
            instructor only and must not be visible to students.
    """

    response_text: str
    technique_used: str
    action_category: ActionCategory
    confidence: float = 1.0
    reasoning: str = ""
    post_to_thread: bool = True


class PipelineResult(BaseModel):
    """Complete pipeline output assembling all intermediate results."""

    classification: ClassificationResult
    intervention: InterventionDecision | None = None
    role_selection: RoleSelection | None = None
    response: FacilitationResponse | None = None
    final_text: str | None = None


# --- Pipeline graph state and deps ---


@dataclass
class PipelineState:
    """Mutable state accumulated across graph nodes."""

    thread: DiscussionThread
    classification: ClassificationResult | None = None
    intervention: InterventionDecision | None = None
    role_selection: RoleSelection | None = None
    response: FacilitationResponse | None = None
    orchestrator_attempts: int = 0
    eval_feedback: list[str] = field(default_factory=list)


@dataclass
class PipelineDeps:
    """Immutable configuration and services for the pipeline."""

    settings: "Settings"
    lms_backend: "LMSBackend | None" = None
    history_store: "ThreadHistoryStore | None" = None
    classification_eval_enabled: bool = False
    response_eval_enabled: bool = True
    max_orchestrator_retries: int = 1
