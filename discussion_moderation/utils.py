"""Shared utility functions for the facilitation system."""

from datetime import UTC, datetime

from discussion_moderation.models import Comment, DiscussionThread


def _format_comment(comment: Comment, indent: str = "") -> list[str]:
    label = f" [{comment.author_label}]" if comment.author_label else ""
    endorsed = " [endorsed]" if comment.endorsed else ""
    flagged = " [flagged]" if comment.abuse_flagged else ""
    lines = [
        f"{indent}- [{comment.created_at.isoformat()}]"
        f" {comment.author}{label}{endorsed}{flagged}: {comment.body}"
    ]
    for reply in comment.replies:
        lines.extend(_format_comment(reply, indent + "  "))
    return lines


def format_thread(
    thread: DiscussionThread,
    now: datetime | None = None,
) -> str:
    """Format a discussion thread as an agent prompt string.

    Args:
        thread: The discussion thread to format.
        now: Reference timestamp. Defaults to current UTC time.

    Returns:
        Formatted string with thread metadata and posts.
    """
    now = now or datetime.now(UTC)
    lines = [
        f"Current timestamp: {now.isoformat()}",
        f"Topic: {thread.title}",
    ]
    if thread.learning_objectives:
        lines.append(
            f"Learning objectives: {', '.join(thread.learning_objectives)}"
        )
    if thread.has_endorsed:
        lines.append("Status: question has an accepted answer")
    lines.append("")
    lines.append("Posts:")
    if thread.author or thread.body:
        label = f" [{thread.author_label}]" if thread.author_label else ""
        lines.append(
            f"- [{thread.created_at.isoformat()}]"
            f" {thread.author}{label}: {thread.body}"
        )
    if not thread.comments and not (thread.author or thread.body):
        lines.append("(No posts yet)")
    for comment in thread.comments:
        lines.extend(_format_comment(comment))
    return "\n".join(lines)
