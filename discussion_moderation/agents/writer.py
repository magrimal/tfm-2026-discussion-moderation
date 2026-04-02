"""Writer agent: optional tone and audience adaptation.

Adapts the role agent's response to the course context and
audience. Toggled via settings.writer_enabled.
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING

from pydantic_ai import Agent, RunContext

from discussion_moderation.agents.base import AgentMixin
from discussion_moderation.config import get_settings
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
    """Writer agent using the AgentMixin pattern.

    Note: _build_system_prompt is async here because it may
    fetch course context from an LMS backend at runtime.
    pydantic-ai supports async system prompt functions.
    """

    PERSONALITY = (
        "You are a writing adaptation agent for academic discussions. "
        "You receive a pedagogically sound facilitation response and "
        "adapt its surface form (vocabulary, register, formality, "
        "language) without altering the pedagogical intent, the "
        "technique applied, or the key points made.\n\n"
        "You do not add content, remove arguments, or change what "
        "the facilitator is doing. You change only how it is said."
    )

    CONTEXT_TEMPLATE = "{course_context_block}"

    INSTRUCTIONS = (
        "Adapt the facilitation response provided for the course "
        "context above.\n\n"
        "Focus on:\n"
        "- Appropriate formality for the audience level\n"
        "- Vocabulary accessible to the stated audience\n"
        "- Natural expression in the course language\n"
        "- Tone consistent with the course context\n\n"
        "Do not add new content or remove key points. "
        "The technique and pedagogical intent must be preserved exactly."
    )

    _FALLBACK_CONTEXT = (
        "No course context available. "
        "Adapt for a general academic audience."
    )

    def __init__(self, model: str = "") -> None:
        self.agent: Agent[WriterDeps, WriterOutput] = Agent(
            model or get_settings().llm_model,
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
            course_context_block = self._FALLBACK_CONTEXT
        else:
            course_context_block = (
                f"Course: {cc.display_name}\n"
                f"Module topic: {cc.module_topic}\n"
                f"Audience level: {cc.audience_level}\n"
                f"Language: {cc.language}"
            )
        return self.build_prompt().format(
            course_context_block=course_context_block,
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
