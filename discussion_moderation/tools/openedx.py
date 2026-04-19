"""Open edX LMS backend implementation.

Provides two things:

1. Pydantic models (`OpenEdXThread`, `OpenEdXComment`) that mirror
   the Open edX Discussion API v1 response format. Used by the
   `map_thread` utility and its unit tests.

2. `OpenEdXBackend`, which implements the `LMSBackend` protocol,
   makes HTTP calls to the internal forum service (`/api/v2/`) using
   JWT authentication, and fills `DiscussionThread` / `Comment`
   domain objects directly from the response JSON. No intermediate
   API models. The pipeline only sees generic domain models.

Convention for `get_thread`:
- Thread author + body → synthetic first Comment in `children`
  (the opening post)
- `children` in each comment response → `Comment.replies` (recursive)
- `learning_objectives` is NOT in the thread API; callers inject it
  from course metadata when available.
"""

from datetime import datetime

import httpx
from pydantic import BaseModel, Field

from discussion_moderation.models import (
    Comment,
    CourseContext,
    DiscussionThread,
)
from discussion_moderation.tools.protocols import LMSBackend

# ---------------------------------------------------------------------------
# Open edX API response models
# ---------------------------------------------------------------------------


class OpenEdXComment(BaseModel):
    """A comment from the Open edX Discussion API v1 comments endpoint.

    Only the fields used by the mapper are declared. The API returns
    many additional fields (editable_fields, voted, etc.) which are
    ignored via Pydantic's default extra-field behaviour.
    """

    model_config = {"extra": "ignore"}

    id: str
    author: str
    author_label: str | None = None
    created_at: datetime
    raw_body: str
    endorsed: bool = False
    abuse_flagged: bool = False
    vote_count: int = 0
    children: list["OpenEdXComment"] = Field(default_factory=list)


OpenEdXComment.model_rebuild()


class OpenEdXThread(BaseModel):
    """A thread from the Open edX Discussion API v1 threads endpoint.

    The thread object contains the opening post's body directly
    (`raw_body`). Comments are fetched separately via the
    `comment_list_url` endpoint and passed to `map_thread`.
    """

    model_config = {"extra": "ignore"}

    id: str
    author: str
    author_label: str | None = None
    created_at: datetime
    updated_at: datetime | None = None
    raw_body: str
    title: str
    course_id: str
    type: str = "discussion"
    closed: bool = False
    has_endorsed: bool = False
    abuse_flagged: bool = False


# ---------------------------------------------------------------------------
# LMS Discussion API v1 mapper
# ---------------------------------------------------------------------------


def _map_comment(api_comment: OpenEdXComment) -> Comment:
    """Recursively map an OpenEdXComment to a Comment.

    Args:
        api_comment: Raw comment from the API.

    Returns:
        Comment with replies populated from api_comment.children.
    """
    return Comment(
        username=api_comment.author,
        body=api_comment.raw_body,
        created_at=api_comment.created_at,
        author_label=api_comment.author_label,
        endorsed=api_comment.endorsed,
        abuse_flagged=api_comment.abuse_flagged,
        vote_count=api_comment.vote_count,
        replies=[_map_comment(r) for r in api_comment.children],
    )


def map_thread(
    api_thread: OpenEdXThread,
    api_comments: list[OpenEdXComment],
    learning_objectives: list[str] | None = None,
) -> DiscussionThread:
    """Build a DiscussionThread from Open edX API data.

    The opening post (thread author + raw_body) becomes the first
    entry in `children`. Top-level comments follow in order, each
    carrying their nested replies.

    Args:
        api_thread: Thread object from the threads endpoint.
        api_comments: Top-level comments from the comments endpoint,
            each with nested children already populated.
        learning_objectives: Course-level learning objectives for
            this discussion. Not available from the thread API;
            inject from course metadata when available.

    Returns:
        DiscussionThread ready for the facilitation pipeline.
    """
    opening_post = Comment(
        username=api_thread.author,
        body=api_thread.raw_body,
        created_at=api_thread.created_at,
        author_label=api_thread.author_label,
    )
    children = [opening_post] + [_map_comment(c) for c in api_comments]

    return DiscussionThread(
        id=api_thread.id,
        course_id=api_thread.course_id,
        title=api_thread.title,
        created_at=api_thread.created_at,
        last_activity_at=api_thread.updated_at,
        thread_type=api_thread.type,
        closed=api_thread.closed,
        has_endorsed=api_thread.has_endorsed,
        children=children,
        learning_objectives=learning_objectives or [],
    )


# ---------------------------------------------------------------------------
# Backend
# ---------------------------------------------------------------------------


