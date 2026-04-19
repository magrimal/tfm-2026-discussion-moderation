"""Application settings."""

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    """Configuration loaded from environment variables."""

    model_config = {
        "env_prefix": "FACILITATION_",
        "env_file": ".env",
        "extra": "ignore",
    }

    llm_model: str = "anthropic:claude-sonnet-4-20250514"
    stalled_threshold_hours: int = 48
