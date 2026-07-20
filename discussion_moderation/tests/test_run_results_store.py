"""Tests for pluggable eval run result stores."""

from __future__ import annotations

import json
from pathlib import Path

from discussion_moderation.evals.artifacts import list_eval_runs
from discussion_moderation.evals.models import (
    EvalRunDetail,
    EvalRunManifest,
    EvalRunSummary,
)
from discussion_moderation.evals.store import (
    FilesystemRunResultStore,
    RunResultStore,
    build_models_from_records,
    get_run_result_store,
    normalize_error,
    thread_view,
)


class DummyRunResultStore(RunResultStore, key="dummy"):
    """Test-only store backend used to validate registry resolution."""

    def list_runs(self) -> list[EvalRunSummary]:
        return []

    def get_run(self, run_id: str) -> EvalRunDetail | None:
        return None


def _write_manifest(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_get_run_result_store_resolves_registered_backend():
    store = get_run_result_store("dummy")

    assert isinstance(store, DummyRunResultStore)


def test_list_eval_runs_accepts_explicit_filesystem_store(tmp_path):
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
            "model_count": 1,
            "thread_count": 1,
            "total_runs": 1,
            "completed_runs": 1,
            "error_count": 0,
            "avg_duration_ms": 1800,
            "models": {},
        },
    )

    runs = list_eval_runs(store=FilesystemRunResultStore(results_dir))

    assert len(runs) == 1
    assert runs[0].run_id == "2026-05-07T08-30-demo-manifest"


def test_filesystem_store_save_run_writes_manifest_and_summary(tmp_path):
    store = FilesystemRunResultStore(tmp_path)
    run = EvalRunManifest(
        run_id="run-001",
        run_name="Demo run",
        timestamp="2026-05-20T10:00:00+00:00",
        run_kind="evaluation",
        status="completed",
        model_count=1,
        thread_count=1,
        total_runs=1,
        completed_runs=1,
        error_count=0,
        avg_duration_ms=1500,
        models={},
    )

    store.save_run(run, summary_markdown="# Summary")

    assert (tmp_path / "run-001" / "run_manifest.json").exists()
    assert (tmp_path / "run-001" / "summary.md").read_text(
        encoding="utf-8"
    ) == "# Summary"


def test_normalize_error_returns_none_for_no_error():
    assert normalize_error(None) is None


def test_normalize_error_preserves_real_message():
    assert normalize_error("model returned invalid JSON") == (
        "model returned invalid JSON"
    )


def test_normalize_error_replaces_empty_string_with_fallback():
    """Regression test: str(asyncio.TimeoutError()) is '', and an empty
    string is falsy in Python and JS - every downstream `if thread.error`
    check silently treated "errored with no message" as a success until
    this was fixed (2026-07-20).
    """
    normalized = normalize_error("")

    assert normalized
    assert normalized != ""


def test_thread_view_error_field_is_never_an_empty_string():
    record = {
        "model": "ollama:qwen3.5:27b",
        "thread": "stalled",
        "thread_title": "Stalled thread",
        "duration_seconds": 180.01,
        "error": "",
        "state": None,
    }

    view = thread_view(record)

    assert view.error
    assert view.error != ""


def test_build_models_from_records_counts_empty_string_errors():
    """Regression test for the counting bug: two threads that both fail
    with an empty error message must not be counted as completions.
    """
    records = [
        {
            "model": "ollama:qwen3.5:27b",
            "thread": "stalled",
            "thread_title": "Stalled thread",
            "duration_seconds": 180.01,
            "error": "",
            "state": None,
        },
        {
            "model": "ollama:qwen3.5:27b",
            "thread": "conflictive",
            "thread_title": "Conflictive thread",
            "duration_seconds": 180.01,
            "error": "",
            "state": None,
        },
    ]

    models = build_models_from_records(records)
    model = models["ollama:qwen3.5:27b"]

    assert model.error_count == 2
    assert model.completion_count == 0
