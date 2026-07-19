# discussion_moderation/rest_api/auth.py
"""HTTP Basic Auth dependency for the facilitation API."""

from __future__ import annotations

import secrets
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from discussion_moderation.config import get_settings

security = HTTPBasic(auto_error=False)


def require_auth(
    credentials: Annotated[HTTPBasicCredentials | None, Depends(security)],
) -> None:
    """Enforce HTTP Basic Auth when FACILITATION_ADMIN_PASSWORD is set.

    No-op when admin_password is empty (local dev convenience).
    Raises 401 when credentials are missing or incorrect.
    """
    settings = get_settings()
    if not settings.admin_password:
        return

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
            headers={"WWW-Authenticate": "Basic"},
        )

    correct_username = secrets.compare_digest(
        credentials.username.encode(),
        settings.admin_username.encode(),
    )
    correct_password = secrets.compare_digest(
        credentials.password.encode(),
        settings.admin_password.encode(),
    )
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect credentials.",
            headers={"WWW-Authenticate": "Basic"},
        )
