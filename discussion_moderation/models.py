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
    DiscussionState,
    FacilitationRole,
)

if TYPE_CHECKING:
    from discussion_moderation.config import Settings
    from discussion_moderation.tools.base import LMSBackend
    from discussion_moderation.tools.history import ThreadHistoryStore


# --- Domain models ---


class Comment(BaseModel):
    """A single response in a discussion thread.

    Field names follow the Open edX forum API (cs_comments_service).
    """

    username: str
    body: str
    created_at: datetime


class DiscussionThread(BaseModel):
    """A discussion thread with pedagogical context.

    Core fields follow the Open edX forum API thread schema.
    learning_objectives is our addition for facilitation context.
    """

    id: str
    course_id: str
    title: str
    learning_objectives: list[str]
    created_at: datetime
    children: list[Comment] = []
    thread_type: str = "discussion"
    last_activity_at: datetime | None = None
    closed: bool = False


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
        state: The detected discussion state.
        reasoning: Explanation of how the state was identified,
            including participation trajectory. Forwarded to
            downstream agents to inform technique selection.
    """

    state: DiscussionState
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
        response_text: The facilitation message to post.
        technique_used: Name of the technique from the repertoire.
        action_category: The action category selected.
        confidence: Self-assessed confidence (0.0 to 1.0).
        reasoning: Justification for technique selection.
    """

    response_text: str
    technique_used: str
    action_category: ActionCategory
    confidence: float = 1.0
    reasoning: str = ""


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
