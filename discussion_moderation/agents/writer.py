"""Writer agent: optional tone and audience adaptation.

Adapts the role agent's response to the course context and
audience. Toggled via settings.writer_enabled.
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING

from pydantic_ai import Agent, RunContext

from discussion_moderation.agents.base import AgentMixin
from discussion_moderation.models import (
    DiscussionThread,
    FacilitationResponse,
    WriterOutput,
)

if TYPE_CHECKING:
    from discussion_moderation.tools.base import LMSBackend


@dataclass
class WriterDeps:
    """Dependencies for the writer agent.

    Attributes:
        response: The role agent's facilitation response.
        thread: The discussion thread.
        lms_backend: Optional LMS backend for fetching course
            context on demand.
    """

    response: FacilitationResponse
    thread: DiscussionThread
    lms_backend: "LMSBackend | None" = None


class WriterAgent(AgentMixin):
    """Writer agent using the AgentMixin pattern."""

    PROMPT = """\
# Personality
You are a writing adaptation agent for academic discussions.

# Context
Course: {display_name}
Module topic: {module_topic}
Audience level: {audience_level}
Language: {language}

# Examples
No embedded examples. Adapt based on audience level and language.

# Instructions
Adapt the {role_name} facilitation response to match the \
audience without changing the pedagogical intent or technique.

Focus on:
- Appropriate formality for the audience level
- Vocabulary accessible to {audience_level} students
- Natural language for {language}
- Consistent tone with the course context

Do not add new content or remove key points.
"""

    def __init__(self) -> None:
        self.agent: Agent[WriterDeps, WriterOutput] = Agent(
            "anthropic:claude-sonnet-4-20250514",
            output_type=WriterOutput,
        )
        self._register_system_prompt()

    async def _build_system_prompt(self, ctx: RunContext[WriterDeps]) -> str:
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
        return self.PROMPT.format(
            display_name=cc.display_name,
            module_topic=cc.module_topic,
            audience_level=cc.audience_level,
            language=cc.language,
            role_name="facilitation",
        )

    async def run(self, deps: WriterDeps) -> WriterOutput:
        """Adapt a facilitation response for the course audience.

        Args:
            deps: Writer dependencies including the response and thread.

        Returns:
            WriterOutput with the adapted final text.
        """
        response = deps.response
        prompt = (
            f"Original response:\n{response.response_text}\n\n"
            f"Technique used: {response.technique_used}\n"
            f"Action category: {response.action_category.value}"
        )
        result = await self.agent.run(prompt, deps=deps)
        return result.output


writer = WriterAgent()
