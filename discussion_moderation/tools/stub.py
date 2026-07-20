"""Stub LMS backend for offline development and testing."""

from discussion_moderation.models import (
    CourseContext,
    DiscussionThread,
    ThreadSummary,
)
from discussion_moderation.tools.protocols import LMSBackend


class StubLMSBackend(LMSBackend, key="stub"):
    """LMS backend that serves threads from an in-memory dict.

    Use when running the pipeline without a live LMS. Populate via
    the constructor or register() before calling get_thread().
    Comments posted via post_comment() are stored in posted_comments
    for inspection in tests.

    Registered as lms_backend="stub" in settings.
    """

    def __init__(self, threads: dict[str, DiscussionThread] | None = None):
        self._threads: dict[str, DiscussionThread] = threads or {}
        self.posted_comments: list[dict] = []
        self.flagged_content: list[dict] = []

    def register(self, thread: DiscussionThread) -> None:
        """Add or replace a thread in the store."""
        self._threads[thread.id] = thread

    async def get_thread(self, thread_id: str) -> DiscussionThread:
        """Return the thread registered under thread_id."""
        try:
            return self._threads[thread_id]
        except KeyError:
            available = list(self._threads)
            raise KeyError(
                f"StubLMSBackend: thread '{thread_id}' not registered. "
                f"Available: {available}"
            ) from None

    async def post_comment(
        self,
        thread: DiscussionThread,
        body: str,
        author_id: str,
    ) -> str:
        """Store a posted comment and return a deterministic fake ID."""
        comment_id = f"stub-comment-{len(self.posted_comments)}"
        self.posted_comments.append(
            {
                "id": comment_id,
                "thread_id": thread.id,
                "course_id": thread.course_id,
                "body": body,
                "author_id": author_id,
            }
        )
        return comment_id

    async def list_threads(self, course_id: str) -> list[ThreadSummary]:
        """Return summaries of threads registered under the given course_id."""
        return [
            ThreadSummary(
                id=t.id,
                course_id=t.course_id,
                title=t.title,
                body=t.body,
                author=t.author,
                comment_count=len(t.comments),
            )
            for t in self._threads.values()
            if t.course_id == course_id
        ]

    async def get_course_context(self, course_id: str) -> CourseContext:
        """Return a minimal stub course context."""
        return CourseContext(
            course_id=course_id,
            display_name="Stub Course",
        )

    async def flag_content(self, post_id: str, reason: str) -> None:
        """Record a flagged post for inspection in tests."""
        self.flagged_content.append({"post_id": post_id, "reason": reason})
