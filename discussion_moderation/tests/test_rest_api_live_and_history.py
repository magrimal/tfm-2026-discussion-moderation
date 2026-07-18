"""Tests for live-run and intervention-history REST endpoints."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from fastapi.testclient import TestClient

from discussion_moderation.api.facilitation import FacilitationOutcome
from discussion_moderation.config import Settings
from discussion_moderation.constants import (
    ActionCategory,
    DiscourseQuality,
    DiscussionState,
    DiscussionTrajectory,
    FacilitationRole,
    InquiryPhase,
    ParticipationBalance,
)
from discussion_moderation.models import (
    ClassificationResult,
    FacilitationResponse,
    InterventionDecision,
    PipelineResult,
    RoleSelection,
)
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


def test_trigger_live_run_persists_thread_snapshot(tmp_path, monkeypatch):
    class FakeLMSBackend:
        async def get_thread(self, thread_id: str):
            from discussion_moderation.models import Comment, DiscussionThread

            return DiscussionThread(
                id=thread_id,
                course_id="course-v1:TestX+TST+2026",
                title="Live thread",
                body="Opening post body",
                author="learner-1",
                created_at=datetime.now(UTC),
                comments=[
                    Comment(
                        author="learner-2",
                        body="First reply",
                        created_at=datetime.now(UTC),
                    )
                ],
                closed=False,
            )

    async def _fake_facilitate_and_post(_thread_id: str):
        return FacilitationOutcome(
            result=PipelineResult(
                classification=ClassificationResult(
                    state=DiscussionState.ACTIVE,
                    trajectory=DiscussionTrajectory.STABLE,
                    participation_balance=ParticipationBalance.DISTRIBUTED,
                    discourse_quality=DiscourseQuality.SUBSTANTIVE,
                    inquiry_phase=InquiryPhase.EXPLORATION,
                    reasoning="Looks healthy.",
                    confidence=0.9,
                ),
                intervention=InterventionDecision(
                    should_intervene=True,
                    reasoning="Needs a nudge.",
                    confidence=0.8,
                ),
                role_selection=RoleSelection(
                    role=FacilitationRole.SOCIAL,
                    reasoning="Invite wider participation.",
                    confidence=0.7,
                ),
                response=FacilitationResponse(
                    response_text="What do others think?",
                    technique_used="Redistribute Attention",
                    action_category=ActionCategory.SOCIAL,
                    confidence=0.68,
                    reasoning="Encourage quieter participants.",
                    post_to_thread=True,
                ),
                messages=[{"role": "user", "content": "demo"}],
            ),
            comment_posted=False,
        )

    from discussion_moderation.evals import store as evals_store

    monkeypatch.setattr(evals_store, "RESULTS_DIR", tmp_path)
    monkeypatch.setattr(router, "RESULTS_DIR", tmp_path)
    monkeypatch.setattr(
        router.LMSBackend,
        "for_key",
        lambda _key: FakeLMSBackend(),
    )
    monkeypatch.setattr(router, "facilitate_and_post", _fake_facilitate_and_post)
    monkeypatch.setattr(
        router,
        "get_settings",
        lambda: Settings(
            lms_backend="openedx",
            llm_model="provider:model-a",
            lms_url="http://localhost:18000",
        ),
    )

    client = TestClient(create_app())
    response = client.post(
        "/api/runs/live/trigger",
        json={"thread_id": "thread-live", "run_name": "live-review"},
    )

    assert response.status_code == 200
    body = response.json()
    manifest_path = tmp_path / body["run_id"] / "run_manifest.json"
    manifest = _read_json(manifest_path)
    thread = manifest["models"]["provider:model-a"]["threads"]["thread-live"]
    assert thread["thread_body"] == "Opening post body"
    assert thread["thread_comments"][0]["body"] == "First reply"
    assert thread["thread_url"] == (
        "http://localhost:18000/courses/course-v1:TestX+TST+2026/"
        "discussion/posts/thread-live"
    )


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


def test_get_thread_detail_returns_full_discussion(monkeypatch):
    class FakeLMSBackend:
        async def get_thread(self, thread_id: str):
            from discussion_moderation.models import Comment, DiscussionThread

            return DiscussionThread(
                id=thread_id,
                course_id="course-v1:TestX+TST+2026",
                title="Live thread",
                body="Opening post body",
                author="learner-1",
                created_at=datetime.now(UTC),
                comments=[
                    Comment(
                        author="learner-2",
                        body="Top-level reply",
                        created_at=datetime.now(UTC),
                        replies=[
                            Comment(
                                author="learner-3",
                                body="Nested reply",
                                created_at=datetime.now(UTC),
                            )
                        ],
                    )
                ],
            )

    monkeypatch.setattr(
        router.LMSBackend,
        "for_key",
        lambda _key: FakeLMSBackend(),
    )

    client = TestClient(create_app())
    response = client.get("/api/threads/thread-123")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == "thread-123"
    assert body["title"] == "Live thread"
    assert body["body"] == "Opening post body"
    assert len(body["comments"]) == 2
    assert body["comments"][0]["body"] == "Top-level reply"
    assert body["comments"][0]["depth"] == 0
    assert body["comments"][1]["body"] == "Nested reply"
    assert body["comments"][1]["depth"] == 1
