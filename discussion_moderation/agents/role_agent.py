"""RoleAgent: AgentMixin-based factory for facilitation role agents."""

from pydantic_ai import Agent, RunContext

from discussion_moderation.agents.base import AgentMixin
from discussion_moderation.common.constants import (
    DiscussionState,
    FacilitationRole,
)
from discussion_moderation.common.models import (
    FacilitationResponse,
    RoleAgentDeps,
)
from discussion_moderation.common.prompts import (
    ROLE_INSTRUCTIONS,
    ROLE_PROMPT_BASE,
)
from discussion_moderation.tools.knowledge_base import (
    get_anti_patterns,
    get_techniques,
)


class RoleAgent(AgentMixin):
    """Role-specific facilitation agent using the AgentMixin pattern.

    Each instance is bound to a single FacilitationRole. The system
    prompt is built at runtime from RunContext deps. Two tools are
    registered: retrieve_techniques and retrieve_anti_patterns.
    """

    def __init__(
        self,
        role: FacilitationRole,
        model: str = "anthropic:claude-sonnet-4-20250514",
    ) -> None:
        self._role = role
        self.agent: Agent[RoleAgentDeps, FacilitationResponse] = Agent(
            model,
            output_type=FacilitationResponse,
        )
        self._register_system_prompt()
        self._register_tools()

    def _build_system_prompt(self, ctx: RunContext[RoleAgentDeps]) -> str:
        return ROLE_PROMPT_BASE.format(
            role_name=self._role.value,
            context_type=ctx.deps.context_type,
            discussion_state=(ctx.deps.classification.state.value),
            selection_reasoning=(ctx.deps.role_selection.reasoning),
            role_specific_instructions=(ROLE_INSTRUCTIONS[self._role]),
        )

    def _register_tools(self) -> None:
        """Register plain tools on the agent after creation."""
        role = self._role

        @self.agent.tool_plain
        def retrieve_techniques(
            state: str = "",
        ) -> str:
            """Retrieve facilitation techniques for this role.

            Description:
                Returns techniques from the ADR 0002 repertoire
                filtered by role and optionally by discussion state.

            Args:
                state: Optional discussion state for filtering.

            Returns:
                Formatted string of available techniques.
            """
            ds = None
            if state:
                try:
                    ds = DiscussionState(state)
                except ValueError:
                    pass
            techniques = get_techniques(role, ds)
            if not techniques:
                return "No techniques found for this role."
            lines = []
            for t in techniques:
                examples_text = "\n  ".join(f"Example: {e}" for e in t.examples)
                lines.append(
                    f"- **{t.name}**: {t.description}\n  {examples_text}"
                )
            return "\n".join(lines)

        @self.agent.tool_plain
        def retrieve_anti_patterns() -> str:
            """Retrieve facilitation anti-patterns to avoid.

            Description:
                Returns patterns the agent should avoid during
                facilitation.

            Returns:
                Formatted string of anti-patterns.
            """
            patterns = get_anti_patterns()
            return "\n".join(f"- {p}" for p in patterns)
