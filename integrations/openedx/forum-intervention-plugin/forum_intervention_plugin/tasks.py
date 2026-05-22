"""Celery tasks for the Forum Intervention Plugin."""

import logging

import httpx
from celery import shared_task
from django.conf import settings

log = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=0)
def facilitate_thread(self, thread_id):
    """Call the facilitation service for the given thread ID.

    Makes a synchronous HTTP POST to the facilitation service endpoint.
    Failures are logged but not retried — a missed facilitation is
    preferable to blocking or retrying indefinitely.

    Args:
        thread_id: Forum thread ID to facilitate.
    """
    url = getattr(settings, "FACILITATION_SERVICE_URL", "")
    if not url:
        log.warning(
            "FACILITATION_SERVICE_URL is not set; skipping thread %s", thread_id
        )
        return
    response = httpx.post(
        f"{url}/facilitate/thread/{thread_id}",
        timeout=120,
    )
    response.raise_for_status()
    log.info(
        "Facilitation for thread %s completed: %s", thread_id, response.json()
    )
