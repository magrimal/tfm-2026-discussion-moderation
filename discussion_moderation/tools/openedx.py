"""Open edX LMS backend implementation."""

import httpx

from discussion_moderation.config import get_settings
from discussion_moderation.models import (
    Comment,
    CourseContext,
    DiscussionThread,
    ThreadSummary,
)
from discussion_moderation.tools.protocols import LMSBackend


class OpenEdXBackend(LMSBackend, key="openedx"):
    """Open edX LMS backend.

    The forum Django app is installed in the LMS at the /forum/ prefix,
    so all forum API calls go to {lms_url}/forum/api/v2/. JWT authentication
    is required. Configuration is read from Settings (lms_url,
    lms_jwt_authentication_token).
    """

    def __init__(self):
        settings = get_settings()
        self.lms_url = settings.lms_url.rstrip("/")
        self._headers: dict[str, str] = {}
        if settings.lms_jwt_authentication_token:
            token = settings.lms_jwt_authentication_token
            self._headers["Authorization"] = f"JWT {token}"

    async def get_thread(
        self,
        thread_id: str,
    ) -> DiscussionThread:
        """Fetch a thread and its comments from the forum service.

        Calls GET /forum/api/v2/threads/{thread_id}?recursive=true to get
        the thread with all nested comments embedded.

        Args:
            thread_id: Forum thread ID.

        Returns:
            DiscussionThread ready for the facilitation pipeline.

        Raises:
            httpx.HTTPStatusError: If the API returns a 4xx or 5xx.
        """
        url = f"{self.lms_url}/forum/api/v2/threads/{thread_id}"
        async with httpx.AsyncClient(headers=self._headers) as client:
            response = await client.get(
                url, params={"with_responses": "true", "recursive": "true"}
            )
            response.raise_for_status()

        data = response.json()
        return DiscussionThread(
            id=data["id"],
            course_id=data["course_id"],
            title=data["title"],
            body=data["body"],
            author=data["username"],
            created_at=data["created_at"],
            last_activity_at=data.get("updated_at"),
            thread_type=data.get("thread_type", "discussion"),
            closed=data.get("closed", False),
            has_endorsed=data.get("endorsed", False),
            comments=[self.parse_comment(c) for c in data.get("children", [])],
        )

    async def post_comment(
        self,
        thread: DiscussionThread,
        body: str,
        author_id: str,
    ) -> str:
        """Post a facilitation comment on a thread.

        Calls POST /forum/api/v2/threads/{thread_id}/comments with JWT auth.

        Args:
            thread: Thread to comment on (provides id and course_id).
            body: Comment text to post.
            author_id: Forum user ID of the account posting the comment.

        Returns:
            The new comment ID assigned by the forum service.

        Raises:
            httpx.HTTPStatusError: If the API returns a 4xx or 5xx.
        """
        url = f"{self.lms_url}/forum/api/v2/threads/{thread.id}/comments"
        payload = {
            "body": body,
            "course_id": thread.course_id,
            "author_id": author_id,
        }
        async with httpx.AsyncClient(headers=self._headers) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
        return str(response.json()["id"])

    async def list_threads(self, course_id: str) -> list[ThreadSummary]:
        """Return active threads for a course from the Open edX discussion API.

        Calls GET /api/discussion/v1/threads/ with course_id and page_size=50.
        Comment bodies are not fetched (list endpoint only provides counts).

        Args:
            course_id: Open edX course key, e.g. "course-v1:Org+Code+Run".

        Returns:
            List of ThreadSummary objects, one per thread in the response.

        Raises:
            httpx.HTTPStatusError: If the API returns a 4xx or 5xx.
        """
        api_url = f"{self.lms_url}/api/discussion/v1/threads/"
        async with httpx.AsyncClient(
            headers=self._headers, timeout=15.0
        ) as client:
            response = await client.get(
                api_url,
                params={"course_id": course_id, "page_size": 50},
            )
            response.raise_for_status()
        threads = response.json().get("results", [])
        return [
            ThreadSummary(
                id=t["id"],
                course_id=t.get("course_id", course_id),
                title=t.get("title", ""),
                body=t.get("raw_body", ""),
                author=t.get("author", ""),
                comment_count=t.get("comment_count", 0),
            )
            for t in threads
        ]

    async def get_course_context(self, course_id: str) -> CourseContext:
        """Return course metadata from the facilitation Django plugin.

        Calls GET {lms_url}/api/facilitation/v1/course-context/{course_id}/.

        The plugin endpoint is expected to implement:
          1. Call get_user_course_outline(user, course_key, at_time) from
             openedx.core.djangoapps.content.learning_sequences.api.
          2. Return a JSON object with:
               display_name (str): CourseOutlineData.title
               sections (list[str]): CourseSectionData.title for each
                   section in CourseOutlineData.sections
               language (str, optional): from course metadata
               module_topic (str, optional): from course metadata
               audience_level (str, optional): from course metadata

        Args:
            course_id: Open edX course key, e.g. "course-v1:Org+Code+Run".

        Returns:
            CourseContext with display name, sections, and optional metadata.

        Raises:
            httpx.HTTPStatusError: If the API returns a 4xx or 5xx.
        """
        url = (
            f"{self.lms_url}/api/facilitation/v1/course-context/"
            f"{course_id}/"
        )
        async with httpx.AsyncClient(headers=self._headers) as client:
            response = await client.get(url)
            response.raise_for_status()
        data = response.json()
        return CourseContext(
            course_id=course_id,
            display_name=data.get("display_name", ""),
            sections=data.get("sections", []),
            module_topic=data.get("module_topic", ""),
            audience_level=data.get("audience_level", ""),
            language=data.get("language", "en"),
        )

    def parse_comment(self, data: dict) -> Comment:
        """Parse a comment dict from the API into a Comment domain object."""
        return Comment(
            author=data["username"],
            body=data["body"],
            created_at=data["created_at"],
            endorsed=data.get("endorsed", False),
            abuse_flagged=data.get("abuse_flagged", False),
            vote_count=data.get("votes", {}).get("point", 0),
            replies=[
                self.parse_comment(reply) for reply in data.get("children", [])
            ],
        )
