"""Graph nodes for the facilitation pipeline.

Each node wraps an agent call and reads/writes to the shared
PipelineState. Nodes provide data; agents own prompt construction.
The classification_eval_enabled and response_eval_enabled flags in
PipelineDeps toggle optional validation nodes.
"""

from dataclasses import dataclass
from datetime import UTC, datetime

from pydantic_graph import BaseNode, End, GraphRunContext

from discussion_moderation.agents.classification import (
    ClassificationDeps,
    classification_agent,
)
from discussion_moderation.agents.intervention import (
    InterventionDeps,
    intervention_agent,
)
from discussion_moderation.agents.orchestrator import (
    OrchestratorDeps,
    orchestrator,
)
from discussion_moderation.agents.roles import ROLE_AGENTS, RoleAgentDeps
from discussion_moderation.constants import FacilitationRole
from discussion_moderation.models import (
    FacilitationResponse,
    PipelineDeps,
    PipelineResult,
    PipelineState,
)

Ctx = GraphRunContext[PipelineState, PipelineDeps]


@dataclass
class ClassificationNode(
    BaseNode[PipelineState, PipelineDeps, PipelineResult],
):
    """Detect the discussion state and participation trajectory."""

    async def run(self, ctx: Ctx) -> "ClassificationEvalNode":
        """Run the classification agent and store the result.

        Args:
            ctx: Graph run context with pipeline state and deps.

        Returns:
            ClassificationEvalNode to validate the result.
        """
        deps = ClassificationDeps(
            stalled_threshold_hours=ctx.deps.settings.stalled_threshold_hours,
            current_timestamp=datetime.now(UTC),
            discussion_context=ctx.deps.settings.discussion_context,
        )
        ctx.state.classification = await classification_agent.run(
            ctx.state.thread, deps
        )
        return ClassificationEvalNode()


@dataclass
class ClassificationEvalNode(
    BaseNode[PipelineState, PipelineDeps, PipelineResult],
):
    """Validate classification and pass to intervention agent."""

    async def run(self, ctx: Ctx) -> "InterventionNode":
        """Optionally validate classification then proceed.

        Args:
            ctx: Graph run context with pipeline state and deps.

        Returns:
            InterventionNode to decide whether to act.
        """
        classification = ctx.state.classification
        assert classification is not None

        if ctx.deps.classification_eval_enabled:
            if not classification.reasoning:
                ctx.state.eval_feedback.append(
                    "Classification agent provided no reasoning."
                )

        return InterventionNode()


@dataclass
class InterventionNode(
    BaseNode[PipelineState, PipelineDeps, PipelineResult],
):
    """Decide whether to intervene based on the classification."""

    async def run(self, ctx: Ctx) -> "InterventionEvalNode":
        """Run the intervention agent and store the decision.

        Args:
            ctx: Graph run context with pipeline state and deps.

        Returns:
            InterventionEvalNode to route based on the decision.
        """
        classification = ctx.state.classification
        assert classification is not None

        deps = InterventionDeps(
            classification=classification,
            stalled_threshold_hours=ctx.deps.settings.stalled_threshold_hours,
            current_timestamp=datetime.now(UTC),
            discussion_context=ctx.deps.settings.discussion_context,
        )
        ctx.state.intervention = await intervention_agent.run(
            ctx.state.thread, deps
        )
        return InterventionEvalNode()


@dataclass
class InterventionEvalNode(
    BaseNode[PipelineState, PipelineDeps, PipelineResult],
):
    """Route to orchestrator or end based on intervention decision."""

    async def run(self, ctx: Ctx) -> "OrchestratorNode | End[PipelineResult]":
        """Route based on should_intervene.

        Args:
            ctx: Graph run context with pipeline state and deps.

        Returns:
            OrchestratorNode if intervention is warranted,
            End with classification and intervention otherwise.
        """
        classification = ctx.state.classification
        intervention = ctx.state.intervention
        assert classification is not None
        assert intervention is not None

        if not intervention.should_intervene:
            return End(
                PipelineResult(
                    classification=classification,
                    intervention=intervention,
                )
            )

        return OrchestratorNode()


@dataclass
class OrchestratorNode(
    BaseNode[PipelineState, PipelineDeps, PipelineResult],
):
    """Select which facilitation role to activate."""

    async def run(self, ctx: Ctx) -> "RoleNode":
        """Run the orchestrator agent and store the role selection.

        Args:
            ctx: Graph run context with pipeline state and deps.

        Returns:
            RoleNode to generate the facilitation response.
        """
        classification = ctx.state.classification
        intervention = ctx.state.intervention
        assert classification is not None
        assert intervention is not None

        ctx.state.orchestrator_attempts += 1

        previous_feedback = None
        if ctx.state.eval_feedback:
            previous_feedback = "; ".join(ctx.state.eval_feedback)
            ctx.state.eval_feedback.clear()

        deps = OrchestratorDeps(
            classification=classification,
            intervention=intervention,
            thread=ctx.state.thread,
            discussion_context=ctx.deps.settings.discussion_context,
            previous_feedback=previous_feedback,
        )
        ctx.state.role_selection = await orchestrator.run(
            ctx.state.thread, deps
        )
        return RoleNode()


@dataclass
class RoleNode(
    BaseNode[PipelineState, PipelineDeps, PipelineResult],
):
    """Generate a facilitation response using the selected role."""

    async def run(self, ctx: Ctx) -> "ResponseEvalNode":
        """Run the selected role agent and store the response.

        Args:
            ctx: Graph run context with pipeline state and deps.

        Returns:
            ResponseEvalNode to validate the response.
        """
        classification = ctx.state.classification
        intervention = ctx.state.intervention
        role_selection = ctx.state.role_selection
        assert classification is not None
        assert intervention is not None
        assert role_selection is not None

        deps = RoleAgentDeps(
            role_selection=role_selection,
            classification=classification,
            intervention=intervention,
            thread=ctx.state.thread,
            discussion_context=ctx.deps.settings.discussion_context,
            lms_backend=ctx.deps.lms_backend,
            history_store=ctx.deps.history_store,
        )
        ctx.state.response = await ROLE_AGENTS[role_selection.role].run(
            ctx.state.thread, deps
        )
        return ResponseEvalNode()


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

    async def run(self, ctx: Ctx) -> "OrchestratorNode | End[PipelineResult]":
        """Validate rule checks and route to retry or end.

        Args:
            ctx: Graph run context with pipeline state and deps.

        Returns:
            OrchestratorNode to retry if rule checks fail,
            End with the response otherwise.
        """
        classification = ctx.state.classification
        intervention = ctx.state.intervention
        role_selection = ctx.state.role_selection
        response = ctx.state.response
        assert classification is not None
        assert intervention is not None
        assert role_selection is not None
        assert response is not None

        if ctx.deps.response_eval_enabled:
            issues = _run_response_rule_checks(response, role_selection.role)
            if issues:
                max_attempts = 1 + ctx.deps.max_orchestrator_retries
                if ctx.state.orchestrator_attempts < max_attempts:
                    ctx.state.eval_feedback.extend(issues)
                    return OrchestratorNode()

        return End(
            PipelineResult(
                classification=classification,
                intervention=intervention,
                role_selection=role_selection,
                response=response,
                final_text=response.response_text,
            )
        )
