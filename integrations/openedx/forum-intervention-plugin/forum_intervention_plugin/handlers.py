"""Signal handlers for forum creation events."""

import logging

from django.conf import settings
from django.dispatch import receiver
from openedx_events.learning.signals import (
    FORUM_RESPONSE_COMMENT_CREATED,
    FORUM_THREAD_CREATED,
    FORUM_THREAD_RESPONSE_CREATED,
)

from .tasks import facilitate_thread

log = logging.getLogger(__name__)


def get_thread_id(thread):
    """Extract the parent thread ID from a DiscussionThreadData object.

    For new threads, thread.id is the thread ID directly. For responses and
    comments, thread.discussion['id'] is the parent thread ID (set by
    edx-platform in track_created_event as {'id': comment.thread_id}).
    """
    if thread.discussion and "id" in thread.discussion:
        return str(thread.discussion["id"])
    return str(thread.id)


@receiver(
    [
        FORUM_THREAD_CREATED,
        FORUM_THREAD_RESPONSE_CREATED,
        FORUM_RESPONSE_COMMENT_CREATED,
    ]
)
def handle_forum_event(sender, thread, **kwargs):
    """Handle forum creation events and dispatch a facilitation task.

    Fires for new threads, responses, and comments. Enqueues a Celery task
    that calls the facilitation service asynchronously so the LMS request
    is not blocked.
    """
    if not getattr(settings, "FACILITATION_SERVICE_ENABLED", True):
        return
    thread_id = get_thread_id(thread)
    log.info("Dispatching facilitation task for thread %s", thread_id)
    facilitate_thread.delay(thread_id)
