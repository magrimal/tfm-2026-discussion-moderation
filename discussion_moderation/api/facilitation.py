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
from discussion_moderation.tools.protocols import LMSBackend


def _build_backend(settings) -> LMSBackend | None:
    """Instantiate the configured LMS backend from settings.

    Returns None if no backend is configured, so the pipeline runs
    without LMS context (useful in tests and offline playground use).
    """
    if settings.lms_backend == "openedx":
        from discussion_moderation.tools.openedx import OpenEdXBackend

        return OpenEdXBackend(
            forum_url=settings.openedx_forum_url,
            jwt_token=settings.jwt_authentication_token,
        )
    return None


async def facilitate(
    thread: DiscussionThread,
    lms_backend: LMSBackend | None = None,
) -> PipelineResult:
    """Run the facilitation pipeline on a discussion thread.

    Description:
        Entry point for the facilitation system. Builds pipeline
        dependencies from settings and runs the graph pipeline.
        When `lms_backend` is not provided, instantiates the backend
        configured in `settings.lms_backend`.

    Args:
        thread: The discussion thread to analyze.
        lms_backend: LMS backend to use. When None, the backend is
            built from settings. Pass explicitly to override (e.g.
            in tests or when the caller already holds a backend).

    Returns:
        PipelineResult with classification, role selection,
        and generated response (if intervention is needed).
    """
    settings = get_settings()
    if lms_backend is None:
        lms_backend = _build_backend(settings)
    deps = PipelineDeps(
        settings=settings,
        lms_backend=lms_backend,
        classification_eval_enabled=(settings.classifier_eval_enabled),
        response_eval_enabled=settings.response_eval_enabled,
        max_orchestrator_retries=(settings.max_orchestrator_retries),
    )
    return await run_pipeline(thread, deps)
