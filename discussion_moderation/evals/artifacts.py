"""Helpers for reading persisted run artifacts from eval outputs.

These artifacts currently come from eval/model comparison runs, but the
API surface built on top of them should stay generic enough to support
other run sources later.
"""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path

from pydantic import BaseModel

RESULTS_DIR = Path(__file__).parents[2] / "docs" / "experiments" / "results"
RUN_DIR_PATTERN = re.compile(
    r"^(?P<timestamp>\d{4}-\d{2}-\d{2}T\d{2}-\d{2})(?:-(?P<name>.+))?$"
)


class EvalClassificationView(BaseModel):
    """Classification stage output for one thread run."""

    state: str | None
    trajectory: str | None
    participation_balance: str | None
    discourse_quality: str | None
    inquiry_phase: str | None
    reasoning: str | None
    confidence: float | None


class EvalInterventionView(BaseModel):
    """Intervention stage output for one thread run."""

    decision: str | None
    role: str | None
    technique: str | None
    post_to_thread: bool | None
    reasoning: str | None
    confidence: float | None


class EvalResponseView(BaseModel):
    """Generated facilitation response details."""

    text: str | None
    reasoning: str | None
    confidence: float | None
    action_category: str | None


class EvalThreadResultView(BaseModel):
    """Frontend-shaped view of a single model/thread run."""

    thread_key: str
    thread_title: str
    expected_state: str | None
    classification: EvalClassificationView
    intervention: EvalInterventionView
    role_reasoning: str | None
    role_confidence: float | None
    response: EvalResponseView | None
    duration_ms: int
    error: str | None
    logfuse_url: str | None = None


class EvalModelResultView(BaseModel):
    """Aggregated view for one model across all threads in a run."""

    model_name: str
    family: str | None
    size: str | None
    threads: dict[str, EvalThreadResultView]
    completion_count: int
    total_threads: int
    error_count: int
    avg_duration_ms: int


class EvalRunSummary(BaseModel):
    """Compact run metadata for history views."""

    run_id: str
    run_name: str
    timestamp: str
    run_kind: str
    model_count: int
    thread_count: int
    total_runs: int
    completed_runs: int
    error_count: int
    avg_duration_ms: int
    summary_available: bool


class EvalRunDetail(BaseModel):
    """Detailed run view for a single historical run."""

    run_id: str
    run_name: str
    timestamp: str
    run_kind: str
    models: dict[str, EvalModelResultView]
    summary_markdown: str | None


def _parse_run_dir_name(run_dir: Path) -> tuple[str, str]:
    match = RUN_DIR_PATTERN.match(run_dir.name)
    if not match:
        return run_dir.name, run_dir.name

    timestamp = match.group("timestamp")
    name = match.group("name") or run_dir.name
    parsed = datetime.strptime(timestamp, "%Y-%m-%dT%H-%M").replace(
        tzinfo=UTC
    )
    return parsed.isoformat(), name


def _model_family(model_name: str) -> str | None:
    if ":" not in model_name:
        return None
    return model_name.split(":", maxsplit=1)[0]


def _model_size(model_name: str) -> str | None:
    candidate = model_name.rsplit(":", maxsplit=1)[-1]
    return candidate or None


def _load_record(path: Path) -> dict[str, object]:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def _response_view(record: dict[str, object]) -> EvalResponseView | None:
    has_response = any(
        record.get(field) is not None
        for field in (
            "response_text",
            "response_reasoning",
            "response_confidence",
            "action_category",
        )
    )
    if not has_response:
        return None

    return EvalResponseView(
        text=record.get("response_text"),
        reasoning=record.get("response_reasoning"),
        confidence=record.get("response_confidence"),
        action_category=record.get("action_category"),
    )


