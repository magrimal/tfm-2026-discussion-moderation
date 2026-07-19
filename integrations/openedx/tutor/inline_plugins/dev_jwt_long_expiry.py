"""
Tutor plugin: extend JWT token lifetime.

Open edX has two JWT expiry settings that need to match:
- JWT_EXPIRATION: used by oauth_dispatch (seconds, int)
- JWT_EXPIRATION_DELTA: used by rest_framework_jwt (timedelta)

The default is 30 s / 5 min respectively, which makes manual testing
and manual redeploys (which need a fresh LMS_JWT_AUTHENTICATION_TOKEN
each time) impractical. This patch sets both to one day.

Used both in local development and on the EC2 LMS instance (see ADR
0040). The token issued to the "facilitation-service" client carries
administrator/superuser scope, so this is a deliberate tradeoff: one
day bounds the exposure window of a leaked token while still being
long enough that idril/EC2 deploys don't need a fresh token every run.
"""

from tutor import hooks

hooks.Filters.ENV_PATCHES.add_item(
    (
        "openedx-common-settings",
        """
# Extended JWT token lifetime (1 day). See ADR 0040.
import datetime as _dt
JWT_AUTH.update({
    "JWT_EXPIRATION": 86400,
    "JWT_EXPIRATION_DELTA": _dt.timedelta(seconds=86400),
})
if "OAUTH2_PROVIDER" not in vars():
    OAUTH2_PROVIDER = {}
OAUTH2_PROVIDER["ACCESS_TOKEN_EXPIRE_SECONDS"] = 86400
""",
    )
)
