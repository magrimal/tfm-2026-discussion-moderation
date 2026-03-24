"""Expected behaviors for the classifier agent evaluation.

Defines what the classifier should produce for each sample
thread state.
"""

from dataclasses import dataclass

from discussion_moderation.common.constants import (
    DiscussionState,
    FacilitationRole,
)


@dataclass
class ClassifierExpectation:
    """Expected classifier output for a sample thread.

    Attributes:
        expected_state: The correct discussion state.
        should_intervene: Whether intervention is expected.
        acceptable_roles: Roles that would be reasonable if
            intervention is needed. None if no intervention.
    """

    expected_state: DiscussionState
    should_intervene: bool
    acceptable_roles: list[FacilitationRole] | None = None


CLASSIFIER_EXPECTATIONS: dict[str, ClassifierExpectation] = {
    "new": ClassifierExpectation(
        expected_state=DiscussionState.NEW,
        should_intervene=True,
        acceptable_roles=[
            FacilitationRole.ORGANIZATIONAL,
            FacilitationRole.SOCIAL,
        ],
    ),
    "active": ClassifierExpectation(
        expected_state=DiscussionState.ACTIVE,
        should_intervene=False,
    ),
    "stalled": ClassifierExpectation(
        expected_state=DiscussionState.STALLED,
        should_intervene=True,
        acceptable_roles=[
            FacilitationRole.SOCIAL,
            FacilitationRole.INTELLECTUAL,
            FacilitationRole.ORGANIZATIONAL,
        ],
    ),
    "conflictive": ClassifierExpectation(
        expected_state=DiscussionState.CONFLICTIVE,
        should_intervene=True,
        acceptable_roles=[
            FacilitationRole.SOCIAL,
            FacilitationRole.MODERATOR,
            FacilitationRole.AFFECTIVE,
        ],
    ),
    "convergent": ClassifierExpectation(
        expected_state=DiscussionState.CONVERGENT,
        should_intervene=False,
    ),
    "off_topic": ClassifierExpectation(
        expected_state=DiscussionState.OFF_TOPIC,
        should_intervene=True,
        acceptable_roles=[
            FacilitationRole.ORGANIZATIONAL,
        ],
    ),
}
