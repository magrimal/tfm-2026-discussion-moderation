"""Base mixin for agents that register a system prompt handler."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, ClassVar

if TYPE_CHECKING:
    from pydantic_ai import Agent, RunContext


class AgentMixin(ABC):
    """Mixin that registers a system prompt handler on a pydantic_ai Agent.

    Each subclass defines up to four class-level prompt constants:

        PERSONALITY: who the agent is and how it reasons (static)
        CONTEXT_TEMPLATE: runtime context filled via .format() (has {vars})
        EXAMPLES: optional examples (static, omitted if empty)
        INSTRUCTIONS: what the agent must do (static or with {vars})

    Assemble them with build_prompt(), then call .format(**runtime_values)
    inside _build_system_prompt().

    Subclasses must:
    - Set self.agent before calling _register_system_prompt().
    - Implement _build_system_prompt(ctx) to return the prompt string.
      May be async if the subclass needs to fetch context at runtime.
    - Define async run(...) as the public interface.
    """

    agent: Agent[Any, Any]

    PERSONALITY: ClassVar[str] = ""
    CONTEXT_TEMPLATE: ClassVar[str] = ""
    EXAMPLES: ClassVar[str] = ""
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
            sections.append(f"# Personality\n{cls.PERSONALITY}")
        if cls.CONTEXT_TEMPLATE:
            sections.append(f"# Context\n{cls.CONTEXT_TEMPLATE}")
        if cls.EXAMPLES:
            sections.append(f"# Examples\n{cls.EXAMPLES}")
        if cls.INSTRUCTIONS:
            sections.append(f"# Instructions\n{cls.INSTRUCTIONS}")
        return "\n\n".join(sections)

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
