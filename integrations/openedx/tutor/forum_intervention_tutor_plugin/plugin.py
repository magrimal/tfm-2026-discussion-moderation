"""Tutor plugin: installs and configures the Forum Intervention Plugin."""

from tutor import hooks

# Dev environments: declare as mountable so `tutor mounts add <path>` works.
# Tutor mounts the package at /openedx/mounted/forum-intervention-plugin and
# pip-installs it in editable mode — no docker cp or image rebuild needed.
hooks.Filters.MOUNTED_DIRECTORIES.add_item(
    ("openedx", "forum-intervention-plugin")
)

hooks.Filters.ENV_PATCHES.add_item((
    "openedx-dockerfile-post-python-requirements",
    "RUN pip install"
    " 'openedx-forum-intervention-plugin"
    " @ git+https://github.com/magrimal/tfm-2026-discussion-moderation.git"
    "@main"
    "#subdirectory=integrations/openedx/forum-intervention-plugin'",
))

hooks.Filters.ENV_PATCHES.add_item((
    "openedx-common-settings",
    """
# Forum Intervention Plugin: facilitation service integration.
# host.docker.internal resolves to the host machine from inside Docker.
# On Linux, replace with the actual host IP if host.docker.internal is unavailable.
FACILITATION_SERVICE_URL = "http://host.docker.internal:8080"
FACILITATION_SERVICE_ENABLED = True
""",
))
