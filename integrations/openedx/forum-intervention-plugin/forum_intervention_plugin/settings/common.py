"""Common settings for the Forum Intervention Plugin."""


def plugin_settings(settings):
    """Inject plugin defaults into the Django settings object."""
    settings.FACILITATION_SERVICE_URL = ""
    settings.FACILITATION_SERVICE_ENABLED = True
