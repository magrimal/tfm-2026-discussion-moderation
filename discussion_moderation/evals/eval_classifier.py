"""Evaluation suite for the classifier agent.

Runs the classifier against sample threads and checks whether
the discussion state is classified correctly and the intervention
decision makes sense.

Usage:
    uv run python -m discussion_moderation.evals.eval_classifier
"""

from pydantic_evals import Case, Dataset

from discussion_moderation.agents.classifier import classify
from discussion_moderation.common.types import (
    ClassificationResult,
    ClassifierDeps,
    DiscussionThread,
)
from discussion_moderation.evals.expectations.classifier import (
    CLASSIFIER_EXPECTATIONS,
    ClassifierExpectation,
)
from discussion_moderation.evals.fixtures.threads import (
    ALL_THREADS,
    NOW,
)
from discussion_moderation.evals.utils import setup_eval_logging

logger = setup_eval_logging("eval_classifier")


async def _classify_thread(
    thread: DiscussionThread,
) -> ClassificationResult:
    """Wrapper for the classifier that creates deps."""
    deps = ClassifierDeps(
        stalled_threshold_hours=48,
        current_timestamp=NOW,
    )
    return await classify(thread, deps)


def build_dataset() -> Dataset[
    DiscussionThread,
    ClassificationResult,
    ClassifierExpectation,
]:
    """Build the evaluation dataset from sample threads.

    Description:
        Creates a pydantic_evals Dataset pairing each sample
        thread with its expected classifier behavior.

    Returns:
        Dataset ready for evaluation.
    """
    cases = []
    for name, thread_fn in ALL_THREADS.items():
        expected = CLASSIFIER_EXPECTATIONS[name]
        cases.append(
            Case(
                name=name,
                inputs=thread_fn(),
                metadata=expected,
                expected_output=None,
            )
        )
    return Dataset(
        name="classifier-eval",
        cases=cases,
    )


async def run_eval() -> None:
    """Run the classifier evaluation and log results.

    Description:
        Evaluates the classifier agent against all sample
        threads and reports state classification accuracy
        and intervention decision correctness.
    """
    dataset = build_dataset()
    report = await dataset.evaluate(_classify_thread)
    report.print()

    logger.info("--- Detailed classifier results ---")
    for case_result in report.cases:
        name = case_result.name
        expected = CLASSIFIER_EXPECTATIONS[name]
        output = case_result.output

        state_match = (
            output.classification.state == expected.expected_state
            if hasattr(output, "classification")
            else output.state == expected.expected_state
        )
        state = getattr(
            output, "state", getattr(output, "classification", output)
        )
        intervene = getattr(output, "should_intervene", None)

        logger.info(
            "[%s] state=%s (expected=%s) match=%s intervene=%s (expected=%s)",
            name,
            state,
            expected.expected_state,
            state_match,
            intervene,
            expected.should_intervene,
        )


if __name__ == "__main__":
    import asyncio

    asyncio.run(run_eval())
