"""LLM provider registry.

ModelProvider is the base class for all LLM provider integrations.
Subclasses register themselves by declaring a prefix= keyword argument.
The pipeline resolves the right provider at runtime from the model
string prefix (e.g. "anthropic:claude-sonnet-4" -> AnthropicModelProvider).

Adding a new provider requires one new subclass — no changes elsewhere.
Adding a per-model profile requires one entry in the provider's
MODEL_PROFILES dict — no other code changes.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import ClassVar, Literal

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


@dataclass
class ModelProfile:
    """Per-model capability configuration (ADR 0031).

    Attributes:
        extraction_mode: How pydantic-ai extracts structured output.
            "tool" uses the tool-call/result cycle (default).
            "prompted" uses a text prompt and parses the response —
            required for providers whose OpenAI-compat layer rejects
            null content in assistant messages with tool_calls.
        has_functional_tools: False for models that explicitly reject
            tool calling (e.g. phi4, gemma2:9b). Informational — the
            eval runner can use this to filter out models that will
            always fail at the role node.
    """

    extraction_mode: Literal["tool", "prompted"] = "tool"
    has_functional_tools: bool = True


class ModelProvider:
    """Base class for LLM provider integrations.

    Subclasses register themselves automatically:

        class MyProvider(ModelProvider, prefix="myprovider"):
            def build(self, model_name: str, api_key: str): ...

    Use ModelProvider.for_model(model_str, api_key) to resolve and
    instantiate the right provider at runtime.
    Use ModelProvider.profile_for(model_str) to get the capability
    profile for a specific model.
    """

    _registry: ClassVar[dict[str, type[ModelProvider]]] = {}
    _default_profile: ClassVar[ModelProfile] = ModelProfile()
    MODEL_PROFILES: ClassVar[dict[str, ModelProfile]] = {}

    def __init_subclass__(cls, prefix: str = "", **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        if prefix:
            ModelProvider._registry[prefix] = cls

    @classmethod
    def profile_for(cls, model_str: str) -> ModelProfile:
        """Return the capability profile for a model string.

        Resolution order:
        1. Model-specific entry in the provider's MODEL_PROFILES dict
        2. Provider-level default (_default_profile)
        3. Base default (ToolOutput, has_functional_tools=True)

        Args:
            model_str: Provider-prefixed model string,
                e.g. "ollama:phi4".

        Returns:
            ModelProfile for the given model.
        """
        if ":" not in model_str:
            return ModelProfile()
        prefix, model_name = model_str.split(":", 1)
        provider_cls = cls._registry.get(prefix)
        if provider_cls is None:
            return ModelProfile()
        profile = provider_cls.MODEL_PROFILES.get(model_name)
        if profile is not None:
            return profile
        return provider_cls._default_profile

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

    _default_profile: ClassVar[ModelProfile] = ModelProfile(
        extraction_mode="tool"
    )

    def build(self, model_name: str, api_key: str) -> AnthropicModel:
        return AnthropicModel(
            model_name,
            provider=_AnthropicProvider(api_key=api_key),
        )


class OllamaModelProvider(ModelProvider, prefix="ollama"):
    """Ollama local provider.

    Ollama exposes an OpenAI-compatible API at http://localhost:11434/v1.
    No API key is required; the api_key argument is ignored.

    Per-model profiles control extraction mode and tool capability (ADR
    0030). Unknown models fall back to the provider default (ToolOutput).
    Models without functional tool support (phi4, gemma2:9b) are flagged
    via has_functional_tools=False and use PromptedOutput for extraction.

    Usage in .env:
        FACILITATION_LLM_MODEL=ollama:qwen2.5:14b
        FACILITATION_LLM_MODEL=ollama:llama3.1:8b

    Requires Ollama to be running locally. Pull models with:
        ollama pull qwen2.5:14b
    """

    _default_profile: ClassVar[ModelProfile] = ModelProfile(
        extraction_mode="tool"
    )
    MODEL_PROFILES: ClassVar[dict[str, ModelProfile]] = {
        # Tier 1: full capability — tool-call extraction, functional tools
        "qwen2.5:14b": ModelProfile(extraction_mode="prompted"),
        "qwen3.5:9b": ModelProfile(extraction_mode="prompted"),
        "qwen3.5:27b": ModelProfile(extraction_mode="prompted"),
        "llama3.1:8b": ModelProfile(extraction_mode="tool"),
        "deepseek-r1:14b": ModelProfile(extraction_mode="tool"),
        # command-r is purpose-built by Cohere for reliable tool/function
        # calling - trusting that design intent over the family default.
        "command-r:35b": ModelProfile(extraction_mode="tool"),
        # Tier 2: partial-schema — PromptedOutput reduces schema-echo
        "mistral-nemo:12b": ModelProfile(extraction_mode="prompted"),
        "ministral-3:8b": ModelProfile(extraction_mode="prompted"),
        "ministral-3:14b": ModelProfile(extraction_mode="prompted"),
        # Untested - default to "prompted" per ADR 0012's general
        # guidance for new Ollama models (avoids the null-content 400
        # bug more reliably than tool mode). gemma2:9b (older, same
        # family) needed has_functional_tools=False; leaving that
        # unset here until a live run shows whether gemma3 fixed it.
        "gemma3:12b": ModelProfile(extraction_mode="prompted"),
        # Tier 3: no functional tools — PromptedOutput for extraction;
        # role node will always fail (has_functional_tools=False)
        "phi4": ModelProfile(
            extraction_mode="prompted", has_functional_tools=False
        ),
        "gemma2:9b": ModelProfile(
            extraction_mode="prompted", has_functional_tools=False
        ),
    }

    def build(self, model_name: str, api_key: str) -> OpenAIChatModel:
        """Build a model pointed at the Ollama server.

        Reads OLLAMA_HOST from the environment (default: http://localhost:11434).
        """
        host = os.environ.get("OLLAMA_HOST", "http://localhost:11434").rstrip(
            "/"
        )
        base_url = f"{host}/v1"
        return OpenAIChatModel(
            model_name,
            provider=_OpenAIProvider(base_url=base_url, api_key="ollama"),
        )


class OpenRouterModelProvider(ModelProvider, prefix="openrouter"):
    """OpenRouter provider.

    OpenRouter exposes an OpenAI-compatible API, so pydantic-ai models
    it as OpenAIModel with an OpenRouterProvider. The class name reflects
    the wire protocol, not the routing service.
    """

    _default_profile: ClassVar[ModelProfile] = ModelProfile(
        extraction_mode="tool"
    )

    def build(self, model_name: str, api_key: str) -> OpenAIChatModel:
        return OpenAIChatModel(
            model_name,
            provider=_OpenRouterProvider(api_key=api_key),
        )
