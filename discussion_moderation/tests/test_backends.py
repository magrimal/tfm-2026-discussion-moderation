"""Tests for the self-registering provider and backend classes.

Covers ModelProvider, LMSBackend, and ThreadHistoryStore registries:
registration, for_key / for_model lookup, and unknown-key fallback.
Does not make real API calls.
"""

from discussion_moderation.providers import (
    AnthropicModelProvider,
    ModelProvider,
    OpenRouterModelProvider,
)
from discussion_moderation.tools.history import (
    InMemoryThreadStore,
    SQLiteThreadStore,
    ThreadHistoryStore,
)
from discussion_moderation.tools.protocols import LMSBackend
from discussion_moderation.tools.stub import StubLMSBackend


class TestModelProviderRegistry:
    def test_anthropic_is_registered(self):
        assert ModelProvider._registry["anthropic"] is AnthropicModelProvider

    def test_openrouter_is_registered(self):
        assert ModelProvider._registry["openrouter"] is OpenRouterModelProvider

    def test_for_model_unknown_prefix_returns_string(self):
        result = ModelProvider.for_model("unknown:some-model", api_key="key")
        assert result == "unknown:some-model"

    def test_for_model_no_prefix_returns_string(self):
        result = ModelProvider.for_model("some-model", api_key="key")
        assert result == "some-model"

    def test_for_model_anthropic_returns_anthropic_model(self):
        from pydantic_ai.models.anthropic import AnthropicModel

        result = ModelProvider.for_model(
            "anthropic:claude-3-haiku-20240307", api_key="test-key"
        )
        assert isinstance(result, AnthropicModel)

    def test_for_model_openrouter_returns_openai_chat_model(self):
        from pydantic_ai.models.openai import OpenAIChatModel

        result = ModelProvider.for_model(
            "openrouter:anthropic/claude-3-haiku", api_key="test-key"
        )
        assert isinstance(result, OpenAIChatModel)

    def test_custom_provider_registers_itself(self):
        class CustomProvider(ModelProvider, prefix="custom"):
            def build(self, model_name: str, api_key: str) -> str:
                return f"custom:{model_name}"

        assert ModelProvider._registry["custom"] is CustomProvider
        result = ModelProvider.for_model("custom:my-model", api_key="key")
        assert result == "custom:my-model"

        del ModelProvider._registry["custom"]


class TestLMSBackendRegistry:
    def test_openedx_is_registered(self):
        from discussion_moderation.tools.openedx import OpenEdXBackend

        assert LMSBackend._registry["openedx"] is OpenEdXBackend

    def test_stub_is_registered(self):
        assert LMSBackend._registry["stub"] is StubLMSBackend

    def test_for_key_stub_returns_instance(self):
        backend = LMSBackend.for_key("stub")
        assert isinstance(backend, StubLMSBackend)

    def test_for_key_unknown_returns_none(self):
        result = LMSBackend.for_key("doesnotexist")
        assert result is None

    def test_for_key_returns_new_instance_each_call(self):
        a = LMSBackend.for_key("stub")
        b = LMSBackend.for_key("stub")
        assert a is not b


class TestThreadHistoryStoreRegistry:
    def test_memory_is_registered(self):
        assert ThreadHistoryStore._registry["memory"] is InMemoryThreadStore

    def test_sqlite_is_registered(self):
        assert ThreadHistoryStore._registry["sqlite"] is SQLiteThreadStore

    def test_for_key_memory_returns_instance(self):
        store = ThreadHistoryStore.for_key("memory")
        assert isinstance(store, InMemoryThreadStore)

    def test_for_key_unknown_returns_none(self):
        result = ThreadHistoryStore.for_key("doesnotexist")
        assert result is None

    def test_for_key_returns_new_instance_each_call(self):
        a = ThreadHistoryStore.for_key("memory")
        b = ThreadHistoryStore.for_key("memory")
        assert a is not b
