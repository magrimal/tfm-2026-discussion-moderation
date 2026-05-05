"""Protocols and base classes for LMS backend integrations.

CommentContext and DiscussionContext define the minimum interface the
facilitation pipeline requires from any discussion data source.

LMSBackend is the base class for LMS integrations. Subclasses register
themselves by declaring a key= keyword argument and are resolved at
runtime via LMSBackend.for_key(key).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Protocol, runtime_checkable

if TYPE_CHECKING:
    from discussion_moderation.models import DiscussionThread


@runtime_checkable
class CommentContext(Protocol):
    """Minimum interface a comment object must expose to the pipeline."""


@runtime_checkable
class DiscussionContext(Protocol):
    """Minimum interface a thread object must expose to the pipeline."""


class LMSBackend:
    """Base class for LMS backend integrations.

    Subclasses register themselves automatically:

        class MyBackend(LMSBackend, key="myplatform"):
            async def get_thread(self, thread_id: str) -> DiscussionThread:
                ...

    Use LMSBackend.for_key(key) to resolve and instantiate the right
    backend at runtime. Returns None for unregistered keys.
    """

    _registry: ClassVar[dict[str, type[LMSBackend]]] = {}

    def __init_subclass__(cls, key: str = "", **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        if key:
            LMSBackend._registry[key] = cls

    @classmethod
    def for_key(cls, key: str) -> LMSBackend | None:
        """Return an instance of the backend registered under key, or None.

        Args:
            key: Backend identifier, e.g. "openedx" or "stub".

        Returns:
            A new backend instance, or None if the key is not registered.
        """
        backend_cls = cls._registry.get(key)
        if backend_cls is None:
            return None
        return backend_cls()

    async def get_thread(self, thread_id: str) -> DiscussionThread:
        """Fetch a thread and its comments from the LMS.

        Args:
            thread_id: Platform-specific thread ID.

        Returns:
            DiscussionThread ready for the facilitation pipeline.
        """
        raise NotImplementedError

    async def post_comment(
        self,
        thread: DiscussionThread,
        body: str,
        author_id: str,
    ) -> str:
        """Post a facilitation comment on a thread.

        Args:
            thread: The thread to comment on. Carries course_id needed
                by the forum API alongside the thread ID.
            body: Comment text to post.
            author_id: Forum user ID of the account posting the comment.

        Returns:
            The new comment ID assigned by the forum service.
        """
        raise NotImplementedError
