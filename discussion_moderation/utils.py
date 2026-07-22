"""Shared utility functions for the facilitation system."""

from datetime import UTC, datetime

from opentelemetry import trace as otel_trace

from discussion_moderation.models import Comment, DiscussionThread


def logfire_trace_url(project_url: str) -> str | None:
    """Return the Logfire trace URL for the current OpenTelemetry span.

    Args:
        project_url: Base Logfire project URL (settings.logfire_project_url).
            Empty string means Logfire isn't configured for this run.

    Returns:
        A direct link to the current trace, or None if there's no
        active span or no project URL configured.
    """
    if not project_url:
        return None
    try:
        ctx = otel_trace.get_current_span().get_span_context()
        if not ctx.is_valid:
            return None
        return f"{project_url.rstrip('/')}/trace/{ctx.trace_id:032x}"
    except Exception:
        return None


MAX_REASONING_CHARS = 500


def cap_reasoning(text: str) -> str:
    """Cap upstream agent reasoning before inlining it into a prompt.

    Classification/intervention/orchestrator reasoning is written for
    a human reviewer and routinely runs to several hundred words. It
    gets inlined into the intervention, orchestrator, and role
    prompts - up to three times for the same text by the time it
    reaches the role agent - and is a major contributor to hitting
    Ollama's default 4096-token context window on longer, retry-heavy
    runs (observed directly via input_tokens pinning at ~4096 on live
    idril runs).
    """
    if len(text) <= MAX_REASONING_CHARS:
        return text
    return text[:MAX_REASONING_CHARS].rstrip() + "... [truncated]"


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
