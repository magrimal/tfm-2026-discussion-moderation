"""Graph nodes for the facilitation pipeline.

Each node wraps a pydantic-ai agent call and reads/writes to the
shared PipelineState. Evaluator nodes are toggleable via
PipelineDeps configuration.
"""

from dataclasses import dataclass
from datetime import UTC, datetime

from pydantic_graph import BaseNode, End, GraphRunContext

from discussion_moderation.common.constants import (
    FacilitationRole,
)
from discussion_moderation.common.formatters import format_thread
from discussion_moderation.common.models import (
    ClassifierDeps,
    FacilitationResponse,
    OrchestratorDeps,
    PipelineDeps,
    PipelineResult,
    PipelineState,
    RoleAgentDeps,
    WriterDeps,
)

# Type alias for our graph context.
Ctx = GraphRunContext[PipelineState, PipelineDeps]


# --- Classifier ---


@dataclass
class ClassifierNode(
    BaseNode[PipelineState, PipelineDeps, PipelineResult],
):
    """Classify the discussion state and decide on intervention.

    Description:
        Phase 1 of the intervention model. Calls the classifier
        agent and stores the result in pipeline state.
    """

    async def run(
        self,
        ctx: Ctx,
    ) -> "ClassifierEvalNode":
        from discussion_moderation.agents.classifier import classify

        deps = ClassifierDeps(
            stalled_threshold_hours=(ctx.deps.settings.stalled_threshold_hours),
            current_timestamp=datetime.now(UTC),
            context_type=ctx.deps.settings.context_type,
        )
        prompt = format_thread(ctx.state.thread, now=deps.current_timestamp)
        result = await classify.run(prompt, deps=deps)
        ctx.state.classification = result.output
        return ClassifierEvalNode()


# --- Classifier evaluator ---


@dataclass
class ClassifierEvalNode(
    BaseNode[PipelineState, PipelineDeps, PipelineResult],
):
    """Validate classification and route based on intervention decision.

    Description:
        When enabled, runs rule-based checks on the classification.
        Routes to OrchestratorNode if intervention is needed, or
        ends the pipeline if not.
    """

    async def run(
        self,
        ctx: Ctx,
    ) -> "OrchestratorNode | End[PipelineResult]":
        classification = ctx.state.classification
        assert classification is not None

        if ctx.deps.classifier_eval_enabled:
            # Rule-based checks
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
    """Select which facilitation role to activate.

    Description:
        Phase 2 of the intervention model. Calls the orchestrator
        agent to select a role. Tracks attempt count for retry
        logic.
    """

    async def run(self, ctx: Ctx) -> "RoleNode":
        from discussion_moderation.agents.orchestrator import select_role

        classification = ctx.state.classification
        assert classification is not None

        ctx.state.orchestrator_attempts += 1

        # Build feedback from previous failed attempt
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
        prompt = format_thread(ctx.state.thread)
        result = await select_role.run(prompt, deps=deps)
        ctx.state.role_selection = result.output
        return RoleNode()


# --- Role agent ---


@dataclass
class RoleNode(
    BaseNode[PipelineState, PipelineDeps, PipelineResult],
):
    """Generate a facilitation response using the selected role.

    Description:
        Phase 3 of the intervention model. Dispatches to the
        role-specific agent based on the orchestrator's selection.
    """

    async def run(self, ctx: Ctx) -> "ResponseEvalNode":
        from discussion_moderation.agents.roles import generate_response

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
        )
        ctx.state.response = await generate_response(
            role_selection.role,
            ctx.state.thread,
            deps,
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
    """Run rule-based checks on a facilitation response.

    Description:
        Checks structural properties of the response: non-empty,
        has a technique, no evaluative language.

    Args:
        response: The response to validate.
        role: The facilitation role that generated it.

    Returns:
        List of issues found (empty if all checks pass).
    """
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
    """Validate the response and decide on retry or proceed.

    Description:
        When enabled, runs rule-based checks on the response.
        If the response is not viable and retries remain, loops
        back to the orchestrator. Otherwise, proceeds to the
        writer or ends the pipeline.
    """

    async def run(
        self,
        ctx: Ctx,
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
                # Max retries exhausted — proceed with
                # whatever we have.

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
    """Adapt the response for the target audience.

    Description:
        Optional node. When writer is disabled in deps, this
        node should not be reached (ResponseEvalNode routes
        to End directly). If reached, runs the writer agent.
    """

    async def run(self, ctx: Ctx) -> End[PipelineResult]:
        from discussion_moderation.agents.writer import adapt_response

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
        prompt = (
            f"Original response:\n{response.response_text}\n\n"
            f"Technique used: {response.technique_used}\n"
            f"Action category: {response.action_category.value}"
        )
        result = await adapt_response.run(prompt, deps=deps)
        ctx.state.writer_output = result.output
        final_text = ctx.state.writer_output.final_text

        return End(
            PipelineResult(
                classification=classification,
                role_selection=role_selection,
                response=response,
                writer_output=ctx.state.writer_output,
                final_text=final_text,
            )
        )
