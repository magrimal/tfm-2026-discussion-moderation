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
    get_run_result_store,
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
