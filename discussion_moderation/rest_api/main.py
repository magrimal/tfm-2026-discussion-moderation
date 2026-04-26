"""FastAPI application factory."""

import os

import logfire
from fastapi import FastAPI

from discussion_moderation.rest_api.router import router

if os.environ.get("LOGFIRE_TOKEN"):
    logfire.configure()
    logfire.instrument_pydantic_ai()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Description:
        Application factory following FastAPI conventions.
        Includes the facilitation router.

    Returns:
        Configured FastAPI application instance.
    """
    application = FastAPI(
        title="Discussion Facilitation",
        version="0.2.0",
    )
    application.include_router(router)
    return application


app = create_app()
