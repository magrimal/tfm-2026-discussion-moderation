"""Python API for the facilitation system.

Internal interface; no HTTP. Other Python code imports from here.
The REST API layer imports from this module.
"""

from dataclasses import dataclass

from discussion_moderation.config import get_settings
from discussion_moderation.graph.pipeline import run_pipeline
from discussion_moderation.models import (
    DiscussionThread,
    PipelineDeps,
    PipelineResult,
)
from discussion_moderation.tools.history import (
    SQLiteThreadStore,
    ThreadHistoryStore,
)
from discussion_moderation.tools.protocols import LMSBackend


def _build_history_store() -> ThreadHistoryStore | None:
    """Instantiate the configured ThreadHistoryStore.

    Reads history_backend and history_db_path from Settings.
    Returns None for unrecognised backend keys.
    """
    settings = get_settings()
    if settings.history_backend == "sqlite":
        return SQLiteThreadStore(db_path=settings.history_db_path)
    return ThreadHistoryStore.for_key(settings.history_backend)


@dataclass
class FacilitationOutcome:
    """Result of a full facilitation cycle including optional write-back.

    Attributes:
        result: Pipeline output (classification, role, response).
        comment_posted: True if a comment was posted back to the forum.
        comment_id: ID of the posted comment, or None if not posted.
    """

    result: PipelineResult
    comment_posted: bool
    comment_id: str | None = None


async def facilitate_and_post(thread_id: str) -> FacilitationOutcome:
    """Fetch a thread, run the pipeline, and post back if warranted.

    The full integration cycle used by the webhook endpoint:
    1. Fetch thread from the configured LMS backend.
    2. Run the facilitation pipeline.
    3. If the pipeline decides to intervene and FACILITATION_BOT_USER_ID
       is set, post the response as a comment on the thread.

    Args:
        thread_id: Platform-specific thread identifier.

    Returns:
        FacilitationOutcome with the pipeline result and write-back status.

    Raises:
        ValueError: If no LMS backend is configured.
    """
    settings = get_settings()
    lms_backend = LMSBackend.for_key(settings.lms_backend)
    if lms_backend is None:
        raise ValueError(
            "facilitate_and_post requires an LMS backend. "
            "Set FACILITATION_LMS_BACKEND (e.g. 'openedx' or 'stub')."
        )
    thread = await lms_backend.get_thread(thread_id)
    result = await facilitate(thread)

    should_post = (
        result.intervention is not None
        and result.intervention.should_intervene
        and result.response is not None
        and bool(settings.bot_user_id)
    )
    if should_post and result.response is not None:
        comment_id = await lms_backend.post_comment(
            thread,
            result.response.response_text,
            settings.bot_user_id,
        )
        return FacilitationOutcome(
            result=result, comment_posted=True, comment_id=comment_id
        )

    return FacilitationOutcome(result=result, comment_posted=False)


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
    lms_backend = LMSBackend.for_key(settings.lms_backend)
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
        lms_backend=LMSBackend.for_key(settings.lms_backend),
        history_store=_build_history_store(),
    )
    return await run_pipeline(thread, deps)
