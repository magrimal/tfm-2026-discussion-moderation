"""LLM provider registry.

ModelProvider is the base class for all LLM provider integrations.
Subclasses register themselves by declaring a prefix= keyword argument.
The pipeline resolves the right provider at runtime from the model
string prefix (e.g. "anthropic:claude-sonnet-4" -> AnthropicModelProvider).

Adding a new provider requires one new subclass — no changes elsewhere.
"""

from __future__ import annotations

from typing import ClassVar

from pydantic_ai.models import Model
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.anthropic import (
    AnthropicProvider as _AnthropicProvider,
)
from pydantic_ai.providers.openai import OpenAIProvider as _OpenAIProvider
from pydantic_ai.providers.openrouter import (
    OpenRouterProvider as _OpenRouterProvider,
)


class ModelProvider:
    """Base class for LLM provider integrations.

    Subclasses register themselves automatically:

        class MyProvider(ModelProvider, prefix="myprovider"):
            def build(self, model_name: str, api_key: str): ...

    Use ModelProvider.for_model(model_str, api_key) to resolve and
    instantiate the right provider at runtime.
    """

    _registry: ClassVar[dict[str, type[ModelProvider]]] = {}
    uses_prompted_output: ClassVar[bool] = False

    def __init_subclass__(cls, prefix: str = "", **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        if prefix:
            ModelProvider._registry[prefix] = cls

    @classmethod
    def uses_prompted_output_for(cls, model_str: str) -> bool:
        """Return True if this model string requires PromptedOutput extraction.

        Ollama's OpenAI-compat layer rejects null content in assistant
        messages with tool_calls, causing 400 errors on pydantic-ai retries.
        PromptedOutput avoids the tool-call/result cycle entirely.

        Args:
            model_str: Provider-prefixed model string.

        Returns:
            True if the provider needs PromptedOutput, False otherwise.
        """
        if ":" not in model_str:
            return False
        prefix = model_str.split(":", 1)[0]
        provider_cls = cls._registry.get(prefix)
        return bool(provider_cls and provider_cls.uses_prompted_output)

    @classmethod
    def for_model(cls, model_str: str, api_key: str) -> Model | str:
        """Build a pydantic-ai model object from a provider-prefixed string.

        Splits the prefix, looks up the registered provider, and delegates
        to its build() method. Falls back to passing the string directly
        for unknown prefixes, letting pydantic-ai resolve them via env vars.

        Args:
            model_str: Provider-prefixed model string, e.g.
                "anthropic:claude-sonnet-4-20250514".
            api_key: API key forwarded to the provider.

        Returns:
            A pydantic-ai Model object, or the original string for
            unregistered prefixes.
        """
        if ":" not in model_str:
            return model_str
        prefix, model_name = model_str.split(":", 1)
        provider_cls = cls._registry.get(prefix)
        if provider_cls is None:
            return model_str
        return provider_cls().build(model_name, api_key)

    def build(self, model_name: str, api_key: str) -> Model:
        raise NotImplementedError


class AnthropicModelProvider(ModelProvider, prefix="anthropic"):
    """Anthropic provider. Wraps pydantic-ai AnthropicModel."""

    def build(self, model_name: str, api_key: str) -> AnthropicModel:
        return AnthropicModel(
            model_name,
            provider=_AnthropicProvider(api_key=api_key),
        )


class OllamaModelProvider(ModelProvider, prefix="ollama"):
    """Ollama local provider.

    Ollama exposes an OpenAI-compatible API at http://localhost:11434/v1.
    No API key is required; the api_key argument is ignored.

    Uses PromptedOutput extraction for structured output: Ollama's
    OpenAI-compat layer rejects null content in assistant messages with
    tool_calls, causing 400 errors when pydantic-ai retries after a
    validation failure. PromptedOutput avoids this by not using the
    tool-call/result cycle for extraction (ADR 0012).

    Usage in .env:
        FACILITATION_LLM_MODEL=ollama:llama3.2
        FACILITATION_LLM_MODEL=ollama:mistral

    Requires Ollama to be running locally. Pull models with:
        ollama pull llama3.2
    """

    BASE_URL = "http://localhost:11434/v1"
    uses_prompted_output: ClassVar[bool] = True

    def build(self, model_name: str, api_key: str) -> OpenAIChatModel:
        """Build a model pointed at the local Ollama server."""
        return OpenAIChatModel(
            model_name,
            provider=_OpenAIProvider(base_url=self.BASE_URL, api_key="ollama"),
        )


class OpenRouterModelProvider(ModelProvider, prefix="openrouter"):
    """OpenRouter provider.

    OpenRouter exposes an OpenAI-compatible API, so pydantic-ai models
    it as OpenAIModel with an OpenRouterProvider. The class name reflects
    the wire protocol, not the routing service.
    """

    def build(self, model_name: str, api_key: str) -> OpenAIChatModel:
        return OpenAIChatModel(
            model_name,
            provider=_OpenRouterProvider(api_key=api_key),
        )
