"""Graph nodes for the facilitation pipeline.

Each node wraps an agent call and reads/writes to the shared
PipelineState. Nodes provide data; agents own prompt construction.
Evaluator nodes are toggleable via PipelineDeps configuration.
"""

from dataclasses import dataclass
from datetime import UTC, datetime

from pydantic_graph import BaseNode, End, GraphRunContext

from discussion_moderation.agents.classifier import ClassifierDeps
from discussion_moderation.agents.orchestrator import OrchestratorDeps
from discussion_moderation.agents.roles import RoleAgentDeps
from discussion_moderation.agents.writer import WriterDeps
from discussion_moderation.constants import FacilitationRole
from discussion_moderation.models import (
    FacilitationResponse,
    PipelineDeps,
    PipelineResult,
    PipelineState,
)

# Type alias for our graph context.
Ctx = GraphRunContext[PipelineState, PipelineDeps]


# --- Classifier ---


@dataclass
class ClassifierNode(
    BaseNode[PipelineState, PipelineDeps, PipelineResult],
):
    """Classify the discussion state and decide on intervention."""

    async def run(self, ctx: Ctx) -> "ClassifierEvalNode":
        from discussion_moderation.agents.classifier import classifier

        deps = ClassifierDeps(
            stalled_threshold_hours=ctx.deps.settings.stalled_threshold_hours,
            current_timestamp=datetime.now(UTC),
            context_type=ctx.deps.settings.context_type,
        )
        ctx.state.classification = await classifier.run(
            ctx.state.thread, deps
        )
        return ClassifierEvalNode()


# --- Classifier evaluator ---


@dataclass
class ClassifierEvalNode(
    BaseNode[PipelineState, PipelineDeps, PipelineResult],
):
    """Validate classification and route based on intervention decision."""

    async def run(
        self, ctx: Ctx
    ) -> "OrchestratorNode | End[PipelineResult]":
        classification = ctx.state.classification
        assert classification is not None

        if ctx.deps.classifier_eval_enabled:
            if not classification.reasoning:
                ctx.state.eval_feedback.append(
                    "Classifier provided no reasoning."
                )

        if not classification.should_intervene:
            return End(PipelineResult(classification=classification))

        return OrchestratorNode()


# --- Orchestrator ---


@dataclass
class OrchestratorNode(
    BaseNode[PipelineState, PipelineDeps, PipelineResult],
):
    """Select which facilitation role to activate."""

    async def run(self, ctx: Ctx) -> "RoleNode":
        from discussion_moderation.agents.orchestrator import orchestrator

        classification = ctx.state.classification
        assert classification is not None

        ctx.state.orchestrator_attempts += 1

        previous_feedback = None
        if ctx.state.eval_feedback:
            previous_feedback = "; ".join(ctx.state.eval_feedback)
            ctx.state.eval_feedback.clear()

        deps = OrchestratorDeps(
            classification=classification,
            thread=ctx.state.thread,
            context_type=ctx.deps.settings.context_type,
            previous_feedback=previous_feedback,
        )
        ctx.state.role_selection = await orchestrator.run(
            ctx.state.thread, deps
        )
        return RoleNode()


# --- Role agent ---


@dataclass
class RoleNode(
    BaseNode[PipelineState, PipelineDeps, PipelineResult],
):
    """Generate a facilitation response using the selected role."""

    async def run(self, ctx: Ctx) -> "ResponseEvalNode":
        from discussion_moderation.agents.roles import ROLE_AGENTS

        classification = ctx.state.classification
        role_selection = ctx.state.role_selection
        assert classification is not None
        assert role_selection is not None

        deps = RoleAgentDeps(
            role_selection=role_selection,
            classification=classification,
            thread=ctx.state.thread,
            context_type=ctx.deps.settings.context_type,
            lms_backend=ctx.deps.lms_backend,
            history_store=ctx.deps.history_store,
        )
        ctx.state.response = await ROLE_AGENTS[role_selection.role].run(
            ctx.state.thread, deps
        )
        return ResponseEvalNode()


# --- Response evaluator ---

# Phrases that indicate evaluative/grading language (invariant:
# the system facilitates, it does not evaluate).
_EVALUATIVE_PHRASES = [
    "grade",
    "grading",
    "scored",
    "points",
    "correct answer",
    "wrong answer",
    "mark",
    "pass or fail",
]


def _run_response_rule_checks(
    response: FacilitationResponse,
    role: FacilitationRole,
) -> list[str]:
    issues: list[str] = []
    if not response.response_text.strip():
        issues.append("Response text is empty.")
    if not response.technique_used.strip():
        issues.append("No technique specified.")
    text_lower = response.response_text.lower()
    for phrase in _EVALUATIVE_PHRASES:
        if phrase in text_lower:
            issues.append(f"Evaluative language detected: '{phrase}'.")
            break
    return issues


@dataclass
class ResponseEvalNode(
    BaseNode[PipelineState, PipelineDeps, PipelineResult],
):
    """Validate the response and decide on retry or proceed."""

    async def run(
        self, ctx: Ctx
    ) -> "OrchestratorNode | WriterNode | End[PipelineResult]":
        classification = ctx.state.classification
        role_selection = ctx.state.role_selection
        response = ctx.state.response
        assert classification is not None
        assert role_selection is not None
        assert response is not None

        if ctx.deps.response_eval_enabled:
            issues = _run_response_rule_checks(response, role_selection.role)
            if issues:
                max_attempts = 1 + ctx.deps.max_orchestrator_retries
                if ctx.state.orchestrator_attempts < max_attempts:
                    ctx.state.eval_feedback.extend(issues)
                    return OrchestratorNode()

        if ctx.deps.writer_enabled:
            return WriterNode()

        return End(
            PipelineResult(
                classification=classification,
                role_selection=role_selection,
                response=response,
                final_text=response.response_text,
            )
        )


# --- Writer ---


@dataclass
class WriterNode(
    BaseNode[PipelineState, PipelineDeps, PipelineResult],
):
    """Adapt the response for the target audience."""

    async def run(self, ctx: Ctx) -> End[PipelineResult]:
        from discussion_moderation.agents.writer import writer

        classification = ctx.state.classification
        role_selection = ctx.state.role_selection
        response = ctx.state.response
        assert classification is not None
        assert role_selection is not None
        assert response is not None

        deps = WriterDeps(
            response=response,
            thread=ctx.state.thread,
            lms_backend=ctx.deps.lms_backend,
        )
        writer_output = await writer.run(deps)
        ctx.state.writer_output = writer_output

        return End(
            PipelineResult(
                classification=classification,
                role_selection=role_selection,
                response=response,
                writer_output=writer_output,
                final_text=writer_output.final_text,
            )
        )
