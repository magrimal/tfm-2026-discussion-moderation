"""Graph nodes for the facilitation pipeline.

Each node wraps an agent call and reads/writes to the shared
PipelineState. Nodes provide data; agents own prompt construction.
The classification_eval_enabled and response_eval_enabled flags in
PipelineDeps toggle optional validation within the nodes.
"""

import logging
from dataclasses import dataclass
from datetime import UTC, datetime

from pydantic_graph import BaseNode, End, GraphRunContext

from discussion_moderation.agents.classification import (
    ClassificationAgent,
    ClassificationDeps,
)
from discussion_moderation.agents.intervention import (
    InterventionAgent,
    InterventionDeps,
)
from discussion_moderation.agents.orchestrator import (
    OrchestratorAgent,
    OrchestratorDeps,
)
from discussion_moderation.agents.roles import (
    ROLE_AGENT_CLASSES_BY_ROLE,
    RoleAgentDeps,
)
from discussion_moderation.config import build_model
from discussion_moderation.constants import FacilitationRole
from discussion_moderation.models import (
    FacilitationResponse,
    PipelineDeps,
    PipelineResult,
    PipelineState,
)
from discussion_moderation.tools.history import InterventionRecord

logger = logging.getLogger(__name__)

Ctx = GraphRunContext[PipelineState, PipelineDeps]


@dataclass
class ClassificationNode(
    BaseNode[PipelineState, PipelineDeps, PipelineResult],
):
    """Detect the discussion state and participation trajectory."""

    async def run(self, ctx: Ctx) -> "InterventionNode":
        """Run the classification agent and store the result.

        Args:
            ctx: Graph run context with pipeline state and deps.

        Returns:
            InterventionNode to decide whether to intervene.
        """
        settings = ctx.deps.settings
        deps = ClassificationDeps(
            stalled_threshold_hours=settings.stalled_threshold_hours,
            current_timestamp=datetime.now(UTC),
            discussion_context=settings.discussion_context,
        )
        agent = ClassificationAgent(
            model=build_model(
                settings.model_for("classification"), settings.llm_api_key
            )
        )
        classification, cls_msgs = await agent.run(ctx.state.thread, deps)
        ctx.state.classification = classification
        ctx.state.pipeline_messages["classification"] = cls_msgs
        classification = ctx.state.classification
        logger.info(
            "[classification] state=%s trajectory=%s"
            " balance=%s quality=%s phase=%s",
            classification.state.value,
            classification.trajectory.value,
            classification.participation_balance.value,
            classification.discourse_quality.value,
            classification.inquiry_phase.value,
        )
        logger.debug("[classification] reasoning: %s", classification.reasoning)

        if settings.classifier_eval_enabled and not classification.reasoning:
            ctx.state.eval_feedback.append(
                "Classification agent provided no reasoning."
            )

        return InterventionNode()


