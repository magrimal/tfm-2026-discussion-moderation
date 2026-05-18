"""Tests for read-only run API endpoints backed by eval artifacts."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from discussion_moderation.evals import artifacts
from discussion_moderation.rest_api.main import create_app


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_list_runs_returns_aggregated_run_summaries(
    tmp_path, monkeypatch
):
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


def test_get_run_returns_grouped_model_thread_results(
    tmp_path, monkeypatch
):
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


def test_get_run_returns_404_for_unknown_run(tmp_path, monkeypatch):
    results_dir = tmp_path / "results"
    results_dir.mkdir(parents=True)
    monkeypatch.setattr(artifacts, "RESULTS_DIR", results_dir)

    client = TestClient(create_app())

    response = client.get("/runs/missing-run")

    assert response.status_code == 404
    assert response.json() == {"detail": "Run not found."}