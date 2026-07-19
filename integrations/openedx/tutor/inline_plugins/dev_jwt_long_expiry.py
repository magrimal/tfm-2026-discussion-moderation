"""
Tutor plugin: extend JWT token lifetime.

Open edX has several, mostly-unrelated expiry settings:
- JWT_EXPIRATION / JWT_EXPIRATION_DELTA: fallback used by
  oauth_dispatch.jwt._compute_time_fields() only when no explicit
  expires_in is passed in, and by rest_framework_jwt session tokens.
- OAUTH2_PROVIDER["ACCESS_TOKEN_EXPIRE_SECONDS"]: django-oauth-toolkit's
  own setting for opaque (non-JWT) Bearer tokens.
- JWT_ACCESS_TOKEN_EXPIRE_SECONDS: a separate, top-level setting read by
  oauth_dispatch.jwt._get_jwt_access_token_expire_seconds(), which is
  what actually controls the "expires_in" of a JWT issued via
  POST /oauth2/access_token with token_type=jwt (e.g. the
  client_credentials grant used by LMS_JWT_AUTHENTICATION_TOKEN).
  Defaults to 60*60 (1 hour) if unset - deliberately separate from the
  other two because JWTs are non-revocable. Confirmed by reading
  oauth_dispatch/jwt.py directly; the other two settings alone do NOT
  affect this flow despite looking like they should.

The default (1 hour) makes manual testing and manual redeploys (which
need a fresh LMS_JWT_AUTHENTICATION_TOKEN each time) impractical. This
patch sets all of the above to one day for consistency, even though
only JWT_ACCESS_TOKEN_EXPIRE_SECONDS is load-bearing for the
client_credentials + token_type=jwt flow this project actually uses.

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
# The setting that actually controls client_credentials + token_type=jwt.
JWT_ACCESS_TOKEN_EXPIRE_SECONDS = 86400
""",
    )
)
