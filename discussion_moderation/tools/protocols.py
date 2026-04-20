"""Protocols for LMS backend integrations and discussion data.

DiscussionContext and CommentContext define the minimum interface the
facilitation pipeline requires from any discussion data source. Platform
backends return objects that satisfy these protocols without mapping to
a shared intermediate model.

LMSBackend defines the interface for LMS-specific operations (fetching
course context, participant history, posting content).
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Protocol, Sequence, runtime_checkable

if TYPE_CHECKING:
    from discussion_moderation.models import DiscussionThread



@runtime_checkable
class CommentContext(Protocol):
    """Minimum interface a comment object must expose to the pipeline."""

    body: str
    author: str
    author_label: str | None
    created_at: datetime
    endorsed: bool
    replies: Sequence["CommentContext"]


@runtime_checkable
class DiscussionContext(Protocol):
    """Minimum interface a thread object must expose to the pipeline.

    The opening argument (body, author) is a first-class field.
    Comments are the replies, not including the opening post.
    """

    id: str
    title: str
    body: str
    author: str
    thread_type: str
    course_id: str
    created_at: datetime
    closed: bool
    has_endorsed: bool
    comments: Sequence[CommentContext]


@runtime_checkable
class LMSBackend(Protocol):
    """Protocol for LMS backend integrations.

    Defines the interface for retrieving course and participant data
    from a learning management system. Implementations handle the
    specifics of each platform's API (Open edX, Moodle, etc.).
    """

    async def get_thread(
        self,
        thread_id: str
    ) -> DiscussionThread:
        """Fetch a thread and its comments from the LMS.

        Args:
            thread_id: Platform-specific thread ID.

        Returns:
            DiscussionThread ready for the facilitation pipeline.

        Raises:
            Exception if the thread cannot be retrieved.
        """
        ...