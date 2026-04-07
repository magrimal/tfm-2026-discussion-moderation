"""Open edX LMS backend implementation.

Provides two things:

1. Pydantic models (`OpenEdXThread`, `OpenEdXComment`) that mirror
   the shape of the Open edX Discussion API v1 response. Only the
   fields used by the mapper are declared; extras are ignored.

2. `OpenEdXBackend`, which implements the `LMSBackend` protocol and
   is responsible for constructing fully populated `DiscussionThread`
   objects from raw API data. The pipeline only sees generic domain
   models; all Open edX specifics stay in this module.

Mapping convention:
- `OpenEdXThread.author` + `raw_body` → synthetic first Comment
  in `DiscussionThread.children` (the opening post)
- `OpenEdXComment.children` (nested replies) → `Comment.replies`
- `learning_objectives` is NOT in the thread API; callers inject it
  from course metadata when available.
"""

from datetime import datetime

from pydantic import BaseModel, Field

from discussion_moderation.models import Comment, CourseContext, DiscussionThread
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
# Mapper
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

    Implements `LMSBackend` for Open edX. Responsible for fetching
    data from the Open edX APIs and returning fully populated domain
    models. The pipeline only sees generic `DiscussionThread` and
    `Comment` objects.

    The `map_thread` function handles the structural mapping. HTTP
    calls are stubbed until connected to the actual APIs.

    Attributes:
        base_url: The Open edX instance base URL.
    """

    def __init__(self, base_url: str = "http://localhost:18000"):
        self.base_url = base_url

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
        """Fetch a thread and its comments from Open edX and map them.

        Makes two API calls: one for the thread object, one for its
        comments. Returns a fully populated DiscussionThread.

        Args:
            thread_id: Open edX thread ID.
            learning_objectives: Course LOs to inject into the thread.
                Fetch separately from the course API if needed.

        Returns:
            DiscussionThread ready for the facilitation pipeline.
        """
        # TODO: GET {base_url}/api/discussion/v1/threads/{thread_id}/
        # TODO: GET {base_url}/api/discussion/v1/comments/?thread_id={thread_id}
        raise NotImplementedError(
            "OpenEdXBackend.get_thread is not yet connected to the API."
        )

    async def get_participant_history(
        self,
        course_id: str,
        user_id: str,
    ) -> list[Comment]:
        """Retrieve a participant's recent posts from Open edX.

        Args:
            course_id: Open edX course key.
            user_id: Open edX username.

        Returns:
            List of the participant's recent posts.
        """
        # TODO: connect to Open edX forum IDA user posts endpoint
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
        reason: str,
    ) -> None:
        """Flag a post for instructor review in Open edX.

        Args:
            post_id: Open edX forum post ID.
            reason: Human-readable explanation for the flag.
        """
        # TODO: connect to Open edX moderation API
        pass
