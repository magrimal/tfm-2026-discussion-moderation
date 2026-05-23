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


class Comment(BaseModel):
    """A single reply in a discussion thread.

    Attributes:
        author: Username of the post author.
        body: Plain-text post content.
        created_at: When the post was submitted.
        author_label: Role label next to the author name,
            e.g. "Instructor" or "Community TA". None for students.
        endorsed: Marked as accepted answer in question-type threads.
        abuse_flagged: Flagged for review by participants or platform.
        vote_count: Number of upvotes or likes received.
        replies: Nested replies to this post.
    """

    author: str
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

    Attributes:
        id: Platform-assigned thread identifier.
        course_id: Course this thread belongs to.
        title: Thread title as shown to participants.
        body: Opening argument posted by the thread author.
        author: Username of the thread author.
        author_label: Role label for the thread author, if any.
        created_at: When the thread was opened.
        learning_objectives: Pedagogical goals for this discussion.
            Not available from the thread API; injected by the caller.
        comments: Replies to the opening argument.
        thread_type: "discussion" for open-ended threads,
            "question" for threads expecting a correct answer.
        last_activity_at: Most recent post or edit timestamp.
        closed: Whether the thread is closed to new posts.
        has_endorsed: Whether a question-type thread has an
            accepted answer. When True, intervention is likely
            unnecessary.
    """

    id: str
    course_id: str
    title: str
    body: str = ""
    author: str = ""
    author_label: str | None = None
    created_at: datetime
    learning_objectives: list[str] = []
    comments: list[Comment] = []
    thread_type: str = "discussion"
    last_activity_at: datetime | None = None
    closed: bool = False
    has_endorsed: bool = False


class ThreadSummary(BaseModel):
    """Lightweight thread descriptor returned by list_threads.

    Enough information to pick a thread for a run without fetching full content.
    """

    id: str
    course_id: str
    title: str
    body: str = ""
    author: str = ""
    comment_count: int = 0


class CourseContext(BaseModel):
    """Course-level context for prompt parameterization.

    Populated by the Django plugin endpoint GET
    /api/facilitation/v1/course-context/{course_id}/.

    Fields derivable from get_user_course_outline:
    - display_name: CourseOutlineData.title
    - sections: list of CourseSectionData.title values

    Fields that require separate course metadata (XBlock fields or
    custom course catalog entries):
    - module_topic: the current pedagogical topic
    - audience_level: e.g. "undergraduate", "graduate"
    - language: course language code (e.g. "en", "es")
    """

    course_id: str
    display_name: str
    sections: list[str] = []
    module_topic: str = ""
    audience_level: str = ""
    language: str = "en"


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
        confidence: Self-assessed confidence in this classification
            (0.0 to 1.0). Research parameter only.
    """

    state: DiscussionState
    trajectory: DiscussionTrajectory
    participation_balance: ParticipationBalance
    discourse_quality: DiscourseQuality
    inquiry_phase: InquiryPhase
    reasoning: str
    confidence: float = 1.0


class InterventionDecision(BaseModel):
    """Phase 1b output: whether to intervene and why.

    Attributes:
        should_intervene: Whether the pipeline should generate
            a facilitation response.
        reasoning: Explanation of the intervention decision,
            including timing and trajectory factors. Forwarded
            to the role agent to inform technique selection.
        confidence: Self-assessed confidence in this decision
            (0.0 to 1.0). Research parameter only.
    """

    should_intervene: bool
    reasoning: str
    confidence: float = 1.0


class RoleSelection(BaseModel):
    """Phase 2 output: which facilitation role to activate.

    Attributes:
        role: The facilitation role selected for this intervention.
        reasoning: Justification for the role selection.
        confidence: Self-assessed confidence in this role selection
            (0.0 to 1.0). Research parameter only.
    """

    role: FacilitationRole
    reasoning: str
    confidence: float = 1.0


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
    raw_response: str | None = None


@dataclass
class PipelineDeps:
    """Immutable configuration and services for the pipeline."""

    settings: "Settings"
    lms_backend: "LMSBackend | None" = None
    history_store: "ThreadHistoryStore | None" = None
