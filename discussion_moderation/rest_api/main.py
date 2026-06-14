"""FastAPI application factory."""

import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator

import logfire
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from discussion_moderation.config import get_settings
from discussion_moderation.evals.artifacts import mark_interrupted_runs
from discussion_moderation.rest_api.router import router

_DASHBOARD_DIR = Path(__file__).parent.parent.parent / "dashboard" / "dist"

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s [%(name)s] %(message)s",
)

if os.environ.get("LOGFIRE_TOKEN"):
    logfire.configure()
    logfire.instrument_pydantic_ai()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Mark interrupted runs on startup."""
    mark_interrupted_runs()
    yield


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        Configured FastAPI application instance.
    """
    application = FastAPI(
        title="Discussion Facilitation",
        version="0.2.0",
        lifespan=lifespan,
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(router, prefix=get_settings().api_prefix)

    if _DASHBOARD_DIR.exists():
        application.mount(
            "/assets",
            StaticFiles(directory=str(_DASHBOARD_DIR / "assets")),
            name="assets",
        )

        @application.get("/{full_path:path}", include_in_schema=False)
        async def serve_spa(full_path: str) -> FileResponse:
            """Serve the SPA index for all non-API routes."""
            return FileResponse(str(_DASHBOARD_DIR / "index.html"))

    return application


app = create_app()
