"""Public API for reading and writing eval run artifacts.

External callers should import from this module. Store backends and
parsing helpers live in discussion_moderation.evals.store.
"""

from __future__ import annotations

import json
from pathlib import Path

from discussion_moderation.evals.models import (
    EvalRunDetail,
    EvalRunManifest,
    EvalRunSummary,
)
from discussion_moderation.evals.store import (
    RESULTS_DIR,
    RunResultStore,
    build_models_from_records,
    get_run_result_store,
    load_manifest,
    manifest_path,
)


def write_run_manifest(
    run_dir: Path,
    *,
    run_id: str,
    run_name: str,
    timestamp: str,
    records: list[dict[str, object]],
    run_type: str = "experiment",
    run_kind: str = "evaluation",
    status: str = "completed",
    progress_message: str | None = None,
    expected_model_count: int | None = None,
    expected_thread_count: int | None = None,
    expected_total_runs: int | None = None,
    store: RunResultStore | None = None,
    summary_markdown: str | None = None,
) -> Path:
    """Persist a single run document alongside raw run artifacts."""
    models = build_models_from_records(records)
    durations = [
        model.avg_duration_ms
        for model in models.values()
        if model.total_threads
    ]
    discovered_thread_count = len(
        {
            thread_key
            for model in models.values()
            for thread_key in model.threads
        }
    )
    discovered_total_runs = sum(
        model.total_threads for model in models.values()
    )
    manifest = EvalRunManifest(
        run_id=run_id,
        run_name=run_name,
        timestamp=timestamp,
        run_type=run_type,
        run_kind=run_kind,
        status=status,
        progress_message=progress_message,
        model_count=(
            expected_model_count
            if expected_model_count is not None
            else len(models)
        ),
        thread_count=(
            expected_thread_count
            if expected_thread_count is not None
            else discovered_thread_count
        ),
        total_runs=(
            expected_total_runs
            if expected_total_runs is not None
            else discovered_total_runs
        ),
        completed_runs=sum(model.completion_count for model in models.values()),
        error_count=sum(model.error_count for model in models.values()),
        avg_duration_ms=(
            (sum(durations) // len(durations)) if durations else 0
        ),
        models=models,
    )
    manifest_path_obj = manifest_path(run_dir)
    manifest_path_obj.write_text(
        manifest.model_dump_json(indent=2),
        encoding="utf-8",
    )
    if store is not None:
        store.save_run(manifest, summary_markdown=summary_markdown)
    return manifest_path_obj


def list_eval_runs(
    store: RunResultStore | None = None,
) -> list[EvalRunSummary]:
    """Return discovered historical runs from the configured result store."""
    selected_store = store or get_run_result_store()
    return selected_store.list_runs()


def mark_interrupted_runs(
    results_dir: Path = RESULTS_DIR,
    store: RunResultStore | None = None,
) -> None:
    """Mark any runs left in 'running' state as 'interrupted'.

    Called at service startup to clean up runs that were in progress
    when the service was killed or restarted. If store is provided,
    the updated manifest is also written to the remote store.
    """
    if not results_dir.exists():
        return
    for run_dir in results_dir.iterdir():
        if not run_dir.is_dir():
            continue
        manifest = load_manifest(run_dir)
        if manifest is None or manifest.status != "running":
            continue
        mp = manifest_path(run_dir)
        data = json.loads(mp.read_text(encoding="utf-8"))
        data["status"] = "interrupted"
        data["progress_message"] = "Run interrupted — service was restarted."
        mp.write_text(json.dumps(data, indent=2), encoding="utf-8")
        if store is not None:
            updated = load_manifest(run_dir)
            if updated is not None:
                store.save_run(updated)


def get_eval_run(
    run_id: str,
    store: RunResultStore | None = None,
) -> EvalRunDetail | None:
    """Return grouped model/thread data for one historical run."""
    selected_store = store or get_run_result_store()
    return selected_store.get_run(run_id)
