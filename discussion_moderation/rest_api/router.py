"""HTTP routes for the facilitation service."""

import asyncio

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from discussion_moderation.api.facilitation import facilitate
from discussion_moderation.common.types import (
    CourseContext,
    DiscussionThread,
    PipelineResult,
)
from discussion_moderation.settings import get_settings

router = APIRouter()


@router.post(
    "/facilitate",
    response_model=PipelineResult,
    status_code=status.HTTP_200_OK,
)
async def facilitate_thread(
    thread: DiscussionThread,
    course_context: CourseContext | None = None,
) -> PipelineResult | JSONResponse:
    """Run the facilitation pipeline on a discussion thread.

    Description:
        HTTP endpoint for the facilitation pipeline. Applies a
        configurable timeout to prevent long-running requests.

    Args:
        thread: The discussion thread to analyze.
        course_context: Optional course context for adaptation.

    Returns:
        PipelineResult on success, 504 on timeout.
    """
    settings = get_settings()
    try:
        return await asyncio.wait_for(
            facilitate(thread, course_context),
            timeout=settings.pipeline_timeout_seconds,
        )
    except TimeoutError:
        return JSONResponse(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            content={"detail": "Pipeline timed out."},
        )


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
)
async def health() -> dict[str, str]:
    """Return service health status.

    Returns:
        Health status dictionary.
    """
    return {"status": "ok"}
