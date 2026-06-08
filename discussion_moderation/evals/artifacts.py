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
from typing import ClassVar

from pydantic import BaseModel

RESULTS_DIR = Path(__file__).parents[2] / "docs" / "experiments" / "results"
MANIFEST_FILENAME = "run_manifest.json"
RUN_DIR_PATTERN = re.compile(
    r"^(?P<timestamp>\d{4}-\d{2}-\d{2}T\d{2}-\d{2})(?:-(?P<name>.+))?$"
)

_REPO_BASE = (
    "https://github.com/magrimal/tfm-2026-discussion-moderation/blob/main"
)
_FIXTURE_FILE = "discussion_moderation/evals/fixtures/threads.py"
# Line anchors for each fixture thread state in fixtures/threads.py.
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


class RunResultStore:
    """Base class for persisted run result backends.

    Subclasses register with a backend key and can then be resolved
    through RunResultStore.for_key(key, **kwargs).
    """

    _registry: ClassVar[dict[str, type[RunResultStore]]] = {}

    def __init_subclass__(cls, key: str = "", **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        if key:
            RunResultStore._registry[key] = cls

    @classmethod
    def for_key(cls, key: str) -> RunResultStore | None:
        """Return a default-configured backend instance for key, or None."""
        store_cls = cls._registry.get(key)
        if store_cls is None:
            return None
        return store_cls()

    def list_runs(self) -> list[EvalRunSummary]:
        raise NotImplementedError

    def get_run(self, run_id: str) -> EvalRunDetail | None:
        raise NotImplementedError

    def save_run(
        self,
        run: EvalRunManifest,
        *,
        summary_markdown: str | None = None,
    ) -> None:
        raise NotImplementedError


class FilesystemRunResultStore(RunResultStore, key="filesystem"):
    """Filesystem-backed run result store.

    Reads run artifacts and manifests from docs/experiments/results.
    """

    def __init__(self, results_dir: Path = RESULTS_DIR) -> None:
        self.results_dir = results_dir

    def list_runs(self) -> list[EvalRunSummary]:
        return _list_eval_runs_from_dir(self.results_dir)

    def get_run(self, run_id: str) -> EvalRunDetail | None:
        return _get_eval_run_from_dir(self.results_dir, run_id)

    def save_run(
        self,
        run: EvalRunManifest,
        *,
        summary_markdown: str | None = None,
    ) -> None:
        run_dir = self.results_dir / run.run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        _manifest_path(run_dir).write_text(
            run.model_dump_json(indent=2),
            encoding="utf-8",
        )
        if summary_markdown is not None:
            (run_dir / "summary.md").write_text(
                summary_markdown,
                encoding="utf-8",
            )


def get_run_result_store(key: str = "filesystem") -> RunResultStore:
    """Resolve and return the configured run result backend.

    Defaults to the filesystem backend rooted at RESULTS_DIR.
    """
    if key == "filesystem":
        return FilesystemRunResultStore(results_dir=RESULTS_DIR)
    store = RunResultStore.for_key(key)
    if store is None:
        raise ValueError(f"Unknown run result store backend: {key!r}")
    return store


def _parse_run_dir_name(run_dir: Path) -> tuple[str, str]:
    match = RUN_DIR_PATTERN.match(run_dir.name)
    if not match:
        return run_dir.name, run_dir.name

    timestamp = match.group("timestamp")
    name = match.group("name") or run_dir.name
    parsed = datetime.strptime(timestamp, "%Y-%m-%dT%H-%M").replace(tzinfo=UTC)
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


def _manifest_path(run_dir: Path) -> Path:
    return run_dir / MANIFEST_FILENAME


def _load_manifest(run_dir: Path) -> EvalRunManifest | None:
    manifest_path = _manifest_path(run_dir)
    if not manifest_path.exists():
        return None

    with manifest_path.open(encoding="utf-8") as handle:
        return EvalRunManifest.model_validate(json.load(handle))


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


def _resolve_thread_url(record: dict[str, object]) -> str | None:
    """Return the best available URL for a thread result record.

    Live runs carry an explicit thread_url (set by the router when the thread
    is fetched from the LMS). Experiment runs use fixture threads keyed by
    state name, so we fall back to a GitHub permalink into the fixture file.
    """
    explicit = record.get("thread_url")
    if explicit:
        return str(explicit)
    thread_key = str(record.get("thread", ""))
    anchor = _FIXTURE_ANCHORS.get(thread_key)
    if anchor is not None:
        return f"{_REPO_BASE}/{_FIXTURE_FILE}#L{anchor}"
    return None


def _thread_view(record: dict[str, object]) -> EvalThreadResultView:
    should_intervene = record.get("should_intervene")
    if should_intervene is True:
        decision = "intervene"
    elif should_intervene is False:
        decision = "no_intervention"
    else:
        decision = None

    if "expected_state" in record:
        expected_state = (
            str(record.get("expected_state"))
            if record.get("expected_state") is not None
            else None
        )
    else:
        expected_state = (
            str(record["thread"]) if record.get("thread") is not None else None
        )

    return EvalThreadResultView(
        thread_key=str(record["thread"]),
        thread_title=str(record.get("thread_title") or record["thread"]),
        thread_url=_resolve_thread_url(record),
        course_id=str(record["course_id"]) if record.get("course_id") else None,
        expected_state=expected_state,
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
        messages=record.get("messages") or None,
        pipeline_messages=record.get("pipeline_messages") or None,
        logfuse_url=str(record["logfuse_url"]) if record.get("logfuse_url") else None,
    )


def _summary_markdown(run_dir: Path) -> str | None:
    summary_path = run_dir / "summary.md"
    if not summary_path.exists():
        return None

    return summary_path.read_text(encoding="utf-8")


def _summary_from_manifest(
    manifest: EvalRunManifest,
    *,
    summary_available: bool,
) -> EvalRunSummary:
    return EvalRunSummary(
        run_id=manifest.run_id,
        run_name=manifest.run_name,
        timestamp=manifest.timestamp,
        run_type=manifest.run_type,
        run_kind=manifest.run_kind,
        status=manifest.status,
        progress_message=manifest.progress_message,
        model_count=manifest.model_count,
        thread_count=manifest.thread_count,
        total_runs=manifest.total_runs,
        completed_runs=manifest.completed_runs,
        error_count=manifest.error_count,
        avg_duration_ms=manifest.avg_duration_ms,
        summary_available=summary_available,
    )


def _build_models_from_records(
    records: list[dict[str, object]],
) -> dict[str, EvalModelResultView]:
    model_threads: dict[str, dict[str, EvalThreadResultView]] = {}
    for record in records:
        model_name = str(record["model"])
        thread_view = _thread_view(record)
        model_threads.setdefault(model_name, {})[thread_view.thread_key] = (
            thread_view
        )

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
            avg_duration_ms=(
                (sum(durations) // len(durations)) if durations else 0
            ),
        )

    return models


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
    models = _build_models_from_records(records)
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
        avg_duration_ms=(sum(durations) // len(durations)) if durations else 0,
        models=models,
    )
    manifest_path = _manifest_path(run_dir)
    manifest_path.write_text(
        manifest.model_dump_json(indent=2),
        encoding="utf-8",
    )
    if store is not None:
        store.save_run(manifest, summary_markdown=summary_markdown)
    return manifest_path


def _list_eval_runs_from_dir(results_dir: Path) -> list[EvalRunSummary]:
    """Return discovered historical runs from a filesystem directory."""
    if not results_dir.exists():
        return []

    runs: list[EvalRunSummary] = []
    for run_dir in sorted(
        (path for path in results_dir.iterdir() if path.is_dir()), reverse=True
    ):
        manifest = _load_manifest(run_dir)
        if manifest is not None:
            runs.append(
                _summary_from_manifest(
                    manifest,
                    summary_available=(run_dir / "summary.md").exists(),
                )
            )
            continue

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
            durations.append(
                int(float(record.get("duration_seconds", 0)) * 1000)
            )

        timestamp, run_name = _parse_run_dir_name(run_dir)
        total_runs = len(json_files)
        runs.append(
            EvalRunSummary(
                run_id=run_dir.name,
                run_name=run_name,
                timestamp=timestamp,
                run_type="experiment",
                run_kind="evaluation",
                status="completed",
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


def list_eval_runs(store: RunResultStore | None = None) -> list[EvalRunSummary]:
    """Return discovered historical runs from the configured result store."""
    selected_store = store or get_run_result_store()
    return selected_store.list_runs()


def mark_interrupted_runs(results_dir: Path = RESULTS_DIR) -> None:
    """Mark any runs left in 'running' state as 'interrupted'.

    Called at service startup to clean up runs that were in progress when
    the service was killed or restarted.
    """
    if not results_dir.exists():
        return
    for run_dir in results_dir.iterdir():
        if not run_dir.is_dir():
            continue
        manifest = _load_manifest(run_dir)
        if manifest is None or manifest.status != "running":
            continue
        manifest_path = _manifest_path(run_dir)
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        data["status"] = "interrupted"
        data["progress_message"] = "Run interrupted — service was restarted."
        manifest_path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _get_eval_run_from_dir(
    results_dir: Path, run_id: str
) -> EvalRunDetail | None:
    """Return grouped model/thread data for one run from filesystem."""
    run_dir = results_dir / run_id
    if not run_dir.exists() or not run_dir.is_dir():
        return None

    manifest = _load_manifest(run_dir)

    json_files = [
        f for f in sorted(run_dir.glob("*.json")) if f.name != MANIFEST_FILENAME
    ]

    if json_files:
        model_threads: dict[str, dict[str, EvalThreadResultView]] = {}
        for json_file in json_files:
            record = _load_record(json_file)
            model_name = str(record["model"])
            thread_view = _thread_view(record)
            model_threads.setdefault(model_name, {})[thread_view.thread_key] = (
                thread_view
            )

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

        if manifest is not None:
            return EvalRunDetail(
                run_id=manifest.run_id,
                run_name=manifest.run_name,
                timestamp=manifest.timestamp,
                run_type=manifest.run_type,
                run_kind=manifest.run_kind,
                status=manifest.status,
                progress_message=manifest.progress_message,
                total_runs=manifest.total_runs,
                completed_runs=manifest.completed_runs,
                error_count=manifest.error_count,
                models=models,
                summary_markdown=_summary_markdown(run_dir),
            )

        timestamp, run_name = _parse_run_dir_name(run_dir)
        total_runs = sum(model.total_threads for model in models.values())
        completed_runs = sum(
            model.completion_count for model in models.values()
        )
        error_count = sum(model.error_count for model in models.values())
        return EvalRunDetail(
            run_id=run_id,
            run_name=run_name,
            timestamp=timestamp,
            run_type="experiment",
            run_kind="evaluation",
            status="completed",
            total_runs=total_runs,
            completed_runs=completed_runs,
            error_count=error_count,
            models=models,
            summary_markdown=_summary_markdown(run_dir),
        )

    if manifest is not None:
        return EvalRunDetail(
            run_id=manifest.run_id,
            run_name=manifest.run_name,
            timestamp=manifest.timestamp,
            run_type=manifest.run_type,
            run_kind=manifest.run_kind,
            status=manifest.status,
            progress_message=manifest.progress_message,
            total_runs=manifest.total_runs,
            completed_runs=manifest.completed_runs,
            error_count=manifest.error_count,
            models=manifest.models,
            summary_markdown=_summary_markdown(run_dir),
        )

    return None


def get_eval_run(
    run_id: str, store: RunResultStore | None = None
) -> EvalRunDetail | None:
    """Return grouped model/thread data for one historical run."""
    selected_store = store or get_run_result_store()
    return selected_store.get_run(run_id)
