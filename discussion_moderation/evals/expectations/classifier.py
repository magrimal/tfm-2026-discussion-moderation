"""Expected behaviors for the classifier agent evaluation.

Defines what the classifier should produce for each sample
thread state.
"""

from dataclasses import dataclass

from discussion_moderation.constants import (
    DiscussionState,
    DiscussionTrajectory,
    FacilitationRole,
    InquiryPhase,
)


@dataclass
class ClassifierExpectation:
    """Expected classifier output for a sample thread.

    Attributes:
        expected_state: The correct discussion state.
        should_intervene: Whether intervention is expected.
        acceptable_roles: Roles that would be reasonable if
            intervention is needed. None if no intervention.
        expected_trajectory: Expected temporal engagement pattern.
            None means any trajectory is acceptable.
        expected_inquiry_phase: Expected PIM phase. None means
            any phase is acceptable.
    """

    expected_state: DiscussionState
    should_intervene: bool
    acceptable_roles: list[FacilitationRole] | None = None
    expected_trajectory: DiscussionTrajectory | None = None
    expected_inquiry_phase: InquiryPhase | None = None


CLASSIFIER_EXPECTATIONS: dict[str, ClassifierExpectation] = {
    "new": ClassifierExpectation(
        expected_state=DiscussionState.NEW,
        should_intervene=True,
        acceptable_roles=[
            FacilitationRole.ORGANIZATIONAL,
            FacilitationRole.SOCIAL,
        ],
        expected_trajectory=DiscussionTrajectory.NEVER_STARTED,
        expected_inquiry_phase=InquiryPhase.TRIGGERING,
    ),
    "active": ClassifierExpectation(
        expected_state=DiscussionState.ACTIVE,
        should_intervene=False,
        expected_trajectory=DiscussionTrajectory.GROWING,
        expected_inquiry_phase=InquiryPhase.EXPLORATION,
    ),
    "stalled": ClassifierExpectation(
        expected_state=DiscussionState.STALLED,
        should_intervene=True,
        acceptable_roles=[
            FacilitationRole.SOCIAL,
            FacilitationRole.INTELLECTUAL,
            FacilitationRole.ORGANIZATIONAL,
        ],
        expected_trajectory=DiscussionTrajectory.DECLINING,
        expected_inquiry_phase=InquiryPhase.TRIGGERING,
    ),
    "conflictive": ClassifierExpectation(
        expected_state=DiscussionState.CONFLICTIVE,
        should_intervene=True,
        acceptable_roles=[
            FacilitationRole.SOCIAL,
            FacilitationRole.MODERATOR,
            FacilitationRole.AFFECTIVE,
        ],
        expected_inquiry_phase=InquiryPhase.EXPLORATION,
    ),
    "convergent": ClassifierExpectation(
        expected_state=DiscussionState.CONVERGENT,
        should_intervene=False,
        expected_trajectory=DiscussionTrajectory.STABLE,
        expected_inquiry_phase=InquiryPhase.RESOLUTION,
    ),
    "off_topic": ClassifierExpectation(
        expected_state=DiscussionState.OFF_TOPIC,
        should_intervene=True,
        acceptable_roles=[
            FacilitationRole.ORGANIZATIONAL,
        ],
        expected_trajectory=DiscussionTrajectory.DECLINING,
    ),
}
