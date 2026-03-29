"""Base mixin for agents that register a system prompt handler."""

from abc import ABC, abstractmethod

from pydantic_ai import Agent, RunContext


class AgentMixin(ABC):
    """Mixin that registers a system prompt handler on a pydantic_ai Agent.

    Subclasses must:
    - Set ``self.agent`` to a ``pydantic_ai.Agent`` instance before calling
      ``_register_system_prompt()``.
    - Implement ``_build_system_prompt(ctx)`` to return the prompt string.
    """

    agent: Agent

    def _register_system_prompt(self) -> None:
        """Register ``_build_system_prompt`` as the agent's system prompt."""
        self.agent.system_prompt(self._build_system_prompt)

    @abstractmethod
    def _build_system_prompt(self, ctx: RunContext) -> str:
        """Build the system prompt string for the agent.

        Args:
            ctx: Run context provided by pydantic_ai at call time.

        Returns:
            The system prompt string.
        """
