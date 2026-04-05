"""Open edX LMS backend implementation.

Stub implementation for the proof of concept. Will be connected
to Open edX APIs (forum IDA, course API) in a future phase.
"""

from discussion_moderation.models import Comment, CourseContext
from discussion_moderation.tools.protocols import LMSBackend


class OpenEdXBackend(LMSBackend):
    """Open edX LMS backend (stub).

    Description:
        Proof-of-concept implementation of the LMSBackend
        protocol for Open edX. Returns placeholder data until
        connected to the actual Open edX APIs (forum IDA for
        discussion data, course API for course metadata).

    Attributes:
        base_url: The Open edX instance URL.
    """

    def __init__(self, base_url: str = "http://localhost:18000"):
        self.base_url = base_url

    async def get_course_context(
        self,
        course_id: str,
    ) -> CourseContext:
        """Retrieve course context from Open edX.

        Args:
            course_id: Open edX course key
                (e.g., "course-v1:UCM+TFM+2026").

        Returns:
            CourseContext with course metadata.
        """
        # TODO: connect to Open edX course API
        return CourseContext(
            course_id=course_id,
            display_name=f"Course {course_id}",
            module_topic="Discussion module",
            audience_level="undergraduate",
            language="en",
        )

    async def get_participant_history(
        self,
        course_id: str,
        user_id: str,
    ) -> list[Comment]:
        """Retrieve participant's posts from Open edX forum.

        Args:
            course_id: Open edX course key.
            user_id: Open edX username.

        Returns:
            List of the participant's recent posts.
        """
        # TODO: connect to Open edX forum IDA
        return []

    async def get_course_materials(
        self,
        course_id: str,
        topic: str,
    ) -> list[str]:
        """Retrieve course materials from Open edX.

        Args:
            course_id: Open edX course key.
            topic: The topic to search materials for.

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
