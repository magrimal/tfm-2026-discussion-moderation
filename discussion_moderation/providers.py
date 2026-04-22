"""LLM provider registry.

ModelProvider is the base class for all LLM provider integrations.
Subclasses register themselves by declaring a prefix= keyword argument.
The pipeline resolves the right provider at runtime from the model
string prefix (e.g. "anthropic:claude-sonnet-4" -> AnthropicModelProvider).

Adding a new provider requires one new subclass — no changes elsewhere.
"""

from __future__ import annotations

from typing import ClassVar

from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.anthropic import (
    AnthropicProvider as _AnthropicProvider,
)
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

    def __init_subclass__(cls, prefix: str = "", **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        if prefix:
            ModelProvider._registry[prefix] = cls

    @classmethod
    def for_model(cls, model_str: str, api_key: str) -> object:
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

    def build(self, model_name: str, api_key: str) -> object:
        raise NotImplementedError


class AnthropicModelProvider(ModelProvider, prefix="anthropic"):
    """Anthropic provider. Wraps pydantic-ai AnthropicModel."""

    def build(self, model_name: str, api_key: str) -> AnthropicModel:
        return AnthropicModel(
            model_name,
            provider=_AnthropicProvider(api_key=api_key),
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