def _thread_view(record: dict[str, object]) -> EvalThreadResultView:
    should_intervene = record.get("should_intervene")
    if should_intervene is True:
        decision = "intervene"
    elif should_intervene is False:
        decision = "no_intervention"
    else:
        decision = None

    return EvalThreadResultView(
        thread_key=str(record["thread"]),
        thread_title=str(record.get("thread_title") or record["thread"]),
        expected_state=(
            str(record["thread"]) if record.get("thread") is not None else None
        ),
        classification=EvalClassificationView(
            state=record.get("state"),
            trajectory=record.get("trajectory"),
            participation_balance=record.get("participation_balance"),
            discourse_quality=record.get("discourse_quality"),
            inquiry_phase=record.get("inquiry_phase"),
            reasoning=record.get("classification_reasoning"),
            confidence=(
                record.get("classification_confidence")
                or record.get("confidence")
            ),
        ),
        intervention=EvalInterventionView(
            decision=decision,
            role=record.get("role"),
            technique=record.get("technique"),
            post_to_thread=record.get("post_to_thread"),
            reasoning=record.get("intervention_reasoning"),
            confidence=record.get("intervention_confidence"),
        ),
        role_reasoning=record.get("role_reasoning"),
        role_confidence=record.get("role_confidence"),
        response=_response_view(record),
        duration_ms=int(float(record.get("duration_seconds", 0)) * 1000),
        error=record.get("error"),
    )


def _summary_markdown(run_dir: Path) -> str | None:
    summary_path = run_dir / "summary.md"
    if not summary_path.exists():
        return None

    return summary_path.read_text(encoding="utf-8")


def list_eval_runs() -> list[EvalRunSummary]:
    """Return discovered historical runs from the eval artifacts directory."""
    if not RESULTS_DIR.exists():
        return []

    runs: list[EvalRunSummary] = []
    for run_dir in sorted(
        (path for path in RESULTS_DIR.iterdir() if path.is_dir()), reverse=True
    ):
        json_files = sorted(run_dir.glob("*.json"))
        if not json_files:
            continue

        model_names: set[str] = set()
        thread_names: set[str] = set()
        error_count = 0
        durations: list[int] = []

        for json_file in json_files:
            record = _load_record(json_file)
            model_names.add(str(record["model"]))
            thread_names.add(str(record["thread"]))
            if record.get("error"):
                error_count += 1
            durations.append(int(float(record.get("duration_seconds", 0)) * 1000))

        timestamp, run_name = _parse_run_dir_name(run_dir)
        total_runs = len(json_files)
        runs.append(
            EvalRunSummary(
                run_id=run_dir.name,
                run_name=run_name,
                timestamp=timestamp,
                run_kind="evaluation",
                model_count=len(model_names),
                thread_count=len(thread_names),
                total_runs=total_runs,
                completed_runs=total_runs - error_count,
                error_count=error_count,
                avg_duration_ms=(sum(durations) // len(durations)),
                summary_available=(run_dir / "summary.md").exists(),
            )
        )

    return runs


def get_eval_run(run_id: str) -> EvalRunDetail | None:
    """Return grouped model/thread data for one historical run."""
    run_dir = RESULTS_DIR / run_id
    if not run_dir.exists() or not run_dir.is_dir():
        return None

    model_threads: dict[str, dict[str, EvalThreadResultView]] = {}
    for json_file in sorted(run_dir.glob("*.json")):
        record = _load_record(json_file)
        model_name = str(record["model"])
        thread_view = _thread_view(record)
        model_threads.setdefault(model_name, {})[thread_view.thread_key] = (
            thread_view
        )

    if not model_threads:
        return None

    models: dict[str, EvalModelResultView] = {}
    for model_name, threads in model_threads.items():
        durations = [thread.duration_ms for thread in threads.values()]
        error_count = sum(1 for thread in threads.values() if thread.error)
        models[model_name] = EvalModelResultView(
            model_name=model_name,
            family=_model_family(model_name),
            size=_model_size(model_name),
            threads=threads,
            completion_count=len(threads) - error_count,
            total_threads=len(threads),
            error_count=error_count,
            avg_duration_ms=(sum(durations) // len(durations)),
        )

    timestamp, run_name = _parse_run_dir_name(run_dir)
    return EvalRunDetail(
        run_id=run_id,
        run_name=run_name,
        timestamp=timestamp,
        run_kind="evaluation",
        models=models,
        summary_markdown=_summary_markdown(run_dir),
    )