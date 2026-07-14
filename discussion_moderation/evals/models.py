"""Pydantic view models and shared constants for eval run artifacts."""

from __future__ import annotations

import re

from pydantic import BaseModel

MANIFEST_FILENAME = "run_manifest.json"
RUN_DIR_PATTERN = re.compile(
    r"^(?P<timestamp>\d{4}-\d{2}-\d{2}T\d{2}-\d{2})"
    r"(?:-(?P<name>.+))?$"
)
_REPO_BASE = (
    "https://github.com/magrimal/tfm-2026-discussion-moderation/blob/main"
)
_FIXTURE_FILE = "discussion_moderation/evals/fixtures/threads.py"
_FIXTURE_ANCHORS: dict[str, int] = {
    "new": 19,
    "active": 42,
    "stalled": 115,
    "conflictive": 148,
    "convergent": 204,
    "off_topic": 275,
    "shallow_discourse": 329,
    "dominated": 401,
}


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
    thread_url: str | None = None
    course_id: str | None = None
    expected_state: str | None
    classification: EvalClassificationView
    intervention: EvalInterventionView
    role_reasoning: str | None
    role_confidence: float | None
    response: EvalResponseView | None
    duration_ms: int
    error: str | None
    logfuse_url: str | None = None
    messages: list[dict] | None = None
    pipeline_messages: dict[str, list[dict]] | None = None


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
    run_type: str = "experiment"
    run_kind: str
    status: str
    progress_message: str | None = None
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
    run_type: str = "experiment"
    run_kind: str
    status: str = "completed"
    progress_message: str | None = None
    total_runs: int = 0
    completed_runs: int = 0
    error_count: int = 0
    models: dict[str, EvalModelResultView]
    summary_markdown: str | None


class EvalRunManifest(BaseModel):
    """Persisted run document stored alongside artifact files."""

    run_id: str
    run_name: str
    timestamp: str
    run_type: str = "experiment"
    run_kind: str
    status: str
    progress_message: str | None = None
    model_count: int
    thread_count: int
    total_runs: int
    completed_runs: int
    error_count: int
    avg_duration_ms: int
    models: dict[str, EvalModelResultView]
