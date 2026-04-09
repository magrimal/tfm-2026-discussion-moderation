"""Application settings loaded from environment variables.

Single configuration class following FastAPI/pydantic-settings
conventions. Override values via environment variables prefixed
with FACILITATION_ or via a .env file.
"""

from functools import lru_cache

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Facilitation pipeline configuration.

    All settings are loaded from environment variables with the
    FACILITATION_ prefix. For example, FACILITATION_LLM_MODEL sets
    the llm_model field. A .env file is read automatically.

    Attributes:
        llm_model: Pydantic-ai model identifier.
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

    llm_model: str = "anthropic:claude-sonnet-4-20250514"
    discussion_context: str = "asynchronous academic discussion threads"
    stalled_threshold_hours: int = 48
    pipeline_timeout_seconds: float = 30.0
    log_level: str = "INFO"
    max_orchestrator_retries: int = 1
    classifier_eval_enabled: bool = False
    response_eval_enabled: bool = True
    lms_backend: str = "openedx"
    lms_url: str = "http://localhost:18000"
    lms_jwt_authentication_token: str = Field(
        default="",
        validation_alias=AliasChoices(
            "LMS_JWT_AUTHENTICATION_TOKEN",
            "FACILITATION_LMS_JWT_AUTHENTICATION_TOKEN",
        ),
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the application settings, cached after first load.

    For tests, call get_settings.cache_clear() after modifying
    environment variables.

    Returns:
        The application Settings instance.
    """
    return Settings()
