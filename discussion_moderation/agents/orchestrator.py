"""Orchestrator agent: Phase 2 role selection.

Selects which facilitation role should handle the intervention
based on the classification result (ADR 0004). Does NOT select
the action or technique — that is the role agent's responsibility.
"""

from pydantic_ai import Agent, RunContext

from discussion_moderation.agents.base import AgentMixin
from discussion_moderation.common.formatters import (
    format_role_descriptions,
)
from discussion_moderation.common.models import (
    OrchestratorDeps,
    RoleSelection,
)
from discussion_moderation.common.prompts import ORCHESTRATOR_PROMPT


class OrchestratorAgent(AgentMixin):
    """Orchestrator agent using the AgentMixin pattern."""

    def __init__(self) -> None:
        self.agent: Agent[OrchestratorDeps, RoleSelection] = Agent(
            "anthropic:claude-sonnet-4-20250514",
            output_type=RoleSelection,
        )
        self._register_system_prompt()

    def _build_system_prompt(self, ctx: RunContext[OrchestratorDeps]) -> str:
        retry_context = ""
        if ctx.deps.previous_feedback:
            retry_context = (
                f"\n\nPrevious attempt feedback: "
                f"{ctx.deps.previous_feedback}\n"
                "Select a DIFFERENT role this time."
            )
        return ORCHESTRATOR_PROMPT.format(
            context_type=ctx.deps.context_type,
            discussion_state=ctx.deps.classification.state.value,
            classification_reasoning=(ctx.deps.classification.reasoning),
            role_descriptions=format_role_descriptions(),
            retry_context=retry_context,
        )


select_role = OrchestratorAgent().agent
