"""Intervention agent: Phase 1b of the intervention model.

Receives the classification result and decides whether facilitation
intervention is warranted. Owns the timing and conservatism logic
(ADR 0003, Fase 1; ADR 0008).
"""

import json
from dataclasses import dataclass
from datetime import datetime

from pydantic_ai import Agent, RunContext

from discussion_moderation.agents.base import AgentMixin
from discussion_moderation.config import build_model, get_settings
from discussion_moderation.models import (
    ClassificationResult,
    DiscussionThread,
    InterventionDecision,
)
from discussion_moderation.utils import cap_reasoning, format_thread


@dataclass
class InterventionDeps:
    """Dependencies for the intervention agent.

    Attributes:
        classification: The classification agent's output.
        stalled_threshold_hours: Hours threshold used in
            classification, forwarded for context.
        current_timestamp: Reference time for recency judgments.
        discussion_context: Human-readable description of the
            discussion type. Injected into the prompt so the
            agent knows the deployment context.
    """

    classification: ClassificationResult
    stalled_threshold_hours: int
    current_timestamp: datetime
    discussion_context: str


class InterventionAgent(AgentMixin):
    """Intervention agent: decides whether to act on a classification."""

    PERSONALITY = """\
You are a facilitation timing expert for academic discussion threads.\
"""

    CONSTRAINTS = """\
You do not select a role or generate a response - those belong to the
next pipeline nodes.

Your default is not to intervene. Unnecessary interventions disrupt
productive struggle, signal distrust, and shift discussions
facilitator-centered. A missed intervention is the lesser harm.

Trajectory over snapshot: a thread that was active and has gone quiet
signals something different from one that never started. Declining
engagement is more urgent than flat non-engagement.

Silence is not impasse. A quiet thread is not proof that students are
stuck. Act only on evidence of genuine blockage: repeated unproductive
loops, explicit confusion, or participation collapse after prior
activity.

Cooldown matters. Consecutive interventions in a short window erode
student ownership. Weight prior intervention history when available.

When in doubt, do not intervene.\
"""

    CONTEXT_TEMPLATE = """\
Discussion context: {discussion_context}
Current timestamp: {current_timestamp}

Classification:
  State: **{discussion_state}**
  Reasoning: {classification_reasoning}\
"""

    INSTRUCTIONS = """\
Based on the classification above, decide whether to intervene.

Consider:
- Does the trajectory (as described in the classification
  reasoning) indicate a genuine need?
- Is this silence/state evidence of blockage, or normal
  discussion rhythm?
- Would intervening now disrupt productive activity?

Output should_intervene = true only when the evidence clearly
warrants it. In all other cases, output false.

Your reasoning will be forwarded to the role agent to help it
choose the right technique, so be specific about what pattern
in the thread is driving your decision. Keep it to 2-3
sentences - specific, not exhaustive.\
"""

    def __init__(self, model: object = None) -> None:
        """Initialize the intervention agent.

        Args:
            model: Optional pydantic-ai model override. Defaults to the
                model configured via FACILITATION_INTERVENTION_MODEL
                or FACILITATION_LLM_MODEL.
        """
        settings = get_settings()
        model_str = settings.model_for("intervention")
        self.agent = Agent(
            model or build_model(model_str, settings.llm_api_key),
            output_type=self.resolve_output_type(
                self._effective_model_str(model, model_str),
                InterventionDecision,
                settings.model_extraction_overrides,
            ),
            retries=3,
        )
        self.register_system_prompt()

    def build_system_prompt(self, ctx: RunContext[InterventionDeps]) -> str:
        """Build the system prompt with runtime context values.

        Args:
            ctx: Run context with intervention dependencies.

        Returns:
            Formatted system prompt string.
        """
        return self.build_prompt().format(
            discussion_context=ctx.deps.discussion_context,
            current_timestamp=ctx.deps.current_timestamp.isoformat(),
            discussion_state=ctx.deps.classification.state.value,
            classification_reasoning=cap_reasoning(
                ctx.deps.classification.reasoning
            ),
        )

    async def run(
        self,
        thread: DiscussionThread,
        deps: InterventionDeps,
    ) -> tuple[InterventionDecision, list[dict]]:
        """Decide whether to intervene on a classified thread.

        Args:
            thread: The discussion thread.
            deps: Intervention dependencies including classification.

        Returns:
            Tuple of (InterventionDecision, serialized agent messages).
        """
        prompt = format_thread(thread, now=deps.current_timestamp)
        result = await self.agent.run(prompt, deps=deps)
        messages = json.loads(result.all_messages_json())
        return result.output, messages


intervention_agent = InterventionAgent()
