"""
Tutor plugin: extend JWT token lifetime for local development.

Open edX has two JWT expiry settings that need to match:
- JWT_EXPIRATION: used by oauth_dispatch (seconds, int)
- JWT_EXPIRATION_DELTA: used by rest_framework_jwt (timedelta)

The default is 30 s / 5 min respectively, which makes manual testing
impractical. This patch sets both to one year.

LOCAL DEVELOPMENT ONLY. Do not enable in production.
"""
from tutor import hooks

hooks.Filters.ENV_PATCHES.add_item(
    (
        "openedx-common-settings",
        """
# Extended JWT token lifetime for local development (1 year).
# Do not use in production.
import datetime as _dt
JWT_AUTH.update({
    "JWT_EXPIRATION": 31536000,
    "JWT_EXPIRATION_DELTA": _dt.timedelta(seconds=31536000),
})
OAUTH2_PROVIDER["ACCESS_TOKEN_EXPIRE_SECONDS"] = 31536000
""",
    )
)
