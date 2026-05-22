"""Forum Intervention Plugin Django application configuration."""

from django.apps import AppConfig


class ForumInterventionPluginConfig(AppConfig):
    """Django AppConfig for the Forum Intervention Plugin."""

    name = "forum_intervention_plugin"

    plugin_app = {
        "settings_config": {
            "lms.djangoapp": {
                "common": {"relative_path": "settings.common"},
            }
        },
    }

    def ready(self):
        """Import signal handlers when the app is ready."""
        from . import handlers  # noqa: F401
