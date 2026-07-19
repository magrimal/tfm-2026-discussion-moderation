"""Tests for cooperative cancellation paths in run_experiment.

Three paths are covered:

1. Pre-call check: when status is "cancelling" at the top of an
   iteration, the run stops before calling _run_once.

2. Post-call check: when status flips to "cancelling" while _run_once
   executes, the post-call check catches it without overwriting the
   "cancelling" status via write_run_manifest(status="running").

3. Final status: after cancellation, the finally block writes
   status="cancelled", not "partial" or "running".
"""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from discussion_moderation.evals.eval_models import RunRecord, run_experiment
from discussion_moderation.evals.models import EvalRunDetail, EvalRunManifest


def _make_record(model: str = "test:m", thread: str = "th") -> RunRecord:
    """Minimal RunRecord with no error."""
    return RunRecord(
        model=model,
        thread=thread,
        thread_title="Test thread",
        state="active",
        trajectory="stable",
        participation_balance="distributed",
        discourse_quality="substantive",
        inquiry_phase="exploration",
        classification_reasoning="ok",
        should_intervene=False,
        intervention_reasoning="no",
        role=None,
        role_reasoning=None,
        classification_confidence=0.9,
        intervention_confidence=0.8,
        role_confidence=None,
        technique=None,
        action_category=None,
        response_confidence=None,
        post_to_thread=None,
        response_reasoning=None,
        response_text=None,
        error=None,
        raw_response=None,
        duration_seconds=0.1,
    )


def _make_detail(status: str) -> EvalRunDetail:
    """Minimal EvalRunDetail with the given status."""
    return EvalRunDetail(
        run_id="test-run",
        run_name="test-run",
        timestamp="2026-07-19T00:00:00+00:00",
        run_kind="evaluation",
        status=status,
        models={},
        summary_markdown=None,
    )


def _make_manifest(status: str = "running") -> EvalRunManifest:
    """Minimal EvalRunManifest with the given status."""
    return EvalRunManifest(
        run_id="test-run",
        run_name="test-run",
        timestamp="2026-07-19T00:00:00+00:00",
        run_kind="evaluation",
        status=status,
        model_count=2,
        thread_count=1,
        total_runs=2,
        completed_runs=0,
        error_count=0,
        avg_duration_ms=0,
        models={},
    )


def _make_store(get_run_responses: list[EvalRunDetail | None]) -> MagicMock:
    """Build a mock RunResultStore with canned get_run responses."""
    store = MagicMock()
    store.get_run.side_effect = get_run_responses
    store.save_run.return_value = None
    store.cancel_run.return_value = "cancelling"
    return store


def _run(coro):
    """Run a coroutine synchronously."""
    return asyncio.run(coro)


def test_pre_call_check_stops_run_before_llm_call(tmp_path):
    """Cancelling at iteration start prevents _run_once from being called."""
    out_dir = tmp_path / "2026-07-19T00-00-pre-call"
    store = _make_store([
        _make_detail("running"),    # top-of-iter, model-a: proceed
        _make_detail("cancelling"), # top-of-iter, model-b: stop
    ])

    with (
        patch(
            "discussion_moderation.evals.eval_models.validate_openrouter_models",
            new=AsyncMock(side_effect=lambda m, *_: m),
        ),
        patch(
            "discussion_moderation.evals.eval_models._run_once",
            new=AsyncMock(return_value=_make_record("test:m-a", "active")),
        ) as mock_run_once,
    ):
        records = _run(run_experiment(
            models=["test:m-a", "test:m-b"],
            threads=["active"],
            out_dir=out_dir,
            result_store=store,
            delay_seconds=0.0,
        ))

    # Cancelling detected before model-b; only model-a ran
    assert mock_run_once.call_count == 1
    assert len(records) == 1


def test_post_call_check_stops_run_without_overwriting_cancelling(tmp_path):
    """Post-call check detects 'cancelling' without overwriting it.

    Covers the bug where write_run_manifest(status="running") was called
    unconditionally after _run_once, destroying the cancelling signal.
    """
    out_dir = tmp_path / "2026-07-19T00-00-post-call"

    # get_run sequence: pre-call check for model-a returns "running" (proceed),
    # post-call check returns "cancelling" (trigger the fix).
    store = _make_store([
        _make_detail("running"),
        _make_detail("cancelling"),
    ])

    with (
        patch(
            "discussion_moderation.evals.eval_models.validate_openrouter_models",
            new=AsyncMock(side_effect=lambda m, *_: m),
        ),
        patch(
            "discussion_moderation.evals.eval_models._run_once",
            new=AsyncMock(return_value=_make_record("test:m-a", "active")),
        ) as mock_run_once,
    ):
        _run(run_experiment(
            models=["test:m-a", "test:m-b"],
            threads=["active"],
            out_dir=out_dir,
            result_store=store,
            delay_seconds=0.0,
        ))

    assert mock_run_once.call_count == 1

    # No save_run call after post-call detection should carry "running"
    # (index 0 is the initial manifest write before the loop)
    statuses = [
        c.args[0].status if c.args else c.kwargs["run"].status
        for c in store.save_run.call_args_list[1:]
    ]
    assert "running" not in statuses, (
        "write_run_manifest must not overwrite 'cancelling' with 'running'"
    )


def test_final_status_is_cancelled_after_cancellation(tmp_path):
    """Finally block writes status='cancelled' after cancellation."""
    out_dir = tmp_path / "2026-07-19T00-00-final-status"
    store = _make_store([
        _make_detail("running"),
        _make_detail("cancelling"),
    ])

    with (
        patch(
            "discussion_moderation.evals.eval_models.validate_openrouter_models",
            new=AsyncMock(side_effect=lambda m, *_: m),
        ),
        patch(
            "discussion_moderation.evals.eval_models._run_once",
            new=AsyncMock(return_value=_make_record("test:m-a", "active")),
        ),
    ):
        _run(run_experiment(
            models=["test:m-a", "test:m-b"],
            threads=["active"],
            out_dir=out_dir,
            result_store=store,
            delay_seconds=0.0,
        ))

    last_call = store.save_run.call_args_list[-1]
    manifest = last_call.args[0] if last_call.args else last_call.kwargs["run"]
    assert manifest.status == "cancelled"


def test_filesystem_post_call_check_stops_run(tmp_path):
    """Filesystem fallback: post-call load_manifest detects cancelling."""
    out_dir = tmp_path / "2026-07-19T00-00-fs-cancel"

    with (
        patch(
            "discussion_moderation.evals.eval_models.validate_openrouter_models",
            new=AsyncMock(side_effect=lambda m, *_: m),
        ),
        patch(
            "discussion_moderation.evals.eval_models._run_once",
            new=AsyncMock(return_value=_make_record("test:m-a", "active")),
        ) as mock_run_once,
        patch(
            "discussion_moderation.evals.eval_models.load_manifest",
            side_effect=[
                _make_manifest("running"),    # pre-call check
                _make_manifest("cancelling"), # post-call check
            ],
        ),
        patch("discussion_moderation.evals.eval_models.write_run_manifest"),
        patch(
            "discussion_moderation.evals.eval_models._write_summary",
            side_effect=lambda d, *_: (d / "summary.md").write_text(
                "", encoding="utf-8"
            ),
        ),
    ):
        _run(run_experiment(
            models=["test:m-a", "test:m-b"],
            threads=["active"],
            out_dir=out_dir,
            result_store=None,
            delay_seconds=0.0,
        ))

    assert mock_run_once.call_count == 1
