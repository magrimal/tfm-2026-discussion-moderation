"""FastAPI application factory."""

from fastapi import FastAPI

from discussion_moderation.rest_api.router import router


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
