"""Open edX LMS backend implementation."""

import httpx

from discussion_moderation.config import get_settings
from discussion_moderation.models import (
    Comment,
    CourseContext,
    DiscussionThread,
)
from discussion_moderation.tools.protocols import LMSBackend


class OpenEdXBackend(LMSBackend):
    """Open edX LMS backend.

    Makes HTTP calls to the internal forum service (/api/v2/) using
    JWT authentication and returns DiscussionThread domain objects.
    Configuration is read from Settings (lms_url, lms_jwt_authentication_token).
    """

    def __init__(self):
        settings = get_settings()
        self.lms_url = settings.lms_url.rstrip("/")
        self._headers: dict[str, str] = {}
        if settings.lms_jwt_authentication_token:
            self._headers["Authorization"] = f"JWT {settings.lms_jwt_authentication_token}"

    async def get_thread(
        self,
        thread_id: str,
    ) -> DiscussionThread:
        """Fetch a thread and its comments from the forum service.

        Calls GET /api/v2/threads/{thread_id}?recursive=true to get
        the thread with all nested comments embedded.

        Args:
            thread_id: Forum thread ID.
            learning_objectives: Course LOs to inject into the thread.
                Not available from the thread API; fetch separately.

        Returns:
            DiscussionThread ready for the facilitation pipeline.

        Raises:
            httpx.HTTPStatusError: If the API returns a 4xx or 5xx.
        """
        url = f"{self.lms_url}/api/v2/threads/{thread_id}"
        async with httpx.AsyncClient(headers=self._headers) as client:
            response = await client.get(url, params={"recursive": "true"})
            response.raise_for_status()

        data = response.json()
        return DiscussionThread(
            id=data["id"],
            course_id=data["course_id"],
            title=data["title"],
            body=data["body"],
            author=data["author_username"],
            created_at=data["created_at"],
            last_activity_at=data.get("updated_at"),
            thread_type=data.get("thread_type", "discussion"),
            closed=data.get("closed", False),
            has_endorsed=data.get("endorsed", False),
            comments=[
                self.parse_comment(comment) for comment in data.get("children", [])
            ],
        )

    def parse_comment(self, data: dict) -> Comment:
        """Parse a comment dict from the API into a Comment domain object."""
        return Comment(
            author=data["author_username"],
            body=data["body"],
            created_at=data["created_at"],
            endorsed=data.get("endorsed", False),
            abuse_flagged=data.get("abuse_flagged", False),
            vote_count=data.get("votes", {}).get("point", 0),
            replies=[
                self.parse_comment(reply) for reply in data.get("children", [])
            ],
        )
