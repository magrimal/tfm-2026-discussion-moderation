"""Tests for the facilitator agent prompt builder."""

from datetime import UTC, datetime

from discussion_moderation.agents.facilitator import (
    _build_prompt,
)
from discussion_moderation.schemas.discussion import (
    DiscussionThread,
    Post,
)


class TestBuildPrompt:
    """Validate prompt construction from discussion threads."""

    def test_formats_thread_with_posts(self):
        thread = DiscussionThread(
            topic="Ethics in AI",
            learning_objectives=[
                "Identify ethical concerns",
                "Propose mitigations",
            ],
            posts=[
                Post(
                    author="Alice",
                    content="Bias is the main issue.",
                    timestamp=datetime(2026, 3, 1, 10, 0, tzinfo=UTC),
                ),
            ],
        )

        now = datetime(2026, 3, 5, 12, 0, tzinfo=UTC)
        prompt = _build_prompt(thread, now=now)

        assert "Current timestamp: 2026-03-05" in prompt
        assert "Topic: Ethics in AI" in prompt
        assert "Identify ethical concerns" in prompt
        assert "Alice: Bias is the main issue." in prompt

    def test_formats_empty_thread(self):
        thread = DiscussionThread(
            topic="Ethics in AI",
            learning_objectives=["Identify ethical concerns"],
            posts=[],
        )

        prompt = _build_prompt(thread)

        assert "Current timestamp:" in prompt
        assert "(No posts yet)" in prompt
