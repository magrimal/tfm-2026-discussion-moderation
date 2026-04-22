"""Stub LMS backend for offline development and testing."""

from discussion_moderation.models import DiscussionThread
from discussion_moderation.tools.protocols import LMSBackend


class StubLMSBackend(LMSBackend, key="stub"):
    """LMS backend that serves threads from an in-memory dict.

    Use when running the pipeline without a live LMS. Populate via
    the constructor or register() before calling get_thread().

    Registered as lms_backend="stub" in settings.
    """

    def __init__(self, threads: dict[str, DiscussionThread] | None = None):
        self._threads: dict[str, DiscussionThread] = threads or {}

    def register(self, thread: DiscussionThread) -> None:
        """Add or replace a thread in the store."""
        self._threads[thread.id] = thread

    async def get_thread(self, thread_id: str) -> DiscussionThread:
        try:
            return self._threads[thread_id]
        except KeyError:
            available = list(self._threads)
            raise KeyError(
                f"StubLMSBackend: thread '{thread_id}' not registered. "
                f"Available: {available}"
            ) from None
