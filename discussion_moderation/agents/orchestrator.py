"""Orchestrator agent: Phase 2 role selection.

Selects which facilitation role should handle the intervention
based on the classification result (ADR 0004). Does NOT select
the action or technique — that is the role agent's responsibility.
"""

from pydantic_ai import Agent, RunContext

from discussion_moderation.common.prompts import (
    ORCHESTRATOR_PROMPT,
    format_role_descriptions,
    format_thread,
)
from discussion_moderation.common.types import (
    DiscussionThread,
    OrchestratorDeps,
    RoleSelection,
)

orchestrator_agent: Agent[OrchestratorDeps, RoleSelection] = Agent(
    "anthropic:claude-sonnet-4-20250514",
    output_type=RoleSelection,
)


@orchestrator_agent.system_prompt
async def _build_system_prompt(
    ctx: RunContext[OrchestratorDeps],
) -> str:
    """Build the orchestrator system prompt from deps.

    Description:
        Fills the orchestrator prompt template with the
        classification result and role descriptions.

    Args:
        ctx: Run context with orchestrator dependencies.

    Returns:
        The parameterized system prompt string.
    """
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


async def select_role(
    thread: DiscussionThread,
    deps: OrchestratorDeps,
) -> RoleSelection:
    """Select a facilitation role for the intervention.

    Description:
        Runs the orchestrator agent to choose which facilitation
        role is best suited for the current discussion state.

    Args:
        thread: The discussion thread being analyzed.
        deps: Orchestrator dependencies (classification, thread).

    Returns:
        RoleSelection with the chosen role and reasoning.
    """
    prompt = format_thread(thread)
    result = await orchestrator_agent.run(prompt, deps=deps)
    return result.output
