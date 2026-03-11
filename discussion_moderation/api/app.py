"""FastAPI application for the facilitation service."""

from fastapi import FastAPI

from discussion_moderation.agents.facilitator import facilitate
from discussion_moderation.schemas.discussion import (
    DiscussionThread,
    FacilitationResult,
)

app = FastAPI(
    title="Discussion Facilitation",
    version="0.1.0",
)


@app.post("/facilitate", response_model=FacilitationResult)
async def facilitate_thread(
    thread: DiscussionThread,
) -> FacilitationResult:
    """Run the facilitation pipeline on a discussion thread."""
    return await facilitate(thread)


@app.get("/health")
async def health() -> dict[str, str]:
    """Return service health status."""
    return {"status": "ok"}
