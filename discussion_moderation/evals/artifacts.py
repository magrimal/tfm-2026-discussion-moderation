"""Public API for reading and writing eval run artifacts.

External callers should import from this module. Store backends and
parsing helpers live in discussion_moderation.evals.store.
"""

from __future__ import annotations

from pathlib import Path

from discussion_moderation.evals.models import (
    EvalRunDetail,
    EvalRunManifest,
    EvalRunSummary,
)
from discussion_moderation.evals.store import (
    RunResultStore,
    build_models_from_records,
    get_run_result_store,
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
    resolved_store = store or get_run_result_store()
    resolved_store.save_run(manifest, summary_markdown=summary_markdown)
    return manifest_path(run_dir)


def list_eval_runs(
    store: RunResultStore | None = None,
) -> list[EvalRunSummary]:
    """Return discovered historical runs from the configured result store."""
    selected_store = store or get_run_result_store()
    return selected_store.list_runs()


def get_eval_run(
    run_id: str,
    store: RunResultStore | None = None,
) -> EvalRunDetail | None:
    """Return grouped model/thread data for one historical run."""
    selected_store = store or get_run_result_store()
    return selected_store.get_run(run_id)


def mark_interrupted_runs(store: RunResultStore | None = None) -> None:
    """Mark any runs left in 'running' or 'cancelling' state as 'interrupted'.

    Called at service startup to clean up runs that were in progress
    (or being cancelled) when the service was killed or restarted.
    Works against whichever backend is configured (filesystem or S3).
    """
    resolved_store = store or get_run_result_store()
    for summary in resolved_store.list_runs():
        if summary.status not in ("running", "cancelling"):
            continue
        detail = resolved_store.get_run(summary.run_id)
        if detail is None:
            continue
        manifest = EvalRunManifest(
            run_id=summary.run_id,
            run_name=summary.run_name,
            timestamp=summary.timestamp,
            run_type=summary.run_type,
            run_kind=summary.run_kind,
            status="interrupted",
            progress_message="Run interrupted: service was restarted.",
            model_count=summary.model_count,
            thread_count=summary.thread_count,
            total_runs=summary.total_runs,
            completed_runs=summary.completed_runs,
            error_count=summary.error_count,
            avg_duration_ms=summary.avg_duration_ms,
            models=detail.models,
        )
        resolved_store.save_run(manifest)


def cancel_run(
    run_id: str,
    store: RunResultStore | None = None,
) -> str | None:
    """Request cancellation of a running experiment run.

    Patches the manifest status from 'running' to 'cancelling'.
    The background task checks for this flag between LLM calls and
    writes 'cancelled' when it stops.

    Args:
        run_id: The run identifier.
        store: Result store backend. Defaults to the configured store.

    Returns:
        The resulting status string, or None if the run is not found.
    """
    selected_store = store or get_run_result_store()
    return selected_store.cancel_run(run_id)
