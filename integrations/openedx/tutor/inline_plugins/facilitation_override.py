from tutor import hooks

hooks.Filters.ENV_PATCHES.add_item((
    "openedx-common-settings",
    'FACILITATION_SERVICE_URL = "https://idril.fdi.ucm.es/2526-moderacion/api"',
))
