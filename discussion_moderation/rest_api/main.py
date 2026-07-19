"""FastAPI application factory."""

from __future__ import annotations

import logging
import os

import logfire
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from discussion_moderation.config import get_settings
from discussion_moderation.rest_api.auth import require_auth
from discussion_moderation.rest_api.router import (
    protected_router,
    public_router,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s [%(name)s] %(message)s",
)

if os.environ.get("LOGFIRE_TOKEN"):
    logfire.configure()
    logfire.instrument_pydantic_ai()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        Configured FastAPI application instance.
    """
    application = FastAPI(
        title="Discussion Facilitation",
        version="0.2.0",
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    settings = get_settings()
    application.include_router(public_router, prefix=settings.api_prefix)
    application.include_router(
        protected_router,
        prefix=settings.api_prefix,
        dependencies=[Depends(require_auth)],
    )
    return application


app = create_app()
