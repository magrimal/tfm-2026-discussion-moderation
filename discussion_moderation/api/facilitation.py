"""Python API for the facilitation system.

Internal interface; no HTTP. Other Python code imports from here.
The REST API layer imports from this module.
"""

from discussion_moderation.models import (
    DiscussionThread,
    PipelineDeps,
    PipelineResult,
)
from discussion_moderation.graph.pipeline import run_pipeline
from discussion_moderation.config import get_settings
from discussion_moderation.tools.base import LMSBackend


async def facilitate(
    thread: DiscussionThread,
    lms_backend: LMSBackend | None = None,
) -> PipelineResult:
    """Run the facilitation pipeline on a discussion thread.

    Description:
        Entry point for the facilitation system. Builds pipeline
        dependencies from settings and runs the graph pipeline.

    Args:
        thread: The discussion thread to analyze.
        lms_backend: Optional LMS backend for fetching course
            context on demand.

    Returns:
        PipelineResult with classification, role selection,
        and generated response (if intervention is needed).
    """
    settings = get_settings()
    deps = PipelineDeps(
        settings=settings,
        lms_backend=lms_backend,
        classifier_eval_enabled=(settings.classifier_eval_enabled),
        response_eval_enabled=settings.response_eval_enabled,
        writer_enabled=settings.writer_enabled,
        max_orchestrator_retries=(settings.max_orchestrator_retries),
    )
    return await run_pipeline(thread, deps)
