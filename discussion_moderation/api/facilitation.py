"""Python API for the facilitation system.

Internal interface; no HTTP. Other Python code imports from here.
The REST API layer imports from this module.
"""

from discussion_moderation.config import get_settings
from discussion_moderation.graph.pipeline import run_pipeline
from discussion_moderation.models import (
    DiscussionThread,
    PipelineDeps,
    PipelineResult,
)
from discussion_moderation.tools import HISTORY_BACKENDS, LMS_BACKENDS


async def facilitate_by_id(thread_id: str) -> PipelineResult:
    """Fetch a thread by ID and run the facilitation pipeline.

    Requires FACILITATION_LMS_BACKEND to be set to a backend that
    implements get_thread(). Use when the caller holds a thread ID
    rather than a fully loaded DiscussionThread.

    Args:
        thread_id: Platform-specific thread identifier.

    Returns:
        PipelineResult with classification, role selection,
        and generated response (if intervention is needed).

    Raises:
        ValueError: If no LMS backend is configured.
    """
    settings = get_settings()
    lms_backend = LMS_BACKENDS.get(settings.lms_backend, lambda: None)()
    if lms_backend is None:
        raise ValueError(
            "facilitate_by_id requires an LMS backend. "
            "Set FACILITATION_LMS_BACKEND (e.g. 'openedx' or 'stub')."
        )
    thread = await lms_backend.get_thread(thread_id)
    return await facilitate(thread)


async def facilitate(thread: DiscussionThread) -> PipelineResult:
    """Run the facilitation pipeline on a discussion thread.

    Args:
        thread: The discussion thread to analyze.

    Returns:
        PipelineResult with classification, role selection,
        and generated response (if intervention is needed).
    """
    settings = get_settings()
    deps = PipelineDeps(
        settings=settings,
        lms_backend=LMS_BACKENDS.get(settings.lms_backend, lambda: None)(),
        history_store=HISTORY_BACKENDS.get(
            settings.history_backend, lambda: None
        )(),
    )
    return await run_pipeline(thread, deps)
