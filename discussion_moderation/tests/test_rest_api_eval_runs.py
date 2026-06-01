"""Tests for read-only run API endpoints backed by eval artifacts."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from discussion_moderation.evals import artifacts
from discussion_moderation.rest_api.main import create_app


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def _write_manifest(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_list_runs_returns_aggregated_run_summaries(tmp_path, monkeypatch):
    results_dir = tmp_path / "results"
    run_dir = results_dir / "2026-05-05T10-00-demo-run"
    run_dir.mkdir(parents=True)
    _write_json(
        run_dir / "provider_model-a__active.json",
        {
            "model": "provider:model-a",
            "thread": "active",
            "thread_title": "Active thread",
            "state": "active",
            "trajectory": "stable",
            "participation_balance": "distributed",
            "discourse_quality": "substantive",
            "inquiry_phase": "exploration",
            "classification_reasoning": "Looks healthy.",
            "should_intervene": False,
            "intervention_reasoning": "No intervention needed.",
            "role": None,
            "role_reasoning": None,
            "classification_confidence": 0.91,
            "intervention_confidence": 0.82,
            "role_confidence": None,
            "technique": None,
            "action_category": None,
            "response_confidence": None,
            "post_to_thread": None,
            "response_reasoning": None,
            "response_text": None,
            "error": None,
            "raw_response": None,
            "duration_seconds": 2.5,
        },
    )
    _write_json(
        run_dir / "provider_model-b__stalled.json",
        {
            "model": "provider:model-b",
            "thread": "stalled",
            "thread_title": "Stalled thread",
            "state": None,
            "trajectory": None,
            "participation_balance": None,
            "discourse_quality": None,
            "inquiry_phase": None,
            "classification_reasoning": None,
            "should_intervene": None,
            "intervention_reasoning": None,
            "role": None,
            "role_reasoning": None,
            "classification_confidence": None,
            "intervention_confidence": None,
            "role_confidence": None,
            "technique": None,
            "action_category": None,
            "response_confidence": None,
            "post_to_thread": None,
            "response_reasoning": None,
            "response_text": None,
            "error": "validation failed",
            "raw_response": None,
            "duration_seconds": 4,
        },
    )
    (run_dir / "summary.md").write_text("# Demo summary\n", encoding="utf-8")
    monkeypatch.setattr(artifacts, "RESULTS_DIR", results_dir)

    client = TestClient(create_app())

    response = client.get("/runs")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["run_id"] == "2026-05-05T10-00-demo-run"
    assert body[0]["run_name"] == "demo-run"
    assert body[0]["run_kind"] == "evaluation"
    assert body[0]["model_count"] == 2
    assert body[0]["thread_count"] == 2
    assert body[0]["total_runs"] == 2
    assert body[0]["completed_runs"] == 1
    assert body[0]["error_count"] == 1
    assert body[0]["avg_duration_ms"] == 3250
    assert body[0]["summary_available"] is True


def test_get_run_returns_grouped_model_thread_results(tmp_path, monkeypatch):
    results_dir = tmp_path / "results"
    run_dir = results_dir / "2026-05-05T10-00-demo-run"
    run_dir.mkdir(parents=True)
    _write_json(
        run_dir / "provider_model-a__active.json",
        {
            "model": "provider:model-a",
            "thread": "active",
            "thread_title": "Active thread",
            "state": "active",
            "trajectory": "stable",
            "participation_balance": "distributed",
            "discourse_quality": "substantive",
            "inquiry_phase": "exploration",
            "classification_reasoning": "Looks healthy.",
            "should_intervene": True,
            "intervention_reasoning": "Needs a nudge.",
            "role": "social_facilitator",
            "role_reasoning": "Participation is uneven.",
            "classification_confidence": 0.91,
            "intervention_confidence": 0.82,
            "role_confidence": 0.74,
            "technique": "encourage_participation",
            "action_category": "social",
            "response_confidence": 0.68,
            "post_to_thread": True,
            "response_reasoning": "Encourage a quieter student.",
            "response_text": "What do others think?",
            "error": None,
            "raw_response": None,
            "duration_seconds": 2.5,
        },
    )
    (run_dir / "summary.md").write_text("# Demo summary\n", encoding="utf-8")
    monkeypatch.setattr(artifacts, "RESULTS_DIR", results_dir)

    client = TestClient(create_app())

    response = client.get("/runs/2026-05-05T10-00-demo-run")

    assert response.status_code == 200
    body = response.json()
    assert body["run_id"] == "2026-05-05T10-00-demo-run"
    assert body["run_name"] == "demo-run"
    assert body["run_kind"] == "evaluation"
    assert body["summary_markdown"] == "# Demo summary\n"
    model = body["models"]["provider:model-a"]
    assert model["family"] == "provider"
    assert model["size"] == "model-a"
    assert model["completion_count"] == 1
    thread = model["threads"]["active"]
    assert thread["thread_title"] == "Active thread"
    assert thread["classification"]["state"] == "active"
    assert thread["intervention"]["decision"] == "intervene"
    assert thread["response"]["text"] == "What do others think?"
    assert thread["duration_ms"] == 2500


def test_list_runs_prefers_run_manifest_when_present(tmp_path, monkeypatch):
    results_dir = tmp_path / "results"
    run_dir = results_dir / "2026-05-07T08-30-demo-manifest"
    run_dir.mkdir(parents=True)
    _write_manifest(
        run_dir / "run_manifest.json",
        {
            "run_id": "2026-05-07T08-30-demo-manifest",
            "run_name": "demo-manifest",
            "timestamp": "2026-05-07T08:30:00+00:00",
            "run_kind": "evaluation",
            "status": "completed",
            "progress_message": "Finalized",
            "model_count": 1,
            "thread_count": 2,
            "total_runs": 2,
            "completed_runs": 2,
            "error_count": 0,
            "avg_duration_ms": 1800,
            "models": {
                "provider:model-a": {
                    "model_name": "provider:model-a",
                    "family": "provider",
                    "size": "model-a",
                    "threads": {
                        "active": {
                            "thread_key": "active",
                            "thread_title": "Active thread",
                            "expected_state": "active",
                            "classification": {
                                "state": "active",
                                "trajectory": "stable",
                                "participation_balance": "distributed",
                                "discourse_quality": "substantive",
                                "inquiry_phase": "exploration",
                                "reasoning": "Looks healthy.",
                                "confidence": 0.9,
                            },
                            "intervention": {
                                "decision": "no_intervention",
                                "role": None,
                                "technique": None,
                                "post_to_thread": None,
                                "reasoning": "No intervention needed.",
                                "confidence": 0.8,
                            },
                            "role_reasoning": None,
                            "role_confidence": None,
                            "response": None,
                            "duration_ms": 1800,
                            "error": None,
                            "logfuse_url": None,
                        }
                    },
                    "completion_count": 2,
                    "total_threads": 2,
                    "error_count": 0,
                    "avg_duration_ms": 1800,
                }
            },
        },
    )
    (run_dir / "summary.md").write_text(
        "# Manifest summary\n", encoding="utf-8"
    )
    monkeypatch.setattr(artifacts, "RESULTS_DIR", results_dir)

    client = TestClient(create_app())

    response = client.get("/runs")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["run_id"] == "2026-05-07T08-30-demo-manifest"
    assert body[0]["run_name"] == "demo-manifest"
    assert body[0]["completed_runs"] == 2
    assert body[0]["progress_message"] == "Finalized"
    assert body[0]["summary_available"] is True


def test_get_run_reads_from_run_manifest_when_present(tmp_path, monkeypatch):
    results_dir = tmp_path / "results"
    run_dir = results_dir / "2026-05-07T08-30-demo-manifest"
    run_dir.mkdir(parents=True)
    _write_manifest(
        run_dir / "run_manifest.json",
        {
            "run_id": "2026-05-07T08-30-demo-manifest",
            "run_name": "demo-manifest",
            "timestamp": "2026-05-07T08:30:00+00:00",
            "run_kind": "evaluation",
            "status": "completed",
            "progress_message": "Finalized",
            "model_count": 1,
            "thread_count": 1,
            "total_runs": 1,
            "completed_runs": 1,
            "error_count": 0,
            "avg_duration_ms": 1800,
            "models": {
                "provider:model-a": {
                    "model_name": "provider:model-a",
                    "family": "provider",
                    "size": "model-a",
                    "threads": {
                        "active": {
                            "thread_key": "active",
                            "thread_title": "Active thread",
                            "expected_state": "active",
                            "classification": {
                                "state": "active",
                                "trajectory": "stable",
                                "participation_balance": "distributed",
                                "discourse_quality": "substantive",
                                "inquiry_phase": "exploration",
                                "reasoning": "Looks healthy.",
                                "confidence": 0.9,
                            },
                            "intervention": {
                                "decision": "intervene",
                                "role": "social_facilitator",
                                "technique": "encourage_participation",
                                "post_to_thread": True,
                                "reasoning": "Needs a nudge.",
                                "confidence": 0.8,
                            },
                            "role_reasoning": "Participation is uneven.",
                            "role_confidence": 0.7,
                            "response": {
                                "text": "What do others think?",
                                "reasoning": "Encourage a quieter student.",
                                "confidence": 0.68,
                                "action_category": "social",
                            },
                            "duration_ms": 1800,
                            "error": None,
                            "logfuse_url": None,
                        }
                    },
                    "completion_count": 1,
                    "total_threads": 1,
                    "error_count": 0,
                    "avg_duration_ms": 1800,
                }
            },
        },
    )
    (run_dir / "summary.md").write_text(
        "# Manifest summary\n", encoding="utf-8"
    )
    monkeypatch.setattr(artifacts, "RESULTS_DIR", results_dir)

    client = TestClient(create_app())

    response = client.get("/runs/2026-05-07T08-30-demo-manifest")

    assert response.status_code == 200
    body = response.json()
    assert body["run_id"] == "2026-05-07T08-30-demo-manifest"
    assert body["status"] == "completed"
    assert body["progress_message"] == "Finalized"
    assert body["summary_markdown"] == "# Manifest summary\n"
    thread = body["models"]["provider:model-a"]["threads"]["active"]
    assert thread["classification"]["state"] == "active"
    assert thread["intervention"]["decision"] == "intervene"
    assert thread["response"]["text"] == "What do others think?"


def test_get_run_returns_404_for_unknown_run(tmp_path, monkeypatch):
    results_dir = tmp_path / "results"
    results_dir.mkdir(parents=True)
    monkeypatch.setattr(artifacts, "RESULTS_DIR", results_dir)

    client = TestClient(create_app())

    response = client.get("/runs/missing-run")

    assert response.status_code == 404
    assert response.json() == {"detail": "Run not found."}



def test_trigger_run_uses_lms_background_for_non_fixture_threads(
    tmp_path, monkeypatch
):
    called = {"lms": False}

    async def _fake_lms_runner(
        models,
        run_name,
        run_id,
        run_timestamp,
        thread_ids,
        out_dir,
        result_store,
    ):
        called["lms"] = True

    async def _fail_fixture_runner(
        models,
        run_name,
        threads,
        out_dir,
        result_store,
    ):
        raise AssertionError("Fixture runner should not be used")

    monkeypatch.setattr(artifacts, "RESULTS_DIR", tmp_path)
    from discussion_moderation.rest_api import router

    monkeypatch.setattr(router, "RESULTS_DIR", tmp_path)
    monkeypatch.setattr(
        router,
        "_run_lms_experiment_background",
        _fake_lms_runner,
    )
    monkeypatch.setattr(
        router,
        "_run_experiment_background",
        _fail_fixture_runner,
    )

    client = TestClient(create_app())
    response = client.post(
        "/runs/trigger",
        json={
            "run_name": "lms-run",
            "models": ["openrouter:demo/model"],
            "threads": ["external-thread-1"],
        },
    )

    assert response.status_code == 202
    assert called["lms"] is True
