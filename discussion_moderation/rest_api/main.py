"""FastAPI application factory."""

import os

import logfire
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from discussion_moderation.config import settings
from discussion_moderation.rest_api.router import router

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
    application.include_router(router, prefix=settings.api_prefix)
    return application


app = create_app()
