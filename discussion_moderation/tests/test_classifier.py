"""Tests for the classifier agent prompt construction."""

from datetime import UTC, datetime

from discussion_moderation.common.formatters import format_thread
from discussion_moderation.common.models import (
    Comment,
    DiscussionThread,
)


class TestFormatThread:
    """Validate thread formatting for agent prompts."""

    def test_formats_thread_with_posts(self):
        """Format a thread with posts.

        Expected result: Prompt includes timestamp, topic,
        objectives, and post content.
        """
        thread = DiscussionThread(
            id="test-1",
            course_id="course-v1:UCM+Test+2026",
            title="Ethics in AI",
            created_at=datetime(2026, 3, 1, tzinfo=UTC),
            learning_objectives=[
                "Identify ethical concerns",
                "Propose mitigations",
            ],
            children=[
                Comment(
                    username="Alice",
                    body="Bias is the main issue.",
                    created_at=datetime(2026, 3, 1, 10, 0, tzinfo=UTC),
                ),
            ],
        )

        now = datetime(2026, 3, 5, 12, 0, tzinfo=UTC)
        prompt = format_thread(thread, now=now)

        assert "Current timestamp: 2026-03-05" in prompt
        assert "Topic: Ethics in AI" in prompt
        assert "Identify ethical concerns" in prompt
        assert "Alice: Bias is the main issue." in prompt

    def test_formats_empty_thread(self):
        """Format a thread with no posts.

        Expected result: Prompt contains "(No responses yet)"
        placeholder.
        """
        thread = DiscussionThread(
            id="test-2",
            course_id="course-v1:UCM+Test+2026",
            title="Ethics in AI",
            created_at=datetime(2026, 3, 1, tzinfo=UTC),
            learning_objectives=["Identify ethical concerns"],
            children=[],
        )

        prompt = format_thread(thread)

        assert "Current timestamp:" in prompt
        assert "(No responses yet)" in prompt
