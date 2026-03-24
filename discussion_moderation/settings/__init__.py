"""Settings module with cached factory."""

from functools import lru_cache

from discussion_moderation.settings.config import Settings


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the application settings, cached after first load.

    Description:
        Creates a singleton Settings instance. For tests, call
        get_settings.cache_clear() after modifying environment
        variables.

    Returns:
        The application Settings instance.
    """
    return Settings()
