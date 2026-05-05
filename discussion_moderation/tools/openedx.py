"""Open edX LMS backend implementation."""

import httpx

from discussion_moderation.config import get_settings
from discussion_moderation.models import (
    Comment,
    DiscussionThread,
)
from discussion_moderation.tools.protocols import LMSBackend


class OpenEdXBackend(LMSBackend, key="openedx"):
    """Open edX LMS backend.

    The forum Django app is installed in the LMS, so all /api/v2/ calls
    go to lms_url. JWT authentication is required.
    Configuration is read from Settings (lms_url,
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

        Calls GET /api/v2/threads/{thread_id}?recursive=true to get
        the thread with all nested comments embedded.

        Args:
            thread_id: Forum thread ID.

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
            comments=[self.parse_comment(c) for c in data.get("children", [])],
        )

    async def post_comment(
        self,
        thread: DiscussionThread,
        body: str,
        author_id: str,
    ) -> str:
        """Post a facilitation comment on a thread.

        Calls POST /api/v2/threads/{thread_id}/comments with JWT auth.

        Args:
            thread: Thread to comment on (provides id and course_id).
            body: Comment text to post.
            author_id: Forum user ID of the account posting the comment.

        Returns:
            The new comment ID assigned by the forum service.

        Raises:
            httpx.HTTPStatusError: If the API returns a 4xx or 5xx.
        """
        url = f"{self.lms_url}/api/v2/threads/{thread.id}/comments"
        payload = {
            "body": body,
            "course_id": thread.course_id,
            "author_id": author_id,
        }
        async with httpx.AsyncClient(headers=self._headers) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
        return str(response.json()["id"])

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
