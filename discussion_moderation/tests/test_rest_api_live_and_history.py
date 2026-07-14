"""Tests for live-run and intervention-history REST endpoints."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from fastapi.testclient import TestClient

from discussion_moderation.rest_api import router
from discussion_moderation.rest_api.main import create_app
from discussion_moderation.tools.history import (
    InMemoryThreadStore,
    InterventionRecord,
)


def _read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_trigger_live_run_closed_thread_returns_noop(tmp_path, monkeypatch):
    class FakeLMSBackend:
        async def get_thread(self, thread_id: str):
            from discussion_moderation.models import DiscussionThread

            return DiscussionThread(
                id=thread_id,
                course_id="course-v1:TestX+TST+2026",
                title="Closed thread",
                body="",
                author="instructor",
                created_at=datetime.now(UTC),
                comments=[],
                closed=True,
            )

    def _fail_if_called(_thread_id: str):
        raise AssertionError(
            "facilitate_and_post should not run for closed threads"
        )

    from discussion_moderation.evals import store as evals_store

    monkeypatch.setattr(evals_store, "RESULTS_DIR", tmp_path)
    monkeypatch.setattr(router, "RESULTS_DIR", tmp_path)
    monkeypatch.setattr(
        router.LMSBackend,
        "for_key",
        lambda _key: FakeLMSBackend(),
    )
    monkeypatch.setattr(router, "facilitate_and_post", _fail_if_called)

    client = TestClient(create_app())
    response = client.post(
        "/api/runs/live/trigger",
        json={"thread_id": "thread-closed", "run_name": "noop-live"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "noop"
    assert body["thread_id"] == "thread-closed"

    manifest_path = tmp_path / body["run_id"] / "run_manifest.json"
    manifest = _read_json(manifest_path)
    assert manifest["run_type"] == "live"
    assert manifest["status"] == "noop"


def test_get_thread_history_returns_records(monkeypatch):
    from discussion_moderation.constants import FacilitationRole

    store = InMemoryThreadStore()
    store.record_intervention(
        "thread-1",
        InterventionRecord(
            thread_id="thread-1",
            timestamp=datetime(2026, 5, 20, 10, 0, tzinfo=UTC),
            role=FacilitationRole.SOCIAL,
            technique="Redistribute Attention",
            reasoning="Re-engage silent participants.",
            response_text="What do others think?",
        ),
    )

    monkeypatch.setattr(router, "_resolve_history_store", lambda: store)

    client = TestClient(create_app())
    response = client.get("/api/threads/thread-1/history")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["thread_id"] == "thread-1"
    assert body[0]["role"] == "social"
    assert body[0]["technique"] == "Redistribute Attention"
