"""Writer agent: optional tone and audience adaptation.

Adapts the role agent's response to the course context and
audience. Toggled via settings.writer_enabled.
"""

from pydantic_ai import Agent, RunContext

from discussion_moderation.common.models import (
    FacilitationResponse,
    WriterDeps,
    WriterOutput,
)
from discussion_moderation.common.prompts import WRITER_PROMPT

writer_agent: Agent[WriterDeps, WriterOutput] = Agent(
    "anthropic:claude-sonnet-4-20250514",
    output_type=WriterOutput,
)


@writer_agent.system_prompt
async def _build_system_prompt(
    ctx: RunContext[WriterDeps],
) -> str:
    """Build the writer system prompt from deps.

    Description:
        Fills the writer prompt template with course context
        for audience adaptation.

    Args:
        ctx: Run context with writer dependencies.

    Returns:
        The parameterized system prompt string.
    """
    cc = None
    if ctx.deps.lms_backend and ctx.deps.thread.course_id:
        cc = await ctx.deps.lms_backend.get_course_context(
            ctx.deps.thread.course_id
        )
    if not cc:
        return (
            "Adapt the facilitation response for a general "
            "academic audience. Preserve the pedagogical "
            "intent and technique used."
        )
    return WRITER_PROMPT.format(
        display_name=cc.display_name,
        module_topic=cc.module_topic,
        audience_level=cc.audience_level,
        language=cc.language,
        role_name="facilitation",
    )


async def adapt_response(
    response: FacilitationResponse,
    deps: WriterDeps,
) -> WriterOutput:
    """Adapt a facilitation response for the target audience.

    Description:
        Runs the writer agent to refine the response text for
        the course context and audience.

    Args:
        response: The role agent's facilitation response.
        deps: Writer dependencies (response, thread, context).

    Returns:
        WriterOutput with adapted text and list of adaptations.
    """
    prompt = (
        f"Original response:\n{response.response_text}\n\n"
        f"Technique used: {response.technique_used}\n"
        f"Action category: {response.action_category.value}"
    )
    result = await writer_agent.run(prompt, deps=deps)
    return result.output