@dataclass
class InterventionNode(
    BaseNode[PipelineState, PipelineDeps, PipelineResult],
):
    """Decide whether to intervene based on the classification."""

    async def run(self, ctx: Ctx) -> "OrchestratorNode | End[PipelineResult]":
        """Run the intervention agent and route based on the decision.

        Args:
            ctx: Graph run context with pipeline state and deps.

        Returns:
            OrchestratorNode if intervention is warranted,
            End with classification and intervention otherwise.
        """
        classification = ctx.state.classification
        assert classification is not None

        settings = ctx.deps.settings
        deps = InterventionDeps(
            classification=classification,
            stalled_threshold_hours=settings.stalled_threshold_hours,
            current_timestamp=datetime.now(UTC),
            discussion_context=settings.discussion_context,
        )
        agent = InterventionAgent(
            model=build_model(
                settings.model_for("intervention"), settings.llm_api_key
            )
        )
        try:
            intervention, int_msgs = await agent.run(ctx.state.thread, deps)
            ctx.state.intervention = intervention
            ctx.state.pipeline_messages["intervention"] = int_msgs
        except Exception as exc:
            logger.exception(
                "[intervention] agent failed, returning without decision: %s",
                exc,
            )
            exc_str = str(exc) or type(exc).__name__
            ctx.state.error = exc_str
            return End(
                PipelineResult(classification=classification, error=exc_str)
            )
        intervention = ctx.state.intervention
        logger.info(
            "[intervention] should_intervene=%s",
            intervention.should_intervene,
        )
        logger.debug("[intervention] reasoning: %s", intervention.reasoning)

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

    async def run(self, ctx: Ctx) -> "RoleNode | End[PipelineResult]":
        """Run the orchestrator agent and store the role selection.

        Args:
            ctx: Graph run context with pipeline state and deps.

        Returns:
            RoleNode to generate the facilitation response, or End if
            the orchestrator agent itself failed (ADR 0032).
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

        settings = ctx.deps.settings
        deps = OrchestratorDeps(
            classification=classification,
            intervention=intervention,
            thread=ctx.state.thread,
            discussion_context=settings.discussion_context,
            previous_feedback=previous_feedback,
        )
        orchestrator = OrchestratorAgent(
            model=build_model(
                settings.model_for("orchestrator"), settings.llm_api_key
            )
        )
        try:
            role_sel, orc_msgs = await orchestrator.run(ctx.state.thread, deps)
            ctx.state.role_selection = role_sel
            ctx.state.pipeline_messages["orchestrator"] = orc_msgs
        except Exception as exc:
            logger.exception(
                "[orchestrator] agent failed, returning without role: %s",
                exc,
            )
            exc_str = str(exc) or type(exc).__name__
            ctx.state.error = exc_str
            return End(
                PipelineResult(
                    classification=classification,
                    intervention=intervention,
                    error=exc_str,
                )
            )
        role_selection = ctx.state.role_selection
        logger.info("[orchestrator] role=%s", role_selection.role.value)
        logger.debug("[orchestrator] reasoning: %s", role_selection.reasoning)
        return RoleNode()


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
    """Return a list of rule violations found in the response."""
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
class RoleNode(
    BaseNode[PipelineState, PipelineDeps, PipelineResult],
):
    """Generate a facilitation response using the selected role."""

    async def run(self, ctx: Ctx) -> "OrchestratorNode | End[PipelineResult]":
        """Run the role agent, validate the response, and route.

        Validates rule checks when response_eval_enabled is set.
        Retries via OrchestratorNode up to max_orchestrator_retries
        times on rule violations. Records the intervention to history
        on success.

        Args:
            ctx: Graph run context with pipeline state and deps.

        Returns:
            OrchestratorNode to retry if rule checks fail,
            End with the full result otherwise.
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
        settings = ctx.deps.settings
        role_cls = ROLE_AGENT_CLASSES_BY_ROLE[role_selection.role]
        role_agent = role_cls(
            model=build_model(settings.model_for("role"), settings.llm_api_key)
        )
        try:
            ctx.state.response, ctx.state.messages = await role_agent.run(
                ctx.state.thread, deps
            )
            ctx.state.pipeline_messages["role"] = ctx.state.messages
        except Exception as exc:
            logger.exception(
                "[role:%s] agent failed, returning without response: %s",
                role_selection.role.value,
                exc,
            )
            exc_str = str(exc) or type(exc).__name__
            ctx.state.error = exc_str
            return End(
                PipelineResult(
                    classification=classification,
                    intervention=intervention,
                    role_selection=role_selection,
                    error=exc_str,
                )
            )
        response = ctx.state.response
        logger.info(
            "[role:%s] technique=%s category=%s confidence=%s post=%s",
            role_selection.role.value,
            response.technique_used,
            response.action_category.value,
            response.confidence,
            response.post_to_thread,
        )
        logger.debug(
            "[role:%s] response: %s",
            role_selection.role.value,
            response.response_text,
        )

        if settings.response_eval_enabled:
            issues = _run_response_rule_checks(response, role_selection.role)
            if issues:
                max_attempts = 1 + settings.max_orchestrator_retries
                if ctx.state.orchestrator_attempts < max_attempts:
                    ctx.state.eval_feedback.extend(issues)
                    return OrchestratorNode()

        if ctx.deps.history_store is not None:
            ctx.deps.history_store.record_intervention(
                ctx.state.thread.id,
                InterventionRecord(
                    thread_id=ctx.state.thread.id,
                    timestamp=datetime.now(UTC),
                    role=role_selection.role,
                    technique=response.technique_used,
                    reasoning=response.reasoning,
                    response_text=response.response_text,
                ),
            )

        return End(
            PipelineResult(
                classification=classification,
                intervention=intervention,
                role_selection=role_selection,
                response=response,
                final_text=response.response_text,
                messages=ctx.state.messages,
            )
        )
