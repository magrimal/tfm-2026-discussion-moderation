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


# --- Comment new fields ---


def test_comment_author_label_defaults_to_none():
    comment = Comment(username="alice", body="Hi", created_at=_now())

    assert comment.author_label is None


def test_comment_endorsed_defaults_to_false():
    comment = Comment(username="alice", body="Hi", created_at=_now())

    assert comment.endorsed is False


def test_comment_abuse_flagged_defaults_to_false():
    comment = Comment(username="alice", body="Hi", created_at=_now())

    assert comment.abuse_flagged is False


def test_comment_vote_count_defaults_to_zero():
    comment = Comment(username="alice", body="Hi", created_at=_now())

    assert comment.vote_count == 0


def test_comment_replies_defaults_to_empty_list():
    comment = Comment(username="alice", body="Hi", created_at=_now())

    assert comment.replies == []


def test_comment_accepts_nested_replies():
    now = _now()
    reply = Comment(username="bob", body="Indeed.", created_at=now)
    parent = Comment(
        username="alice", body="Hello!", created_at=now, replies=[reply]
    )

    assert len(parent.replies) == 1
    assert parent.replies[0].username == "bob"


def test_comment_nesting_is_recursive():
    now = _now()
    deep = Comment(username="carol", body="Deep reply.", created_at=now)
    mid = Comment(username="bob", body="Mid reply.", created_at=now, replies=[deep])
    top = Comment(username="alice", body="Top.", created_at=now, replies=[mid])

    assert top.replies[0].replies[0].username == "carol"


# --- DiscussionThread new fields ---


def test_thread_learning_objectives_defaults_to_empty_list():
    thread = _minimal_thread()

    assert thread.learning_objectives == []


def test_thread_has_endorsed_defaults_to_false():
    thread = _minimal_thread()

    assert thread.has_endorsed is False


# --- RoleSelection ---


def test_role_selection_rejects_invalid_role():
    with pytest.raises(ValidationError):
        RoleSelection(role="not_a_role", reasoning="x")  # type: ignore[arg-type]


def test_role_selection_valid_construction():
    selection = RoleSelection(
        role=FacilitationRole.INTELLECTUAL, reasoning="Thread needs depth."
    )

    assert selection.role == FacilitationRole.INTELLECTUAL
