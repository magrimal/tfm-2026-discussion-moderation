"""Domain models, pipeline state, and agent dependencies.

All Pydantic models and dataclasses shared across the facilitation
system. Models are grounded in the ADRs and serve as the typed
contract between agents, graph nodes, and API layers.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel

from discussion_moderation.common.constants import (
    ActionCategory,
    DiscussionState,
    FacilitationRole,
)

if TYPE_CHECKING:
    from discussion_moderation.settings.config import Settings
    from discussion_moderation.tools.base import LMSBackend


# --- Domain models ---


class Post(BaseModel):
    """A single post in a discussion thread.

    Description:
        Represents one contribution by a participant, with
        author attribution and timestamp for recency analysis.
    """

    author: str
    content: str
    timestamp: datetime


class DiscussionThread(BaseModel):
    """A discussion thread with pedagogical context.

    Description:
        The primary input to the facilitation pipeline. Includes
        the thread content (posts) and the pedagogical context
        (topic, learning objectives) needed for informed
        facilitation decisions.
    """

    topic: str
    learning_objectives: list[str]
    posts: list[Post]


class CourseContext(BaseModel):
    """Course-level context for prompt parameterization.

    Description:
        Provides the course setting that tools retrieve from the
        LMS backend. Used by role agents and the writer agent to
        adapt interventions to the specific audience and subject.
    """

    course_name: str
    module_topic: str
    audience_level: str
    language: str = "en"


# --- Agent output types ---


class ClassificationResult(BaseModel):
    """Phase 1 output: discussion state and intervention decision.

    Description:
        Produced by the classifier agent (ADR 0003, Fase 1).
        Determines the discussion state and whether intervention
        is warranted. The reasoning field provides the classifier's
        justification for auditability.
    """

    state: DiscussionState
    should_intervene: bool
    reasoning: str


class RoleSelection(BaseModel):
    """Phase 2 output: which facilitation role to activate.

    Description:
        Produced by the orchestrator agent. Selects a facilitation
        role (ADR 0004) based on the classification. The role
        agent then decides the specific action and technique.
    """

    role: FacilitationRole
    reasoning: str


class FacilitationResponse(BaseModel):
    """Phase 3 output: the generated facilitation intervention.

    Description:
        Produced by a role-specific agent. Contains the response
        text, the technique used (from ADR 0002 repertoire), and
        a confidence score for evaluation purposes.

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


class WriterOutput(BaseModel):
    """Writer agent output: adapted final text.

    Description:
        Produced by the optional writer agent. Adapts the role
        agent's response to the course audience and tone.
    """

    final_text: str
    adaptations_made: list[str] = []


class PipelineResult(BaseModel):
    """Complete pipeline output assembling all intermediate results.

    Description:
        The final output of the facilitation graph. Carries all
        intermediate results for auditability and evaluation.
        When no intervention is needed, only classification is
        populated.
    """

    classification: ClassificationResult
    role_selection: RoleSelection | None = None
    response: FacilitationResponse | None = None
    writer_output: WriterOutput | None = None
    final_text: str | None = None


# --- Pipeline graph state and deps ---


@dataclass
class PipelineState:
    """Mutable state accumulated across graph nodes.

    Description:
        Shared by all nodes in the pydantic_graph pipeline.
        Each node reads from and writes to this state to pass
        data to subsequent nodes.
    """

    thread: DiscussionThread
    classification: ClassificationResult | None = None
    role_selection: RoleSelection | None = None
    response: FacilitationResponse | None = None
    writer_output: WriterOutput | None = None
    orchestrator_attempts: int = 0
    eval_feedback: list[str] = field(default_factory=list)


@dataclass
class PipelineDeps:
    """Immutable configuration and services for the pipeline.

    Description:
        Read-only dependencies injected into the graph. Controls
        which evaluator nodes are active, retry limits, and
        provides access to the LMS backend and settings.
    """

    settings: "Settings"
    lms_backend: "LMSBackend | None" = None
    course_context: CourseContext | None = None
    classifier_eval_enabled: bool = False
    response_eval_enabled: bool = True
    writer_enabled: bool = False
    max_orchestrator_retries: int = 1


# --- Per-agent dependency types ---


@dataclass
class ClassifierDeps:
    """Dependencies for the classifier agent.

    Attributes:
        stalled_threshold_hours: Hours without posts before a
            thread is considered stalled.
        current_timestamp: Reference time for recency judgments.
        context_type: Description of the discussion context.
        course_context: Optional course context for prompt
            parameterization.
    """

    stalled_threshold_hours: int
    current_timestamp: datetime
    context_type: str = "asynchronous academic discussion threads"
    course_context: CourseContext | None = None


@dataclass
class OrchestratorDeps:
    """Dependencies for the orchestrator agent.

    Attributes:
        classification: The classifier's output.
        thread: The discussion thread being analyzed.
        context_type: Description of the discussion context.
        course_context: Optional course context.
        previous_feedback: Feedback from a failed retry, if any.
    """

    classification: ClassificationResult
    thread: DiscussionThread
    context_type: str = "asynchronous academic discussion threads"
    course_context: CourseContext | None = None
    previous_feedback: str | None = None


@dataclass
class RoleAgentDeps:
    """Dependencies for role-specific agents.

    Attributes:
        role_selection: The orchestrator's role selection.
        classification: The classifier's output.
        thread: The discussion thread.
        context_type: Description of the discussion context.
        course_context: Optional course context.
        lms_backend: Optional LMS backend for tool calls.
    """

    role_selection: RoleSelection
    classification: ClassificationResult
    thread: DiscussionThread
    context_type: str = "asynchronous academic discussion threads"
    course_context: CourseContext | None = None
    lms_backend: "LMSBackend | None" = None


@dataclass
class WriterDeps:
    """Dependencies for the writer agent.

    Attributes:
        response: The role agent's facilitation response.
        thread: The discussion thread.
        course_context: Optional course context for adaptation.
    """

    response: FacilitationResponse
    thread: DiscussionThread
    course_context: CourseContext | None = None