class OpenEdXBackend(LMSBackend):
    """Open edX LMS backend.

    Implements `LMSBackend` for Open edX. Makes HTTP calls to the
    internal forum service (`/api/v2/`) using JWT authentication and
    returns fully populated domain models. The pipeline only sees
    generic domain models; all Open edX specifics stay here.

    Attributes:
        forum_url: Base URL of the internal forum service.
        jwt_token: JWT token for `Authorization: JWT <token>` header.
            Pass an empty string to skip authentication (useful when
            the service runs without auth enforcement in dev).
    """

    def __init__(
        self,
        forum_url: str = "http://localhost:18000",
        jwt_token: str = "",
    ):
        self.forum_url = forum_url.rstrip("/")
        self._headers: dict[str, str] = {}
        if jwt_token:
            self._headers["Authorization"] = f"JWT {jwt_token}"

    async def get_course_context(
        self,
        course_id: str,
    ) -> CourseContext:
        """Retrieve course context from Open edX.

        Args:
            course_id: Open edX course key.

        Returns:
            CourseContext with course metadata.
        """
        # TODO: connect to Open edX course API (course blocks endpoint)
        return CourseContext(
            course_id=course_id,
            display_name=f"Course {course_id}",
            module_topic="Discussion module",
            audience_level="undergraduate",
            language="en",
        )

    async def get_thread(
        self,
        thread_id: str,
        learning_objectives: list[str] | None = None,
    ) -> DiscussionThread:
        """Fetch a thread and its comments from the forum service.

        Calls `GET /api/v2/threads/{thread_id}?recursive=true` to get
        the thread with all nested comments embedded. Fills a
        `DiscussionThread` directly from the response JSON.

        Args:
            thread_id: Forum thread ID.
            learning_objectives: Course LOs to inject into the thread.
                Not available from the thread API; fetch separately.

        Returns:
            DiscussionThread ready for the facilitation pipeline.

        Raises:
            httpx.HTTPStatusError: If the API returns a 4xx or 5xx.
        """
        url = f"{self.forum_url}/api/v2/threads/{thread_id}"
        async with httpx.AsyncClient(headers=self._headers) as client:
            response = await client.get(url, params={"recursive": "true"})
            response.raise_for_status()

        data = response.json()
        opening_post = Comment(
            username=data["author_username"],
            body=data["body"],
            created_at=data["created_at"],
        )
        children = [opening_post] + [
            self._parse_comment(c) for c in data.get("children", [])
        ]
        return DiscussionThread(
            id=data["id"],
            course_id=data["course_id"],
            title=data["title"],
            created_at=data["created_at"],
            last_activity_at=data.get("updated_at"),
            thread_type=data.get("thread_type", "discussion"),
            closed=data.get("closed", False),
            has_endorsed=data.get("endorsed", False),
            children=children,
            learning_objectives=learning_objectives or [],
        )

    def _parse_comment(self, data: dict) -> Comment:
        return Comment(
            username=data["author_username"],
            body=data["body"],
            created_at=data["created_at"],
            endorsed=data.get("endorsed", False),
            abuse_flagged=data.get("abuse_flagged", False),
            vote_count=data.get("votes", {}).get("point", 0),
            replies=[
                self._parse_comment(r) for r in data.get("children", [])
            ],
        )

    async def get_participant_history(
        self,
        course_id: str,
        user_id: str,
    ) -> list[Comment]:
        """Retrieve a participant's recent posts from the forum service.

        Args:
            course_id: Open edX course key.
            user_id: Open edX username.

        Returns:
            List of the participant's recent posts.
        """
        # TODO: GET /api/v2/users/{user_id}/active_threads
        return []

    async def get_course_materials(
        self,
        course_id: str,
        topic: str,
    ) -> list[str]:
        """Retrieve course materials from Open edX.

        Args:
            course_id: Open edX course key.
            topic: Topic to search for.

        Returns:
            List of relevant material excerpts.
        """
        # TODO: connect to Open edX content API
        return []

    async def flag_content(
        self,
        post_id: str,
        reason: str,  # noqa: ARG002 — passed to audit log once connected
    ) -> None:
        """Flag a post for instructor review in the forum service.

        Calls `PUT /api/v2/comments/{post_id}/abuse_flag`. The `reason`
        is not sent to the forum API (it has no reason field) but will
        be recorded in the audit log once that is connected.

        Args:
            post_id: Forum comment or thread ID to flag.
            reason: Human-readable explanation for the flag.

        Raises:
            httpx.HTTPStatusError: If the API returns a 4xx or 5xx.
        """
        url = f"{self.forum_url}/api/v2/comments/{post_id}/abuse_flag"
        async with httpx.AsyncClient(headers=self._headers) as client:
            response = await client.put(url)
            response.raise_for_status()
