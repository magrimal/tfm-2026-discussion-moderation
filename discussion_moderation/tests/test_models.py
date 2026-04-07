"""Unit tests for domain models — no LLM required."""

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from discussion_moderation.constants import (
    ActionCategory,
    DiscourseQuality,
    DiscussionState,
    DiscussionTrajectory,
    FacilitationRole,
    InquiryPhase,
    ParticipationBalance,
)
from discussion_moderation.models import (
    ClassificationResult,
    Comment,
    DiscussionThread,
    FacilitationResponse,
    InterventionDecision,
    RoleSelection,
)


# --- Helpers ---


def _now() -> datetime:
    return datetime.now(tz=timezone.utc)


def _minimal_thread() -> DiscussionThread:
    return DiscussionThread(
        id="t1",
        course_id="course-v1:UCM+TFM+2026",
        title="Test thread",
        learning_objectives=["Understand X"],
        created_at=_now(),
    )


def _minimal_classification() -> ClassificationResult:
    return ClassificationResult(
        state=DiscussionState.ACTIVE,
        trajectory=DiscussionTrajectory.GROWING,
        participation_balance=ParticipationBalance.DISTRIBUTED,
        discourse_quality=DiscourseQuality.SUBSTANTIVE,
        inquiry_phase=InquiryPhase.EXPLORATION,
        reasoning="Test reasoning.",
    )


# --- FacilitationResponse defaults ---


def test_facilitation_response_post_to_thread_defaults_to_true():
    response = FacilitationResponse(
        response_text="Good question!",
        technique_used="socratic_clarification",
        action_category=ActionCategory.INTELLECTUAL,
    )

    assert response.post_to_thread is True


def test_facilitation_response_confidence_defaults_to_one():
    response = FacilitationResponse(
        response_text="Keep going.",
        technique_used="encourage_participation",
        action_category=ActionCategory.SOCIAL,
    )

    assert response.confidence == 1.0


def test_facilitation_response_reasoning_defaults_to_empty_string():
    response = FacilitationResponse(
        response_text="Keep going.",
        technique_used="encourage_participation",
        action_category=ActionCategory.SOCIAL,
    )

    assert response.reasoning == ""


def test_facilitation_response_post_to_thread_can_be_false():
    response = FacilitationResponse(
        response_text="Instructor: escalate this.",
        technique_used="instructor_escalation",
        action_category=ActionCategory.MODERATION,
        post_to_thread=False,
    )

    assert response.post_to_thread is False


# --- ClassificationResult validation ---


def test_classification_result_rejects_invalid_state():
    with pytest.raises(ValidationError):
        ClassificationResult(
            state="not_a_state",  # type: ignore[arg-type]
            trajectory=DiscussionTrajectory.GROWING,
            participation_balance=ParticipationBalance.DISTRIBUTED,
            discourse_quality=DiscourseQuality.SUBSTANTIVE,
            inquiry_phase=InquiryPhase.EXPLORATION,
            reasoning="x",
        )


def test_classification_result_rejects_invalid_trajectory():
    with pytest.raises(ValidationError):
        ClassificationResult(
            state=DiscussionState.ACTIVE,
            trajectory="not_a_trajectory",  # type: ignore[arg-type]
            participation_balance=ParticipationBalance.DISTRIBUTED,
            discourse_quality=DiscourseQuality.SUBSTANTIVE,
            inquiry_phase=InquiryPhase.EXPLORATION,
            reasoning="x",
        )


def test_classification_result_valid_construction():
    result = _minimal_classification()

    assert result.state == DiscussionState.ACTIVE
    assert result.trajectory == DiscussionTrajectory.GROWING


# --- InterventionDecision ---


def test_intervention_decision_should_intervene_true():
    decision = InterventionDecision(
        should_intervene=True, reasoning="Thread stalled."
    )

    assert decision.should_intervene is True


def test_intervention_decision_should_intervene_false():
    decision = InterventionDecision(
        should_intervene=False, reasoning="Thread active."
    )

    assert decision.should_intervene is False


# --- DiscussionThread ---


def test_thread_children_defaults_to_empty_list():
    thread = _minimal_thread()

    assert thread.children == []


def test_thread_closed_defaults_to_false():
    thread = _minimal_thread()

    assert thread.closed is False


def test_thread_accepts_comments():
    comment = Comment(
        username="alice",
        body="Hello!",
        created_at=_now(),
    )
    thread = _minimal_thread()
    thread = thread.model_copy(update={"children": [comment]})

    assert len(thread.children) == 1
    assert thread.children[0].username == "alice"


# --- RoleSelection ---


def test_role_selection_rejects_invalid_role():
    with pytest.raises(ValidationError):
        RoleSelection(role="not_a_role", reasoning="x")  # type: ignore[arg-type]


def test_role_selection_valid_construction():
    selection = RoleSelection(
        role=FacilitationRole.INTELLECTUAL, reasoning="Thread needs depth."
    )

    assert selection.role == FacilitationRole.INTELLECTUAL
