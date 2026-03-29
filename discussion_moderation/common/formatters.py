"""Thread and role description formatters for agent prompts."""

from datetime import UTC, datetime

from discussion_moderation.common.constants import FacilitationRole
from discussion_moderation.common.models import DiscussionThread


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


def format_role_descriptions() -> str:
    """Format role descriptions for the orchestrator prompt.

    Returns:
        Formatted string with role names and descriptions.
    """
    descriptions = {
        FacilitationRole.ORGANIZATIONAL: (
            "Structures the discussion: launches topics, "
            "summarizes, redirects off-topic threads, "
            "manages phases, closes discussions."
        ),
        FacilitationRole.INTELLECTUAL: (
            "Deepens thinking: asks Socratic questions, "
            "challenges with counterarguments, solicits "
            "evidence, revoices contributions, structures "
            "arguments."
        ),
        FacilitationRole.SOCIAL: (
            "Builds community: encourages participation, "
            "redistributes attention, acknowledges "
            "contributions, models constructive interaction."
        ),
        FacilitationRole.AFFECTIVE: (
            "Provides emotional support: validates feelings, "
            "acknowledges effort, uses positive framing, "
            "maintains psychological safety."
        ),
        FacilitationRole.MODERATOR: (
            "Handles moderation: flags inappropriate content, "
            "addresses escalating conflicts, manages "
            "copyright concerns."
        ),
    }
    return "\n".join(
        f"- **{role.value}**: {desc}"
        for role, desc in descriptions.items()
    )
