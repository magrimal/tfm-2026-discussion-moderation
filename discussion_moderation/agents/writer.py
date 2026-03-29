"""Writer agent: optional tone and audience adaptation.

Adapts the role agent's response to the course context and
audience. Toggled via settings.writer_enabled.
"""

from pydantic_ai import Agent, RunContext

from discussion_moderation.agents.base import AgentMixin
from discussion_moderation.common.models import (
    WriterDeps,
    WriterOutput,
)
from discussion_moderation.common.prompts import WRITER_PROMPT


class WriterAgent(AgentMixin):
    """Writer agent using the AgentMixin pattern."""

    def __init__(self) -> None:
        self.agent: Agent[WriterDeps, WriterOutput] = Agent(
            "anthropic:claude-sonnet-4-20250514",
            output_type=WriterOutput,
        )
        self._register_system_prompt()

    async def _build_system_prompt(self, ctx: RunContext[WriterDeps]) -> str:
        """Build the writer system prompt from deps.

        Description:
            Fills the writer prompt template with course context
            for audience adaptation. Falls back to a generic
            prompt when lms_backend is None.

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


adapt_response = WriterAgent().agent
