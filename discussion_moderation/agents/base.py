"""Base mixin for agents that register a system prompt handler."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, ClassVar, TypeVar

from pydantic_ai.output import PromptedOutput

from discussion_moderation.providers import ModelProvider

if TYPE_CHECKING:
    from pydantic_ai import Agent, RunContext

_T = TypeVar("_T")


class AgentMixin(ABC):
    """Mixin that registers a system prompt handler on a pydantic_ai Agent.

    Each subclass defines up to four class-level prompt constants:

        PERSONALITY: who the agent is - minimal for internal agents,
            rich character archetype for visible-output agents (ADR 0009)
        CONSTRAINTS: what the agent must not do - responsibility boundary,
            behavioral limits, tool-calling requirements
        CONTEXT_TEMPLATE: runtime context filled via .format() (has {vars})
        INSTRUCTIONS: the task directive - what to produce and how

    Assemble them with build_prompt(), then call .format(**runtime_values)
    inside build_system_prompt().

    Subclasses must:
    - Set self.agent before calling register_system_prompt().
    - Implement build_system_prompt(ctx) to return the prompt string.
      May be async if the subclass needs to fetch context at runtime.
    - Define async run(...) as the public interface.
    """

    agent: Agent[Any, Any]

    PERSONALITY: ClassVar[str] = ""
    CONSTRAINTS: ClassVar[str] = ""
    CONTEXT_TEMPLATE: ClassVar[str] = ""
    INSTRUCTIONS: ClassVar[str] = ""

    @classmethod
    def build_prompt(cls) -> str:
        """Assemble the prompt from the four section constants.

        Sections with empty content are omitted. Headers are added
        automatically.

        Returns:
            The assembled prompt template string (before .format()).
        """
        sections = []
        if cls.PERSONALITY:
            sections.append(f"# Persona\n{cls.PERSONALITY}")
        if cls.CONSTRAINTS:
            sections.append(f"# Constraints\n{cls.CONSTRAINTS}")
        if cls.CONTEXT_TEMPLATE:
            sections.append(f"# Context\n{cls.CONTEXT_TEMPLATE}")
        if cls.INSTRUCTIONS:
            sections.append(f"# Task\n{cls.INSTRUCTIONS}")
        return "\n\n".join(sections)

    @staticmethod
    def resolve_output_type(model_str: str, base_type: type[_T]) -> type[_T] | PromptedOutput[_T]:
        """Return the output type for this model, wrapped in PromptedOutput when needed.

        Ollama's OpenAI-compat layer rejects null content in assistant messages
        with tool_calls, causing 400 errors on pydantic-ai validation retries.
        PromptedOutput avoids the tool-call/result cycle entirely (ADR 0012).

        Args:
            model_str: Provider-prefixed model string used to detect the provider.
            base_type: The Pydantic model class for structured output.

        Returns:
            PromptedOutput(base_type) for providers that need it, base_type otherwise.
        """
        if ModelProvider.uses_prompted_output_for(model_str):
            return PromptedOutput(base_type)
        return base_type

    def register_system_prompt(self) -> None:
        """Register build_system_prompt as the agent's system prompt."""
        self.agent.system_prompt(self.build_system_prompt)

    @abstractmethod
    def build_system_prompt(self, ctx: RunContext[Any]) -> str:
        """Build the final system prompt string for the agent.

        May be declared async in subclasses that need to fetch
        context at runtime (e.g. from an LMS backend).

        Args:
            ctx: Run context provided by pydantic_ai at call time.

        Returns:
            The system prompt string, or a coroutine that produces one.
        """
