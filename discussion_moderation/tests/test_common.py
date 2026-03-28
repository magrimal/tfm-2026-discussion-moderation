"""Tests for shared types and constants."""

from datetime import UTC, datetime

from discussion_moderation.common.constants import (
    ActionCategory,
    DiscussionState,
    FacilitationRole,
)
from discussion_moderation.common.models import (
    ClassificationResult,
    Comment,
    DiscussionThread,
    FacilitationResponse,
    PipelineResult,
    RoleSelection,
)


class TestDiscussionThread:
    """Validate DiscussionThread model construction."""

    def test_create_thread_with_children(self):
        """Create a thread with comments.

        Expected result: Thread has correct title and comment count.
        """
        thread = DiscussionThread(
            id="abc123",
            course_id="course-v1:UCM+Test+2026",
            title="Ethics in AI",
            learning_objectives=["Identify ethical concerns"],
            created_at=datetime(2026, 3, 1, tzinfo=UTC),
            children=[
                Comment(
                    username="Alice",
                    body="I think bias is the main issue.",
                    created_at=datetime(2026, 3, 1, tzinfo=UTC),
                ),
            ],
        )

        assert thread.title == "Ethics in AI"
        assert len(thread.children) == 1

    def test_create_empty_thread(self):
        """Create a thread with no comments.

        Expected result: Children list is empty.
        """
        thread = DiscussionThread(
            id="abc123",
            course_id="course-v1:UCM+Test+2026",
            title="Ethics in AI",
            learning_objectives=["Identify ethical concerns"],
            created_at=datetime(2026, 3, 1, tzinfo=UTC),
            children=[],
        )

        assert thread.children == []


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
