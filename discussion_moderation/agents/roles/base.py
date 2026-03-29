"""Shared factory and tools for role-specific agents.

Each role agent is a pydantic-ai Agent with the same deps and
output types but different system prompts and technique access.
"""

from pydantic_ai import Agent, RunContext

from discussion_moderation.common.constants import (
    DiscussionState,
    FacilitationRole,
)
from discussion_moderation.common.formatters import format_thread
from discussion_moderation.common.models import (
    DiscussionThread,
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


def create_role_agent(
    role: FacilitationRole,
    model: str = "anthropic:claude-sonnet-4-20250514",
) -> Agent[RoleAgentDeps, FacilitationResponse]:
    """Create a pydantic-ai agent for a facilitation role.

    Description:
        Factory that builds a role-specific agent with the
        appropriate system prompt, output type, and tools.
        The system prompt is parameterized at runtime via
        RunContext.

    Args:
        role: The facilitation role this agent serves.
        model: The pydantic-ai model identifier.

    Returns:
        A configured Agent for the given role.
    """
    agent: Agent[RoleAgentDeps, FacilitationResponse] = Agent(
        model,
        output_type=FacilitationResponse,
    )

    @agent.system_prompt
    async def _build_role_prompt(
        ctx: RunContext[RoleAgentDeps],
    ) -> str:
        return ROLE_PROMPT_BASE.format(
            role_name=role.value,
            context_type=ctx.deps.context_type,
            discussion_state=(ctx.deps.classification.state.value),
            selection_reasoning=(ctx.deps.role_selection.reasoning),
            role_specific_instructions=(ROLE_INSTRUCTIONS[role]),
        )

    @agent.tool_plain
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
            examples_text = "\n  ".join(
                f"Example: {e}" for e in t.examples
            )
            lines.append(
                f"- **{t.name}**: {t.description}\n  {examples_text}"
            )
        return "\n".join(lines)

    @agent.tool_plain
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

    return agent


async def generate_response(
    role: FacilitationRole,
    thread: DiscussionThread,
    deps: RoleAgentDeps,
    model: str = "anthropic:claude-sonnet-4-20250514",
) -> FacilitationResponse:
    """Run a role-specific agent to generate a response.

    Description:
        Creates (or retrieves) the agent for the given role and
        runs it against the thread to produce a facilitation
        response.

    Args:
        role: The facilitation role to activate.
        thread: The discussion thread.
        deps: Role agent dependencies.
        model: The pydantic-ai model identifier.

    Returns:
        FacilitationResponse with text, technique, and confidence.
    """
    agent = _get_role_agent(role, model)
    prompt = format_thread(thread)
    result = await agent.run(prompt, deps=deps)
    return result.output


_role_agent_cache: dict[
    FacilitationRole,
    Agent[RoleAgentDeps, FacilitationResponse],
] = {}


def _get_role_agent(
    role: FacilitationRole,
    model: str,
) -> Agent[RoleAgentDeps, FacilitationResponse]:
    """Get or create a cached role agent.

    Args:
        role: The facilitation role.
        model: The pydantic-ai model identifier.

    Returns:
        The role agent instance.
    """
    if role not in _role_agent_cache:
        _role_agent_cache[role] = create_role_agent(role, model)
    return _role_agent_cache[role]
