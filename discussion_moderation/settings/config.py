"""Application settings loaded from environment variables.

Single configuration class following FastAPI/pydantic-settings
conventions. Override values via environment variables prefixed
with FACILITATION_ or via a .env file.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Facilitation pipeline configuration.

    Description:
        All settings are loaded from environment variables with
        the FACILITATION_ prefix. For example, FACILITATION_LLM_MODEL
        sets the llm_model field. A .env file is read automatically.

    Attributes:
        llm_model: Pydantic-ai model identifier.
        stalled_threshold_hours: Hours without posts before a
            thread is considered stalled.
        pipeline_timeout_seconds: Max seconds for the full
            pipeline before timing out.
        log_level: Python logging level.
        max_orchestrator_retries: Max retry attempts when the
            response evaluator rejects a response.
        writer_enabled: Whether the writer agent is active.
        classifier_eval_enabled: Whether the classifier evaluator
            node is active.
        response_eval_enabled: Whether the response evaluator
            node is active.
        lms_backend: LMS backend identifier (e.g., "openedx").
        context_type: Description of the discussion context used
            in agent prompts (e.g., "asynchronous academic
            discussion threads").
    """

    model_config = {
        "env_prefix": "FACILITATION_",
        "env_file": ".env",
        "extra": "ignore",
    }

    llm_model: str = "anthropic:claude-sonnet-4-20250514"
    context_type: str = "asynchronous academic discussion threads"
    stalled_threshold_hours: int = 48
    pipeline_timeout_seconds: float = 30.0
    log_level: str = "INFO"
    max_orchestrator_retries: int = 1
    writer_enabled: bool = False
    classifier_eval_enabled: bool = False
    response_eval_enabled: bool = True
    lms_backend: str = "openedx"
