"""Base mixin for agents that register a system prompt handler."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, ClassVar, TypeVar

from pydantic_ai.output import PromptedOutput

from discussion_moderation.providers import ModelProvider

if TYPE_CHECKING:
    from pydantic_ai import Agent, RunContext

_T = TypeVar("_T")

# Overrides pydantic-ai's default PromptedOutput instructions. Seen live:
# after a role agent's tool calls (retrieve_techniques, get_thread_history),
# some models drift into Markdown prose for the final answer instead of
# raw JSON, which fails parsing outright (not schema-echo - the model
# just stops emitting JSON at all). {schema} is substituted by pydantic-ai.
_PROMPTED_OUTPUT_TEMPLATE = (
    "Respond with a single JSON object matching this schema. "
    "Your entire response must be that JSON object and nothing else: "
    "no Markdown formatting, no code fences, no bullet points, no "
    "explanation before or after it - even if you called tools earlier "
    "in this conversation.\n\n{schema}"
)


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
    def _effective_model_str(model: object, fallback: str) -> str:
        """Return the model identifier string for profile resolution.

        When an explicit model object is passed (e.g. TestModel), use its
        own model_name so that profile resolution reflects the actual model
        being used rather than the settings default.
        """
        if model is None:
            return fallback
        if isinstance(model, str):
            return model
        name = getattr(model, "model_name", None)
        return name if isinstance(name, str) else fallback

    @staticmethod
    def resolve_output_type(
        model_str: str,
        base_type: type[_T],
        overrides: dict[str, str] | None = None,
    ) -> type[_T] | PromptedOutput[_T]:
        """Return the output type, wrapped in PromptedOutput when needed.

        Resolution order (ADR 0031):
        1. Runtime overrides from settings
           (FACILITATION_MODEL_EXTRACTION_OVERRIDES)
        2. Per-model profile in the provider's MODEL_PROFILES dict
        3. Provider-level default profile
        4. Base default (ToolOutput)

        Args:
            model_str: Provider-prefixed model string.
            base_type: The Pydantic model class for structured output.
            overrides: Optional dict mapping model name (without provider
                prefix) to "tool" or "prompted". Takes precedence over
                the static profile. Pass settings.model_extraction_overrides.

        Returns:
            PromptedOutput(base_type) when extraction_mode is "prompted",
            base_type otherwise.
        """
        model_name = (
            model_str.split(":", 1)[-1] if ":" in model_str else model_str
        )
        if overrides and model_name in overrides:
            mode = overrides[model_name]
        else:
            mode = ModelProvider.profile_for(model_str).extraction_mode
        if mode == "prompted":
            return PromptedOutput(base_type, template=_PROMPTED_OUTPUT_TEMPLATE)
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
