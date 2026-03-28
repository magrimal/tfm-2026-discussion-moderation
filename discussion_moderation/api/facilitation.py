"""Python API for the facilitation system.

Internal interface — no HTTP. Other Python code imports from here.
The REST API layer imports from this module.
"""

from discussion_moderation.common.models import (
    CourseContext,
    DiscussionThread,
    PipelineDeps,
    PipelineResult,
)
from discussion_moderation.graph.pipeline import run_pipeline
from discussion_moderation.settings import get_settings


async def facilitate(
    thread: DiscussionThread,
    course_context: CourseContext | None = None,
) -> PipelineResult:
    """Run the facilitation pipeline on a discussion thread.

    Description:
        Entry point for the facilitation system. Builds pipeline
        dependencies from settings and runs the graph pipeline.

    Args:
        thread: The discussion thread to analyze.
        course_context: Optional course context for prompt
            parameterization and audience adaptation.

    Returns:
        PipelineResult with classification, role selection,
        and generated response (if intervention is needed).
    """
    settings = get_settings()
    deps = PipelineDeps(
        settings=settings,
        course_context=course_context,
        classifier_eval_enabled=(settings.classifier_eval_enabled),
        response_eval_enabled=settings.response_eval_enabled,
        writer_enabled=settings.writer_enabled,
        max_orchestrator_retries=(settings.max_orchestrator_retries),
    )
    return await run_pipeline(thread, deps)
