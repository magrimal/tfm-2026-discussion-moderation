"""Abstract LMS backend interface.

Defines the protocol that all LMS backend implementations must
follow. The facilitation system is vendor-neutral; Open edX is
the proof of concept, but any backend implementing this protocol
can be used.
"""

from typing import Protocol, runtime_checkable

from discussion_moderation.models import Comment, CourseContext


@runtime_checkable
class LMSBackend(Protocol):
    """Protocol for LMS backend integrations.

    Description:
        Defines the interface for retrieving course and
        participant data from a learning management system.
        Implementations handle the specifics of each platform's
        API (Open edX, Moodle, etc.).
    """

    async def get_course_context(
        self,
        course_id: str,
    ) -> CourseContext:
        """Retrieve course context for prompt parameterization.

        Args:
            course_id: Platform-specific course identifier.

        Returns:
            CourseContext with course metadata.
        """
        ...

    async def get_participant_history(
        self,
        course_id: str,
        user_id: str,
    ) -> list[Comment]:
        """Retrieve a participant's recent discussion posts.

        Args:
            course_id: Platform-specific course identifier.
            user_id: Platform-specific user identifier.

        Returns:
            List of the participant's recent posts.
        """
        ...

    async def get_course_materials(
        self,
        course_id: str,
        topic: str,
    ) -> list[str]:
        """Retrieve course materials relevant to a topic.

        Args:
            course_id: Platform-specific course identifier.
            topic: The topic to search materials for.

        Returns:
            List of relevant material excerpts or references.
        """
        ...

    async def flag_content(
        self,
        post_id: str,
        reason: str,
    ) -> None:
        """Flag a post for instructor review.

        Called by ModeratorAgent when content requires human
        review rather than (or in addition to) automated
        facilitation.

        Args:
            post_id: Platform-specific identifier of the post.
            reason: Human-readable explanation for the flag.
        """
        ...
