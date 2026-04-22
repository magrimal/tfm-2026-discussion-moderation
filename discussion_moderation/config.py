"""Application settings loaded from environment variables.

Single configuration class following FastAPI/pydantic-settings
conventions. Override values via environment variables prefixed
with FACILITATION_ or via a .env file.
"""

from functools import lru_cache

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings

from discussion_moderation.providers import ModelProvider


class Settings(BaseSettings):
    """Facilitation pipeline configuration.

    All settings are loaded from environment variables with the
    FACILITATION_ prefix. For example, FACILITATION_LLM_MODEL sets
    the llm_model field. A .env file is read automatically.

    Attributes:
        llm_api_key: API key forwarded to the active LLM provider.
            Read from LLM_API_KEY (no prefix) or FACILITATION_LLM_API_KEY.
            Used by build_model() to authenticate against Anthropic or
            OpenRouter without requiring provider-specific env vars.
        llm_model: Default pydantic-ai model identifier, used for any
            agent that does not have a specific override set.
            Supports provider-prefixed strings: "anthropic:model-name"
            or "openrouter:provider/model-name".
        classification_model: Model override for the classification agent.
            Falls back to llm_model if not set.
        intervention_model: Model override for the intervention agent.
            Falls back to llm_model if not set.
        orchestrator_model: Model override for the orchestrator agent.
            Falls back to llm_model if not set.
        role_model: Model override for all role agents (organizational,
            intellectual, social, affective, moderator).
            Falls back to llm_model if not set.
        stalled_threshold_hours: Hours without posts before a
            thread is considered stalled.
        pipeline_timeout_seconds: Max seconds for the full
            pipeline before timing out.
        log_level: Python logging level.
        max_orchestrator_retries: Max retry attempts when the
            response evaluator rejects a response.
        classifier_eval_enabled: Whether the classifier evaluator
            node is active.
        response_eval_enabled: Whether the response evaluator
            node is active.
        lms_backend: LMS backend identifier (e.g., "openedx").
            Set via FACILITATION_LMS_BACKEND.
        lms_url: Base URL of the LMS instance. Used by the active
            backend for API calls. Set via FACILITATION_LMS_URL.
        discussion_context: Human-readable description of the
            discussion type, injected into agent prompts. Override
            when deploying outside academic asynchronous contexts.
        lms_jwt_authentication_token: JWT token issued by the LMS for
            authenticating API calls. Read from LMS_JWT_AUTHENTICATION_TOKEN
            (no prefix) or FACILITATION_LMS_JWT_AUTHENTICATION_TOKEN.
    """

    model_config = {
        "env_prefix": "FACILITATION_",
        "env_file": ".env",
        "extra": "ignore",
    }

    llm_api_key: str = Field(
        default="",
        validation_alias=AliasChoices(
            "LLM_API_KEY",
            "FACILITATION_LLM_API_KEY",
        ),
    )
    llm_model: str = "anthropic:claude-sonnet-4-20250514"
    classification_model: str | None = None
    intervention_model: str | None = None
    orchestrator_model: str | None = None
    role_model: str | None = None
    discussion_context: str = "asynchronous academic discussion threads"
    stalled_threshold_hours: int = 48
    pipeline_timeout_seconds: float = 30.0
    log_level: str = "INFO"
    max_orchestrator_retries: int = 1
    classifier_eval_enabled: bool = False
    response_eval_enabled: bool = True
    lms_backend: str = "openedx"
    history_backend: str = "memory"
    lms_url: str = "http://localhost:18000"
    lms_jwt_authentication_token: str = Field(
        default="",
        validation_alias=AliasChoices(
            "LMS_JWT_AUTHENTICATION_TOKEN",
            "FACILITATION_LMS_JWT_AUTHENTICATION_TOKEN",
        ),
    )

    def model_for(self, agent: str) -> str:
        """Return the model string for a named agent, falling back to llm_model.

        Args:
            agent: One of "classification", "intervention",
                "orchestrator", "role".

        Returns:
            Provider-prefixed model string,
            e.g. "anthropic:claude-sonnet-4-20250514".
        """
        return getattr(self, f"{agent}_model", None) or self.llm_model


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the application settings, cached after first load.

    For tests, call get_settings.cache_clear() after modifying
    environment variables.

    Returns:
        The application Settings instance.
    """
    return Settings()


def build_model(model_str: str, api_key: str) -> object:
    """Build a pydantic-ai model object for the given model string and key.

    Delegates to ModelProvider.for_model(), which looks up the registered
    provider for the prefix and constructs the model with the given key.

    Args:
        model_str: Provider-prefixed model string,
            e.g. "anthropic:claude-sonnet-4-20250514".
        api_key: API key forwarded to the provider.

    Returns:
        A pydantic-ai Model object, or the original string for
        unregistered prefixes.
    """
    return ModelProvider.for_model(model_str, api_key)
