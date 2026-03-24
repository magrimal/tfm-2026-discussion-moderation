"""Tests for shared types and constants."""

from datetime import UTC, datetime

from discussion_moderation.common.constants import (
    ActionCategory,
    DiscussionState,
    FacilitationRole,
)
from discussion_moderation.common.types import (
    ClassificationResult,
    DiscussionThread,
    FacilitationResponse,
    PipelineResult,
    Post,
    RoleSelection,
)


class TestDiscussionThread:
    """Validate DiscussionThread model construction."""

    def test_create_thread_with_posts(self):
        """Create a thread with posts.

        Expected result: Thread has correct topic and post count.
        """
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
        """Create a thread with no posts.

        Expected result: Posts list is empty.
        """
        thread = DiscussionThread(
            topic="Ethics in AI",
            learning_objectives=["Identify ethical concerns"],
            posts=[],
        )

        assert thread.posts == []


class TestPipelineResult:
    """Validate PipelineResult model construction."""

    def test_no_intervention(self):
        """Create a result where no intervention is needed.

        Expected result: Only classification is populated;
        role_selection, response, and final_text are None.
        """
        result = PipelineResult(
            classification=ClassificationResult(
                state=DiscussionState.ACTIVE,
                should_intervene=False,
                reasoning="Discussion is healthy.",
            ),
        )

        assert not result.classification.should_intervene
        assert result.role_selection is None
        assert result.response is None
        assert result.final_text is None

    def test_with_intervention(self):
        """Create a result with full intervention pipeline.

        Expected result: All fields are populated with
        consistent data.
        """
        result = PipelineResult(
            classification=ClassificationResult(
                state=DiscussionState.STALLED,
                should_intervene=True,
                reasoning="No posts in 3 days.",
            ),
            role_selection=RoleSelection(
                role=FacilitationRole.SOCIAL,
                reasoning="Thread needs encouragement.",
            ),
            response=FacilitationResponse(
                response_text="What do you all think?",
                technique_used="encourage_participation",
                action_category=ActionCategory.SOCIAL,
                confidence=0.85,
                reasoning="Thread is stalled.",
            ),
            final_text="What do you all think?",
        )

        assert result.classification.should_intervene
        assert result.role_selection.role == FacilitationRole.SOCIAL
        assert result.response is not None
        assert result.final_text is not None


class TestFacilitationRole:
    """Validate FacilitationRole enum has all five roles."""

    def test_has_five_roles(self):
        """Check all five facilitation roles exist.

        Expected result: Enum has organizational, intellectual,
        social, affective, and moderator values.
        """
        roles = list(FacilitationRole)
        assert len(roles) == 5
        assert FacilitationRole.ORGANIZATIONAL in roles
        assert FacilitationRole.INTELLECTUAL in roles
        assert FacilitationRole.SOCIAL in roles
        assert FacilitationRole.AFFECTIVE in roles
        assert FacilitationRole.MODERATOR in roles
