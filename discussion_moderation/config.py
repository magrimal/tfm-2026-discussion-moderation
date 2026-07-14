"""Application settings loaded from environment variables.

Single configuration class following FastAPI/pydantic-settings
conventions. Override values via environment variables prefixed
with FACILITATION_ or via a .env file.
"""

import os
from functools import lru_cache
from pathlib import Path

from pydantic import AliasChoices, Field
from pydantic_ai.models import Model
from pydantic_settings import BaseSettings

from discussion_moderation.providers import ModelProvider

_env_file = os.environ.get("APP_ENV_FILE", ".env.local")


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
        lms_url: Base URL of the LMS instance. The forum Django app
            is installed in the LMS, so this URL is also used for all
            /api/v2/ forum calls. Set via FACILITATION_LMS_URL.
        bot_user_id: Forum user ID used when posting facilitation
            comments. If empty, the pipeline runs but does not write
            back to the forum (dry-run mode).
            Set via FACILITATION_BOT_USER_ID.
        discussion_context: Human-readable description of the
            discussion type, injected into agent prompts. Override
            when deploying outside academic asynchronous contexts.
        lms_jwt_authentication_token: JWT token issued by the LMS for
            authenticating API calls. Read from LMS_JWT_AUTHENTICATION_TOKEN
            (no prefix) or FACILITATION_LMS_JWT_AUTHENTICATION_TOKEN.
        history_backend: ThreadHistoryStore backend key. "memory" (default)
            resets on restart; "sqlite" persists to history_db_path.
        history_db_path: Path to the SQLite file used by SQLiteThreadStore.
            Only relevant when history_backend is "sqlite".
            Defaults to history.db in the current working directory.
        run_results_backend: Backend key for run result reads.
            Supported values: "filesystem", "s3".
        s3_bucket: S3 bucket name for the S3 run result store.
            Required when run_results_backend is "s3".
            Set via FACILITATION_S3_BUCKET.
        s3_prefix: Key prefix inside the S3 bucket. Defaults to "runs".
            Set via FACILITATION_S3_PREFIX.
        env_name: Deployment environment label used as a path segment
            in S3 keys (e.g. "local", "ec2", "idril").
            Set via FACILITATION_ENV.
        admin_username: Username for HTTP Basic Auth. Defaults to "admin".
        admin_password: Password for HTTP Basic Auth. If empty, auth is
            disabled (all requests pass through without challenge).
            Set in production to protect the dashboard and API.
    """

    model_config = {
        "env_prefix": "FACILITATION_",
        "env_file": (".env", _env_file),
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
    history_db_path: Path = Path("history.db")
    run_results_backend: str = "filesystem"
    s3_bucket: str = ""
    s3_prefix: str = "runs"
    env_name: str = Field(
        default="local",
        validation_alias="FACILITATION_ENV",
    )
    api_prefix: str = "/api"
    lms_url: str = "http://localhost:18000"
    bot_user_id: str = ""
    logfire_project_url: str = ""
    admin_username: str = "admin"
    admin_password: str = ""
    model_extraction_overrides: dict[str, str] = Field(
        default_factory=dict,
        description=(
            "Per-model extraction mode overrides. Maps model name "
            "(without provider prefix) to 'tool' or 'prompted'. "
            "Takes precedence over the static ModelProfile registry. "
            "Set as JSON: "
            'FACILITATION_MODEL_EXTRACTION_OVERRIDES=\'{"phi4": "tool"}\''
        ),
    )
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


def build_model(model_str: str, api_key: str) -> Model | str:
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
