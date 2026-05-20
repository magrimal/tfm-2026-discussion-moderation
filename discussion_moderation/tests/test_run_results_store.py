"""Tests for pluggable eval run result stores."""

from __future__ import annotations

import json
from pathlib import Path

from discussion_moderation.evals.artifacts import (
    EvalRunDetail,
    EvalRunSummary,
    FilesystemRunResultStore,
    MongoRunResultStore,
    RunResultStore,
    get_run_result_store,
    list_eval_runs,
)


class DummyRunResultStore(RunResultStore, key="dummy"):
    """Test-only store backend used to validate registry resolution."""

    def list_runs(self) -> list[EvalRunSummary]:
        return []

    def get_run(self, run_id: str) -> EvalRunDetail | None:
        return None


def _write_manifest(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


class FakeMongoCollection:
    """Simple in-memory stand-in for a Mongo collection in tests."""

    def __init__(self, docs: list[dict[str, object]]) -> None:
        self._docs = docs

    def find(self, _query: dict[str, object]) -> list[dict[str, object]]:
        return list(self._docs)

    def find_one(self, query: dict[str, object]) -> dict[str, object] | None:
        or_filters = query.get("$or", [])
        for doc in self._docs:
            for entry in or_filters:
                if "run_id" in entry and doc.get("run_id") == entry["run_id"]:
                    return dict(doc)
                if "_id" in entry and doc.get("_id") == entry["_id"]:
                    return dict(doc)
        return None


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


def test_mongo_store_lists_runs_from_documents():
    collection = FakeMongoCollection(
        [
            {
                "run_id": "2026-05-09T09-00-demo",
                "run_name": "demo",
                "timestamp": "2026-05-09T09:00:00+00:00",
                "run_kind": "evaluation",
                "status": "completed",
                "model_count": 1,
                "thread_count": 1,
                "total_runs": 1,
                "completed_runs": 1,
                "error_count": 0,
                "avg_duration_ms": 1700,
                "models": {},
                "summary_markdown": "# demo",
            }
        ]
    )
    store = MongoRunResultStore(mongo_collection=collection)

    runs = store.list_runs()

    assert len(runs) == 1
    assert runs[0].run_id == "2026-05-09T09-00-demo"
    assert runs[0].summary_available is True


def test_mongo_store_get_run_returns_detail_with_summary_markdown():
    collection = FakeMongoCollection(
        [
            {
                "run_id": "2026-05-09T09-00-demo",
                "run_name": "demo",
                "timestamp": "2026-05-09T09:00:00+00:00",
                "run_kind": "evaluation",
                "status": "completed",
                "model_count": 1,
                "thread_count": 1,
                "total_runs": 1,
                "completed_runs": 1,
                "error_count": 0,
                "avg_duration_ms": 1700,
                "models": {},
                "summary_markdown": "# demo",
            }
        ]
    )
    store = MongoRunResultStore(mongo_collection=collection)

    run = store.get_run("2026-05-09T09-00-demo")

    assert run is not None
    assert run.run_id == "2026-05-09T09-00-demo"
    assert run.summary_markdown == "# demo"
