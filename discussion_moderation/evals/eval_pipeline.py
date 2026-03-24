"""End-to-end evaluation of the facilitation pipeline.

Runs the full graph pipeline against sample threads and checks
classification, role selection, and response quality.

Usage:
    uv run python -m discussion_moderation.evals.eval_pipeline
"""

from discussion_moderation.api.facilitation import facilitate
from discussion_moderation.common.types import (
    PipelineResult,
)
from discussion_moderation.evals.expectations.classifier import (
    CLASSIFIER_EXPECTATIONS,
)
from discussion_moderation.evals.fixtures.courses import (
    AI_ETHICS_COURSE,
)
from discussion_moderation.evals.fixtures.threads import (
    ALL_THREADS,
)
from discussion_moderation.evals.utils import setup_eval_logging

logger = setup_eval_logging("eval_pipeline")


async def run_eval() -> None:
    """Run the end-to-end pipeline evaluation.

    Description:
        Evaluates the full facilitation pipeline against all
        sample threads. Reports classification accuracy, role
        selection, and response characteristics.
    """
    results: dict[str, PipelineResult] = {}
    passed = 0
    total = len(ALL_THREADS)

    for name, thread_fn in ALL_THREADS.items():
        thread = thread_fn()
        logger.info("Running pipeline on '%s' thread...", name)

        try:
            result = await facilitate(thread, course_context=AI_ETHICS_COURSE)
            results[name] = result
        except Exception:
            logger.exception("[%s] Pipeline failed with exception", name)
            continue

        expected = CLASSIFIER_EXPECTATIONS[name]
        state_ok = result.classification.state == expected.expected_state
        intervene_ok = (
            result.classification.should_intervene == expected.should_intervene
        )

        role_ok = True
        if result.role_selection and expected.acceptable_roles:
            role_ok = result.role_selection.role in expected.acceptable_roles

        all_ok = state_ok and intervene_ok and role_ok
        if all_ok:
            passed += 1

        status = "PASS" if all_ok else "FAIL"
        logger.info(
            "[%s] %s — state=%s(%s) intervene=%s(%s)",
            name,
            status,
            result.classification.state,
            "ok" if state_ok else "MISMATCH",
            result.classification.should_intervene,
            "ok" if intervene_ok else "MISMATCH",
        )

        if result.role_selection:
            logger.info(
                "[%s]   role=%s (%s)",
                name,
                result.role_selection.role,
                "ok" if role_ok else "UNEXPECTED",
            )

        if result.final_text:
            preview = result.final_text[:120]
            logger.info("[%s]   response: %s...", name, preview)

    logger.info("--- Summary: %d/%d passed ---", passed, total)


if __name__ == "__main__":
    import asyncio

    asyncio.run(run_eval())
