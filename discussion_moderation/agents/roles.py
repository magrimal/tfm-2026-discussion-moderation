"""Pre-instantiated role agents for all facilitation roles.

Each agent is the pydantic-ai Agent object produced by RoleAgent,
ready for direct use in graph nodes. ROLE_AGENTS provides lookup
by FacilitationRole.
"""

from pydantic_ai import Agent

from discussion_moderation.agents.role_agent import RoleAgent
from discussion_moderation.common.constants import FacilitationRole
from discussion_moderation.common.formatters import format_thread
from discussion_moderation.common.models import (
    DiscussionThread,
    FacilitationResponse,
    RoleAgentDeps,
)

organizational_agent = RoleAgent(FacilitationRole.ORGANIZATIONAL).agent
intellectual_agent = RoleAgent(FacilitationRole.INTELLECTUAL).agent
social_agent = RoleAgent(FacilitationRole.SOCIAL).agent
affective_agent = RoleAgent(FacilitationRole.AFFECTIVE).agent
moderator_agent = RoleAgent(FacilitationRole.MODERATOR).agent

ROLE_AGENTS: dict[FacilitationRole, Agent] = {
    FacilitationRole.ORGANIZATIONAL: organizational_agent,
    FacilitationRole.INTELLECTUAL: intellectual_agent,
    FacilitationRole.SOCIAL: social_agent,
    FacilitationRole.AFFECTIVE: affective_agent,
    FacilitationRole.MODERATOR: moderator_agent,
}


async def generate_response(
    role: FacilitationRole,
    thread: DiscussionThread,
    deps: RoleAgentDeps,
) -> FacilitationResponse:
    """Run the role agent for the given role and return its output.

    Args:
        role: The facilitation role to activate.
        thread: The discussion thread.
        deps: Role agent dependencies.

    Returns:
        FacilitationResponse with text, technique, and confidence.
    """
    agent = ROLE_AGENTS[role]
    prompt = format_thread(thread)
    result = await agent.run(prompt, deps=deps)
    return result.output
