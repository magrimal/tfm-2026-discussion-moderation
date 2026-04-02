"""Shared utility functions for the facilitation system."""

from datetime import UTC, datetime

from discussion_moderation.models import DiscussionThread


def format_thread(
    thread: DiscussionThread,
    now: datetime | None = None,
) -> str:
    """Format a discussion thread as an agent prompt string.

    Args:
        thread: The discussion thread to format.
        now: Reference timestamp. Defaults to current UTC time.

    Returns:
        Formatted string with thread metadata and comments.
    """
    now = now or datetime.now(UTC)
    lines = [
        f"Current timestamp: {now.isoformat()}",
        f"Topic: {thread.title}",
        f"Learning objectives: {', '.join(thread.learning_objectives)}",
        "",
        "Responses:",
    ]
    for comment in thread.children:
        lines.append(
            f"- [{comment.created_at.isoformat()}]"
            f" {comment.username}: {comment.body}"
        )
    if not thread.children:
        lines.append("(No responses yet)")
    return "\n".join(lines)
