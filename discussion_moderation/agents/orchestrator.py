"""Orchestrator agent: Phase 2 role selection.

Selects which facilitation role should handle the intervention
based on the classification result (ADR 0004). Does NOT select
the action or technique — that is the role agent's responsibility.
"""

from dataclasses import dataclass

from pydantic_ai import Agent, RunContext

from discussion_moderation.agents.base import AgentMixin
from discussion_moderation.models import (
    ClassificationResult,
    DiscussionThread,
    RoleSelection,
)
from discussion_moderation.utils import format_thread


@dataclass
class OrchestratorDeps:
    """Dependencies for the orchestrator agent.

    Attributes:
        classification: The classifier's output.
        thread: The discussion thread being analyzed.
        context_type: Description of the discussion context.
        previous_feedback: Feedback from a failed retry, if any.
    """

    classification: ClassificationResult
    thread: DiscussionThread
    context_type: str = "asynchronous academic discussion threads"
    previous_feedback: str | None = None


class OrchestratorAgent(AgentMixin):
    """Orchestrator agent using the AgentMixin pattern."""

    PROMPT = """\
# Personality
You are a facilitation role selector for {context_type}.

# Context
Discussion state: **{discussion_state}**
Classification reasoning: {classification_reasoning}

# Examples
No embedded examples. Select based on role descriptions below.

# Instructions
Select exactly ONE role. Do not select a specific action or \
technique — the role agent decides that. Explain why this role \
is the best fit for the current state.

Available roles:
{role_descriptions}
{retry_context}\
"""

    def __init__(self) -> None:
        self.agent: Agent[OrchestratorDeps, RoleSelection] = Agent(
            "anthropic:claude-sonnet-4-20250514",
            output_type=RoleSelection,
        )
        self._register_system_prompt()

    @staticmethod
    def _build_role_descriptions() -> str:
        from discussion_moderation.agents.roles import ROLE_AGENT_CLASSES

        return "\n".join(
            f"- **{cls.ROLE.value}**: {cls.DESCRIPTION}"
            for cls in ROLE_AGENT_CLASSES
        )

    def _build_system_prompt(self, ctx: RunContext[OrchestratorDeps]) -> str:
        retry_context = ""
        if ctx.deps.previous_feedback:
            retry_context = (
                f"\n\nPrevious attempt feedback: "
                f"{ctx.deps.previous_feedback}\n"
                "Select a DIFFERENT role this time."
            )
        return self.PROMPT.format(
            context_type=ctx.deps.context_type,
            discussion_state=ctx.deps.classification.state.value,
            classification_reasoning=ctx.deps.classification.reasoning,
            role_descriptions=self._build_role_descriptions(),
            retry_context=retry_context,
        )

    async def run(
        self,
        thread: DiscussionThread,
        deps: OrchestratorDeps,
    ) -> RoleSelection:
        """Select a facilitation role for a classified thread.

        Args:
            thread: The discussion thread.
            deps: Orchestrator dependencies including classification.

        Returns:
            RoleSelection with the chosen role and reasoning.
        """
        prompt = format_thread(thread)
        result = await self.agent.run(prompt, deps=deps)
        return result.output


orchestrator = OrchestratorAgent()
