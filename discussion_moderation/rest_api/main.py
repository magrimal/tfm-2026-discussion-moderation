"""FastAPI application factory."""

import os
from pathlib import Path

import logfire
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

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
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(router)
    static_dir = Path(__file__).parent.parent.parent / "dashboard" / "dist"
    if static_dir.exists():
        application.mount(
            "/", StaticFiles(directory=static_dir, html=True), name="dashboard"
        )
    return application


app = create_app()
