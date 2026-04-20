"""Evaluation suite for the classification and intervention agents.

Runs both agents against sample threads and checks whether
the discussion state is classified correctly and the intervention
decision makes sense.
"""

from dataclasses import dataclass

from pydantic_evals import Case, Dataset

from discussion_moderation.agents.classification import (
    ClassificationDeps,
    classification_agent,
)
from discussion_moderation.agents.intervention import (
    InterventionDeps,
    intervention_agent,
)
from discussion_moderation.constants import (
    DiscourseQuality,
    DiscussionState,
    DiscussionTrajectory,
    InquiryPhase,
    ParticipationBalance,
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
from discussion_moderation.models import DiscussionThread

DISCUSSION_CONTEXT = "asynchronous academic discussion threads"

logger = setup_eval_logging("eval_classifier")


@dataclass
class ClassifierEvalOutput:
    """Combined output of classification and intervention agents.

    Attributes:
        state: Detected discussion state.
        trajectory: Temporal engagement pattern.
        participation_balance: Participation structure across
            contributors.
        discourse_quality: Whether posts are substantive or
            formulaic.
        inquiry_phase: PIM phase (Garrison et al. 2001).
        should_intervene: Whether intervention was decided.
        classification_reasoning: Reasoning from the classification
            agent.
        intervention_reasoning: Reasoning from the intervention
            agent.
    """

    state: DiscussionState
    trajectory: DiscussionTrajectory
    participation_balance: ParticipationBalance
    discourse_quality: DiscourseQuality
    inquiry_phase: InquiryPhase
    should_intervene: bool
    classification_reasoning: str
    intervention_reasoning: str


async def _classify_thread(
    thread: DiscussionThread,
) -> ClassifierEvalOutput:
    """Run classification and intervention agents on a thread.

    Args:
        thread: The discussion thread to evaluate.

    Returns:
        ClassifierEvalOutput with state and intervention decision.
    """
    classification_deps = ClassificationDeps(
        stalled_threshold_hours=48,
        current_timestamp=NOW,
        discussion_context=DISCUSSION_CONTEXT,
    )
    classification = await classification_agent.run(thread, classification_deps)

    intervention_deps = InterventionDeps(
        classification=classification,
        stalled_threshold_hours=48,
        current_timestamp=NOW,
        discussion_context=DISCUSSION_CONTEXT,
    )
    intervention = await intervention_agent.run(thread, intervention_deps)

    return ClassifierEvalOutput(
        state=classification.state,
        trajectory=classification.trajectory,
        participation_balance=classification.participation_balance,
        discourse_quality=classification.discourse_quality,
        inquiry_phase=classification.inquiry_phase,
        should_intervene=intervention.should_intervene,
        classification_reasoning=classification.reasoning,
        intervention_reasoning=intervention.reasoning,
    )


def build_dataset() -> Dataset[
    DiscussionThread,
    ClassifierEvalOutput,
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
        Evaluates the classification and intervention agents
        against all sample threads and reports state classification
        accuracy and intervention decision correctness.
    """
    dataset = build_dataset()
    report = await dataset.evaluate(_classify_thread)
    report.print()

    logger.info("--- Detailed classifier results ---")
    for case_result in report.cases:
        name = case_result.name
        expected = CLASSIFIER_EXPECTATIONS[name]
        output: ClassifierEvalOutput = case_result.output

        state_match = output.state == expected.expected_state
        intervene_match = output.should_intervene == expected.should_intervene

        trajectory_match = (
            expected.expected_trajectory is None
            or output.trajectory == expected.expected_trajectory
        )
        inquiry_match = (
            expected.expected_inquiry_phase is None
            or output.inquiry_phase == expected.expected_inquiry_phase
        )

        logger.info(
            "[%s] state=%s (expected=%s) match=%s"
            " intervene=%s (expected=%s) match=%s",
            name,
            output.state,
            expected.expected_state,
            state_match,
            output.should_intervene,
            expected.should_intervene,
            intervene_match,
        )
        logger.info(
            "[%s]   trajectory=%s (expected=%s) match=%s"
            " inquiry=%s (expected=%s) match=%s",
            name,
            output.trajectory,
            expected.expected_trajectory,
            trajectory_match,
            output.inquiry_phase,
            expected.expected_inquiry_phase,
            inquiry_match,
        )
        logger.info(
            "[%s]   participation=%s discourse=%s",
            name,
            output.participation_balance,
            output.discourse_quality,
        )


def main() -> None:
    """Entry point for the classifier eval script."""
    import asyncio

    asyncio.run(run_eval())
