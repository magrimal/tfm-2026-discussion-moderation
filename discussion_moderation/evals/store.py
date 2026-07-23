"""Pluggable run result store backends and filesystem helpers."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from functools import cache
from pathlib import Path
from typing import ClassVar

from discussion_moderation.config import get_settings
from discussion_moderation.evals.models import (
    _FIXTURE_ANCHORS,
    _FIXTURE_FILE,
    _REPO_BASE,
    MANIFEST_FILENAME,
    RUN_DIR_PATTERN,
    EvalClassificationView,
    EvalCommentView,
    EvalInterventionView,
    EvalModelResultView,
    EvalResponseView,
    EvalRunDetail,
    EvalRunManifest,
    EvalRunSummary,
    EvalThreadResultView,
)

RESULTS_DIR = Path(__file__).parents[2] / "docs" / "experiments" / "results"


class RunResultStore:
    """Base class for persisted run result backends.

    Subclasses register with a backend key and can then be resolved
    through RunResultStore.for_key(key, **kwargs).
    """

    _registry: ClassVar[dict[str, type[RunResultStore]]] = {}

    def __init_subclass__(cls, key: str = "", **kwargs: object) -> None:
        """Register subclass under key if provided."""
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
        """Return all available run summaries."""
        raise NotImplementedError

    def get_run(self, run_id: str) -> EvalRunDetail | None:
        """Return detailed run data for run_id, or None."""
        raise NotImplementedError

    def save_run(
        self,
        run: EvalRunManifest,
        *,
        summary_markdown: str | None = None,
    ) -> None:
        """Persist a run manifest and optional summary."""
        raise NotImplementedError

    def cancel_run(self, run_id: str) -> str | None:
        """Patch the manifest status from 'running' to 'cancelling'.

        Returns the resulting status string, or None if the run is not found.
        """
        raise NotImplementedError


class FilesystemRunResultStore(RunResultStore, key="filesystem"):
    """Filesystem-backed run result store.

    Reads run artifacts and manifests from docs/experiments/results.
    """

    def __init__(self, results_dir: Path = RESULTS_DIR) -> None:
        """Initialise with the given results directory."""
        self.results_dir = results_dir
        # Terminal-run summaries never change once written, so caching
        # them keeps list_runs() from re-reading every historical run's
        # manifest on every poll - only active runs and runs seen for
        # the first time cost a real read. Instance-level (not a
        # ClassVar): get_run_result_store() memoizes the store instance
        # in production so the cache persists across polls, while tests
        # constructing this class directly each get a fresh, empty one.
        self._summary_cache: dict[str, EvalRunSummary] = {}

    def list_runs(self) -> list[EvalRunSummary]:
        """Return all runs discovered in the results directory."""
        return list_eval_runs_from_dir(
            self.results_dir, cache=self._summary_cache
        )

    def get_run(self, run_id: str) -> EvalRunDetail | None:
        """Return detailed run data for run_id from the filesystem."""
        return get_eval_run_from_dir(self.results_dir, run_id)

    def save_run(
        self,
        run: EvalRunManifest,
        *,
        summary_markdown: str | None = None,
    ) -> None:
        """Write run manifest and optional summary to the results directory."""
        run_dir = self.results_dir / run.run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        manifest_path(run_dir).write_text(
            run.model_dump_json(indent=2),
            encoding="utf-8",
        )
        if summary_markdown is not None:
            (run_dir / "summary.md").write_text(
                summary_markdown,
                encoding="utf-8",
            )

    def cancel_run(self, run_id: str) -> str | None:
        """Patch the manifest status from 'running' to 'cancelling'."""
        run_dir = self.results_dir / run_id
        mp = manifest_path(run_dir)
        if not mp.exists():
            return None
        data = json.loads(mp.read_text(encoding="utf-8"))
        current = data.get("status")
        if current != "running":
            return current
        data["status"] = "cancelling"
        mp.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return "cancelling"


@cache
def _cached_filesystem_store(results_dir: Path) -> FilesystemRunResultStore:
    """Return a store instance memoized per results_dir.

    Keying on results_dir (not a constant) means a monkeypatched
    RESULTS_DIR in tests naturally produces its own cache entry,
    instead of reusing another test's stale instance.
    """
    return FilesystemRunResultStore(results_dir=results_dir)


@cache
def _cached_s3_store(
    bucket: str, prefix: str, env_name: str
) -> RunResultStore:
    """Return a store instance memoized per (bucket, prefix, env_name)."""
    from discussion_moderation.evals.s3_store import S3RunResultStore

    return S3RunResultStore(bucket=bucket, prefix=prefix, env_name=env_name)


def get_run_result_store(key: str = "filesystem") -> RunResultStore:
    """Resolve and return the configured run result backend.

    Defaults to the filesystem backend rooted at RESULTS_DIR.
    Supports "filesystem" and "s3". The S3 backend is instantiated
    from Settings when key is "s3".

    The returned instance is memoized per underlying config (results_dir,
    or bucket/prefix/env_name), so the same instance - and its summary
    cache - is reused across requests within a process, without going
    stale when tests monkeypatch RESULTS_DIR or settings.
    """
    if key == "filesystem":
        return _cached_filesystem_store(RESULTS_DIR)
    if key == "s3":
        settings = get_settings()
        if not settings.s3_bucket:
            raise ValueError(
                "FACILITATION_S3_BUCKET must be set when"
                " run_results_backend is 's3'"
            )
        return _cached_s3_store(
            settings.s3_bucket, settings.s3_prefix, settings.env_name
        )
    store = RunResultStore.for_key(key)
    if store is None:
        raise ValueError(f"Unknown run result store backend: {key!r}")
    return store


def parse_run_dir_name(run_dir: Path) -> tuple[str, str]:
    """Parse a run directory name into (ISO timestamp, display name)."""
    match = RUN_DIR_PATTERN.match(run_dir.name)
    if not match:
        return run_dir.name, run_dir.name

    timestamp = match.group("timestamp")
    name = match.group("name") or run_dir.name
    parsed = datetime.strptime(timestamp, "%Y-%m-%dT%H-%M").replace(tzinfo=UTC)
    return parsed.isoformat(), name


def model_family(model_name: str) -> str | None:
    """Extract the family prefix from a colon-separated model name."""
    if ":" not in model_name:
        return None
    return model_name.split(":", maxsplit=1)[0]


def model_size(model_name: str) -> str | None:
    """Extract the size suffix from a colon-separated model name."""
    candidate = model_name.rsplit(":", maxsplit=1)[-1]
    return candidate or None


def load_record(path: Path) -> dict[str, object]:
    """Load and return a JSON record from path."""
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def manifest_path(run_dir: Path) -> Path:
    """Return the path to run_manifest.json inside run_dir."""
    return run_dir / MANIFEST_FILENAME


def load_manifest(run_dir: Path) -> EvalRunManifest | None:
    """Load and validate the run manifest from run_dir, or None."""
    mp = manifest_path(run_dir)
    if not mp.exists():
        return None

    with mp.open(encoding="utf-8") as handle:
        return EvalRunManifest.model_validate(json.load(handle))


def response_view(record: dict[str, object]) -> EvalResponseView | None:
    """Build an EvalResponseView from a raw record dict, or None."""
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


def resolve_thread_url(record: dict[str, object]) -> str | None:
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


def normalize_error(raw_error: object) -> str | None:
    """Return a non-empty error string, or None if no error occurred.

    An empty string means an error occurred but its message was lost
    (e.g. str(TimeoutError()) is ''). Empty string is falsy, so every
    downstream `if thread.error` check (error counts, error banners,
    row styling) would silently treat it as success. Distinguish "no
    error" (None) from "error with no message" (empty string) here,
    once, so every consumer's truthy check works correctly.
    """
    if raw_error is None:
        return None
    return str(raw_error) or "Unknown error (no message recorded)"


def thread_view(record: dict[str, object]) -> EvalThreadResultView:
    """Build an EvalThreadResultView from a raw record dict."""
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
        thread_url=resolve_thread_url(record),
        course_id=(
            str(record["course_id"]) if record.get("course_id") else None
        ),
        thread_body=(
            str(record["thread_body"]) if record.get("thread_body") else None
        ),
        thread_comments=(
            [
                EvalCommentView(
                    author=str(comment["author"]),
                    body=str(comment["body"]),
                )
                for comment in record["thread_comments"]  # type: ignore[union-attr]
            ]
            if isinstance(record.get("thread_comments"), list)
            else None
        ),
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
        response=response_view(record),
        duration_ms=int(float(record.get("duration_seconds", 0)) * 1000),
        error=normalize_error(record.get("error")),
        messages=record.get("messages") or None,
        pipeline_messages=record.get("pipeline_messages") or None,
        logfuse_url=(
            str(record["logfuse_url"]) if record.get("logfuse_url") else None
        ),
    )


def summary_markdown(run_dir: Path) -> str | None:
    """Return the summary.md contents for run_dir, or None."""
    summary_path = run_dir / "summary.md"
    if not summary_path.exists():
        return None

    return summary_path.read_text(encoding="utf-8")


def summary_from_manifest(
    manifest: EvalRunManifest,
    *,
    summary_available: bool,
) -> EvalRunSummary:
    """Build an EvalRunSummary from a parsed manifest."""
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


def build_models_from_records(
    records: list[dict[str, object]],
) -> dict[str, EvalModelResultView]:
    """Group raw records into EvalModelResultView by model name."""
    model_threads: dict[str, dict[str, EvalThreadResultView]] = {}
    for record in records:
        model_name = str(record["model"])
        tv = thread_view(record)
        model_threads.setdefault(model_name, {})[tv.thread_key] = tv

    models: dict[str, EvalModelResultView] = {}
    for model_name, threads in model_threads.items():
        durations = [t.duration_ms for t in threads.values()]
        error_count = sum(1 for t in threads.values() if t.error)
        models[model_name] = EvalModelResultView(
            model_name=model_name,
            family=model_family(model_name),
            size=model_size(model_name),
            threads=threads,
            completion_count=len(threads) - error_count,
            total_threads=len(threads),
            error_count=error_count,
            avg_duration_ms=(
                (sum(durations) // len(durations)) if durations else 0
            ),
        )

    return models


def list_eval_runs_from_dir(
    results_dir: Path,
    cache: dict[str, EvalRunSummary] | None = None,
) -> list[EvalRunSummary]:
    """Return discovered historical runs from a filesystem directory.

    When cache is given, a run already known to be in a terminal
    status is served from it instead of re-reading and re-parsing its
    manifest - only active runs and runs seen for the first time cost
    a real read.
    """
    if not results_dir.exists():
        return []

    runs: list[EvalRunSummary] = []
    for run_dir in sorted(
        (path for path in results_dir.iterdir() if path.is_dir()),
        reverse=True,
    ):
        cached = cache.get(run_dir.name) if cache is not None else None
        if cached is not None and cached.status not in (
            "running",
            "cancelling",
        ):
            runs.append(cached)
            continue

        manifest = load_manifest(run_dir)
        if manifest is not None:
            summary = summary_from_manifest(
                manifest,
                summary_available=(run_dir / "summary.md").exists(),
            )
            if cache is not None and summary.status not in (
                "running",
                "cancelling",
            ):
                cache[run_dir.name] = summary
            runs.append(summary)
            continue

        json_files = sorted(run_dir.glob("*.json"))
        if not json_files:
            continue

        model_names: set[str] = set()
        thread_names: set[str] = set()
        error_count = 0
        durations: list[int] = []

        for json_file in json_files:
            record = load_record(json_file)
            model_names.add(str(record["model"]))
            thread_names.add(str(record["thread"]))
            if record.get("error"):
                error_count += 1
            durations.append(
                int(float(record.get("duration_seconds", 0)) * 1000)
            )

        timestamp, run_name = parse_run_dir_name(run_dir)
        total_runs = len(json_files)
        summary = EvalRunSummary(
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
        if cache is not None:
            cache[run_dir.name] = summary
        runs.append(summary)

    return runs


def get_eval_run_from_dir(
    results_dir: Path, run_id: str
) -> EvalRunDetail | None:
    """Return grouped model/thread data for one run from filesystem."""
    run_dir = results_dir / run_id
    if not run_dir.exists() or not run_dir.is_dir():
        return None

    manifest = load_manifest(run_dir)

    json_files = [
        f for f in sorted(run_dir.glob("*.json")) if f.name != MANIFEST_FILENAME
    ]

    if json_files:
        model_threads: dict[str, dict[str, EvalThreadResultView]] = {}
        for json_file in json_files:
            record = load_record(json_file)
            model_name = str(record["model"])
            tv = thread_view(record)
            model_threads.setdefault(model_name, {})[tv.thread_key] = tv

        expected_per_model: int | None = None
        if (
            manifest is not None
            and manifest.total_runs
            and manifest.status in ("running", "cancelling")
            and model_threads
        ):
            expected_per_model = manifest.total_runs // len(model_threads)

        models: dict[str, EvalModelResultView] = {}
        for model_name, threads in model_threads.items():
            durations = [t.duration_ms for t in threads.values()]
            error_count = sum(1 for t in threads.values() if t.error)
            models[model_name] = EvalModelResultView(
                model_name=model_name,
                family=model_family(model_name),
                size=model_size(model_name),
                threads=threads,
                completion_count=len(threads) - error_count,
                total_threads=(
                    expected_per_model
                    if expected_per_model is not None
                    else len(threads)
                ),
                error_count=error_count,
                avg_duration_ms=(
                    (sum(durations) // len(durations)) if durations else 0
                ),
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
                summary_markdown=summary_markdown(run_dir),
            )

        timestamp, run_name = parse_run_dir_name(run_dir)
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
            summary_markdown=summary_markdown(run_dir),
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
            summary_markdown=summary_markdown(run_dir),
        )

    return None
