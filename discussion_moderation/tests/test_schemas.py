"""Tests for discussion schemas."""

from datetime import UTC, datetime

from discussion_moderation.schemas.discussion import (
    ActionCategory,
    ClassificationResult,
    DiscussionState,
    DiscussionThread,
    FacilitationResult,
    Post,
)


class TestDiscussionThread:
    """Validate DiscussionThread model construction."""

    def test_create_thread_with_posts(self):
        thread = DiscussionThread(
            topic="Ethics in AI",
            learning_objectives=["Identify ethical concerns"],
            posts=[
                Post(
                    author="Alice",
                    content="I think bias is the main issue.",
                    timestamp=datetime(2026, 3, 1, tzinfo=UTC),
                ),
            ],
        )

        assert thread.topic == "Ethics in AI"
        assert len(thread.posts) == 1

    def test_create_empty_thread(self):
        thread = DiscussionThread(
            topic="Ethics in AI",
            learning_objectives=["Identify ethical concerns"],
            posts=[],
        )

        assert thread.posts == []


class TestFacilitationResult:
    """Validate FacilitationResult model construction."""

    def test_no_intervention(self):
        result = FacilitationResult(
            classification=ClassificationResult(
                state=DiscussionState.ACTIVE,
                should_intervene=False,
                reasoning="Discussion is healthy.",
            ),
            action=None,
            response=None,
        )

        assert not result.classification.should_intervene
        assert result.action is None

    def test_with_intervention(self):
        result = FacilitationResult(
            classification=ClassificationResult(
                state=DiscussionState.STALLED,
                should_intervene=True,
                reasoning="No posts in 3 days.",
            ),
            action={
                "category": ActionCategory.SOCIAL,
                "action": "Encourage participation",
                "reasoning": "Thread is stalled.",
            },
            response="What do you all think about...?",
        )

        assert result.classification.should_intervene
        assert result.action.category == ActionCategory.SOCIAL
        assert result.response is not None
