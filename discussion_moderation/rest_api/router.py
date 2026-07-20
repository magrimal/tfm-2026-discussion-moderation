"""HTTP routes for the facilitation service."""

from __future__ import annotations

import asyncio
import logging
import os
import re
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter

import httpx
from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from discussion_moderation.api.facilitation import (
    FacilitationOutcome,
    facilitate,
    facilitate_and_post,
)
from discussion_moderation.config import get_settings
from discussion_moderation.evals.artifacts import (
    cancel_run,
    get_eval_run,
    list_eval_runs,
    write_run_manifest,
)
from discussion_moderation.evals.eval_models import (
    DEFAULT_MODELS,
    run_experiment,
)
from discussion_moderation.evals.fixtures.threads import ALL_THREADS
from discussion_moderation.evals.models import (
    EvalRunDetail,
    EvalRunSummary,
)
from discussion_moderation.evals.store import (
    RESULTS_DIR,
    RunResultStore,
    get_run_result_store,
)
from discussion_moderation.graph.pipeline import run_pipeline
from discussion_moderation.models import (
    DiscussionThread,
    PipelineDeps,
    PipelineResult,
    ThreadSummary,
)
from discussion_moderation.tools.history import (
    SQLiteThreadStore,
    ThreadHistoryStore,
)
from discussion_moderation.tools.protocols import LMSBackend
from discussion_moderation.utils import logfire_trace_url

logger = logging.getLogger(__name__)


def _get_eval_models() -> list[str]:
    """Return the list of models for eval runs.

    Reads EVAL_MODELS env var (comma-separated) if set, otherwise
    falls back to DEFAULT_MODELS from eval_models.
    """
    env = os.environ.get("EVAL_MODELS", "").strip()
    if env:
        return [m.strip() for m in env.split(",") if m.strip()]
    return list(DEFAULT_MODELS)


public_router = APIRouter()
protected_router = APIRouter()


def _resolve_run_result_store() -> RunResultStore:
    """Return the configured run result store backend."""
    return get_run_result_store(get_settings().run_results_backend)


def _resolve_history_store() -> ThreadHistoryStore | None:
    """Return the configured history store backend."""
    settings = get_settings()
    if settings.history_backend == "sqlite":
        return SQLiteThreadStore(db_path=settings.history_db_path)
    return ThreadHistoryStore.for_key(settings.history_backend)


def _live_run_id(thread_id: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9_-]", "-", thread_id)
    timestamp = datetime.now(UTC).strftime("%Y-%m-%dT%H-%M")
    return f"{timestamp}-live-{slug}"


def _live_run_record(
    *,
    model_name: str,
    thread: DiscussionThread,
    outcome: FacilitationOutcome,
    duration_seconds: float,
    lms_url: str = "",
) -> dict[str, object]:
    """Build one manifest record row from a live facilitation outcome."""
    classification = outcome.result.classification
    intervention = outcome.result.intervention
    role_selection = outcome.result.role_selection
    response = outcome.result.response

    thread_url = (
        f"{lms_url.rstrip('/')}/courses/{thread.course_id}/discussion/posts/{thread.id}"
        if lms_url
        else None
    )

    return {
        "model": model_name,
        "thread_url": thread_url,
        "course_id": thread.course_id,
        "thread": thread.id,
        "thread_title": thread.title,
        "thread_body": thread.body,
        "thread_comments": [
            {"author": comment.author, "body": comment.body}
            for comment in thread.comments
        ],
        "expected_state": None,
        "state": classification.state.value,
        "trajectory": classification.trajectory.value,
        "participation_balance": (classification.participation_balance.value),
        "discourse_quality": classification.discourse_quality.value,
        "inquiry_phase": classification.inquiry_phase.value,
        "classification_reasoning": classification.reasoning,
        "classification_confidence": classification.confidence,
        "should_intervene": (
            intervention.should_intervene if intervention is not None else None
        ),
        "intervention_reasoning": (
            intervention.reasoning if intervention is not None else None
        ),
        "intervention_confidence": (
            intervention.confidence if intervention is not None else None
        ),
        "role": role_selection.role.value if role_selection else None,
        "role_reasoning": role_selection.reasoning if role_selection else None,
        "role_confidence": (
            role_selection.confidence if role_selection else None
        ),
        "technique": response.technique_used if response else None,
        "action_category": (
            response.action_category.value if response else None
        ),
        "response_confidence": response.confidence if response else None,
        "post_to_thread": outcome.comment_posted,
        "response_reasoning": response.reasoning if response else None,
        "response_text": response.response_text if response else None,
        # outcome.result.error is set by a node's own graceful
        # degradation (ADR 0032) - a later stage caught an exception
        # internally and returned a partial result instead of raising.
        "error": outcome.result.error,
        "duration_seconds": duration_seconds,
        "messages": outcome.result.messages,
    }


@protected_router.post(
    "/facilitate",
    response_model=PipelineResult,
    status_code=status.HTTP_200_OK,
)
async def facilitate_thread(
    thread: DiscussionThread,
) -> PipelineResult | JSONResponse:
    """Run the facilitation pipeline on a discussion thread.

    Description:
        HTTP endpoint for the facilitation pipeline. Applies a
        configurable timeout to prevent long-running requests.

    Args:
        thread: The discussion thread to analyze.

    Returns:
        PipelineResult on success, 504 on timeout.
    """
    settings = get_settings()
    try:
        return await asyncio.wait_for(
            facilitate(thread),
            timeout=settings.pipeline_timeout_seconds,
        )
    except TimeoutError:
        return JSONResponse(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            content={"detail": "Pipeline timed out."},
        )


@protected_router.post(
    "/facilitate/thread/{thread_id}",
    response_model=FacilitationOutcome,
    status_code=status.HTTP_200_OK,
)
async def facilitate_thread_by_id(
    thread_id: str,
) -> FacilitationOutcome | JSONResponse:
    """Fetch a thread, run the pipeline, and post back if warranted.

    Description:
        Full integration cycle endpoint. Fetches the thread from the
        configured LMS backend, runs the pipeline, and posts a comment
        back to the forum if intervention is warranted and
        FACILITATION_BOT_USER_ID is set.

    Args:
        thread_id: Platform-specific thread identifier.

    Returns:
        FacilitationOutcome with pipeline result and comment_posted
        status on success, 504 on timeout, 400 if no backend is
        configured.
    """
    settings = get_settings()
    try:
        return await asyncio.wait_for(
            facilitate_and_post(thread_id),
            timeout=settings.pipeline_timeout_seconds,
        )
    except ValueError as exc:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": str(exc)},
        )
    except TimeoutError:
        return JSONResponse(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            content={"detail": "Pipeline timed out."},
        )


@public_router.get(
    "/health",
    status_code=status.HTTP_200_OK,
)
async def health() -> dict[str, str]:
    """Return service health status and top-level configuration.

    Returns:
        Health status dictionary with lms_url for the dashboard.
    """
    settings = get_settings()
    return {"status": "ok", "lms_url": settings.lms_url}


@protected_router.get(
    "/runs",
    response_model=list[EvalRunSummary],
    status_code=status.HTTP_200_OK,
)
@protected_router.get(
    "/evals/runs",
    response_model=list[EvalRunSummary],
    status_code=status.HTTP_200_OK,
)
async def list_runs() -> list[EvalRunSummary]:
    """Return historical runs discovered from persisted artifacts."""
    return list_eval_runs(store=_resolve_run_result_store())


class CommentSummary(BaseModel):
    """Lightweight comment representation for thread descriptors."""

    author: str
    body: str


class ThreadDescriptor(BaseModel):
    """Available thread fixture for eval runs."""

    key: str
    title: str
    body: str = ""
    comments: list[CommentSummary] = []


class TriggerRunRequest(BaseModel):
    """Payload for triggering a new eval run."""

    run_name: str = ""
    models: list[str] | None = None
    threads: list[str] | None = None


class TriggerRunResponse(BaseModel):
    """Response returned immediately after triggering a run."""

    run_id: str
    status: str = "running"


class LiveTriggerRunRequest(BaseModel):
    """Payload for triggering one live facilitation run."""

    thread_id: str
    run_name: str = ""


class LiveTriggerRunResponse(BaseModel):
    """Response for a completed live run."""

    run_id: str
    status: str
    thread_id: str
    comment_posted: bool = False
    comment_id: str | None = None


class InterventionHistoryItem(BaseModel):
    """Intervention history row shown by the API."""

    thread_id: str
    timestamp: str
    role: str
    technique: str
    reasoning: str
    response_text: str


@protected_router.get(
    "/runs/threads",
    response_model=list[ThreadDescriptor],
    status_code=status.HTTP_200_OK,
)
async def list_threads() -> list[ThreadDescriptor]:
    """Return the available thread fixtures for eval runs."""
    result = []
    for key, factory in ALL_THREADS.items():
        thread = factory()
        result.append(
            ThreadDescriptor(
                key=key,
                title=thread.title,
                body=thread.body,
                comments=[
                    CommentSummary(author=c.author, body=c.body)
                    for c in thread.comments
                ],
            )
        )
    return result


@protected_router.get(
    "/runs/models",
    response_model=list[str],
    status_code=status.HTTP_200_OK,
)
async def list_eval_models() -> list[str]:
    """Return the configured eval model list.

    Reads EVAL_MODELS env var if set, otherwise returns DEFAULT_MODELS.
    """
    return _get_eval_models()


@protected_router.get(
    "/threads/browse",
    response_model=list[ThreadSummary],
    status_code=status.HTTP_200_OK,
)
async def browse_threads(course_id: str) -> list[ThreadSummary]:
    """Return active threads from a course for monitoring.

    Delegates to the configured LMS backend. Returns an empty list for
    the stub backend. Raises 503 when the backend is not configured.
    """
    settings = get_settings()
    backend = LMSBackend.for_key(settings.lms_backend)
    if backend is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "LMS backend not configured. "
                "Set FACILITATION_LMS_BACKEND to enable thread browsing."
            ),
        )

    try:
        return await backend.list_threads(course_id)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                f"LMS returned {exc.response.status_code} "
                f"for course {course_id!r}."
            ),
        ) from exc
    except httpx.RequestError as exc:
        lms_url = settings.lms_url.rstrip("/")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Could not reach LMS at {lms_url}: {exc}",
        ) from exc


async def _run_experiment_background(
    models: list[str] | None,
    run_name: str,
    run_id: str,
    threads: list[str] | None,
    out_dir: Path,
    result_store: RunResultStore,
) -> None:
    """Run eval_models.run_experiment in the background."""
    logger.info("Starting experiment run: %s", run_id)
    await run_experiment(
        models=models,
        run_name=run_name,
        threads=threads,
        out_dir=out_dir,
        result_store=result_store,
    )


async def _run_lms_experiment_background(
    models: list[str] | None,
    run_name: str,
    run_id: str,
    run_timestamp: str,
    thread_ids: list[str],
    out_dir: Path,
    result_store: RunResultStore,
) -> None:
    """Run an experiment over real LMS threads (snapshot mode).

    This runner does not post to LMS and does not write to intervention
    history, because it is still an experiment flow.
    """
    logger.info("Starting LMS experiment run: %s", run_id)
    settings = get_settings()
    selected_models = models or _get_eval_models()
    lms_backend = LMSBackend.for_key(settings.lms_backend)
    if lms_backend is None:
        raise ValueError("LMS experiments require FACILITATION_LMS_BACKEND.")

    records: list[dict[str, object]] = []
    total_runs = len(selected_models) * len(thread_ids)
    completed = 0
    cancelled = False

    write_run_manifest(
        out_dir,
        run_id=run_id,
        run_name=run_name or run_id,
        timestamp=run_timestamp,
        records=[],
        run_type="experiment",
        status="running",
        progress_message="Preparing LMS snapshot run...",
        expected_model_count=len(selected_models),
        expected_thread_count=len(thread_ids),
        expected_total_runs=total_runs,
        store=result_store,
    )

    for model_name in selected_models:
        model_settings = settings.model_copy(
            update={
                "llm_model": model_name,
                "history_backend": "memory",
            }
        )
        deps = PipelineDeps(settings=model_settings, lms_backend=lms_backend)

        for thread_id in thread_ids:
            run_detail = result_store.get_run(run_id)
            if run_detail is not None and run_detail.status == "cancelling":
                cancelled = True
                break
            started_at = perf_counter()
            try:

                async def _fetch_and_run() -> tuple[
                    DiscussionThread, PipelineResult
                ]:
                    fetched_thread = await lms_backend.get_thread(thread_id)
                    pipeline_result = await run_pipeline(fetched_thread, deps)
                    return fetched_thread, pipeline_result

                thread, result = await asyncio.wait_for(
                    _fetch_and_run(),
                    timeout=model_settings.pipeline_timeout_seconds,
                )
                duration_seconds = perf_counter() - started_at
                record = _live_run_record(
                    model_name=model_name,
                    thread=thread,
                    outcome=FacilitationOutcome(
                        result=result,
                        comment_posted=False,
                    ),
                    duration_seconds=duration_seconds,
                )
                record["logfuse_url"] = logfire_trace_url(
                    settings.logfire_project_url
                )
                records.append(record)
            except Exception as exc:
                duration_seconds = perf_counter() - started_at
                logger.exception(
                    "Pipeline failed for model=%s thread=%s: %s",
                    model_name,
                    thread_id,
                    exc,
                )
                records.append(
                    {
                        "model": model_name,
                        "thread": thread_id,
                        "thread_title": thread_id,
                        "expected_state": None,
                        "state": None,
                        "trajectory": None,
                        "participation_balance": None,
                        "discourse_quality": None,
                        "inquiry_phase": None,
                        "classification_reasoning": None,
                        "classification_confidence": None,
                        "should_intervene": None,
                        "intervention_reasoning": None,
                        "intervention_confidence": None,
                        "role": None,
                        "role_reasoning": None,
                        "role_confidence": None,
                        "technique": None,
                        "action_category": None,
                        "response_confidence": None,
                        "post_to_thread": False,
                        "response_reasoning": None,
                        "response_text": None,
                        "error": f"{type(exc).__name__}: {exc}",
                        "duration_seconds": duration_seconds,
                    }
                )

            completed += 1
            write_run_manifest(
                out_dir,
                run_id=run_id,
                run_name=run_name or run_id,
                timestamp=run_timestamp,
                records=records,
                run_type="experiment",
                status="running",
                progress_message=(
                    f"[{completed}/{total_runs}] {model_name} / {thread_id}"
                ),
                expected_model_count=len(selected_models),
                expected_thread_count=len(thread_ids),
                expected_total_runs=total_runs,
                store=result_store,
            )

        if cancelled:
            logger.info(
                "LMS run %s cancelled after %d/%d steps.",
                run_id,
                completed,
                total_runs,
            )
            break

    final_status = "cancelled" if cancelled else "completed"
    summary_lines = [
        "# LMS Experiment Summary",
        "",
        f"Run: {run_name}",
        f"Models: {len(selected_models)}",
        f"Threads: {len(thread_ids)}",
        f"Records: {len(records)}",
    ]
    summary_markdown = "\n".join(summary_lines) + "\n"

    write_run_manifest(
        out_dir,
        run_id=run_id,
        run_name=run_name or run_id,
        timestamp=run_timestamp,
        records=records,
        run_type="experiment",
        status=final_status,
        progress_message=None,
        expected_model_count=len(selected_models),
        expected_thread_count=len(thread_ids),
        expected_total_runs=total_runs,
        store=result_store,
        summary_markdown=summary_markdown,
    )


@protected_router.post(
    "/runs/trigger",
    response_model=TriggerRunResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def trigger_run(
    request: TriggerRunRequest,
    background_tasks: BackgroundTasks,
) -> TriggerRunResponse:
    """Start a new eval run in the background.

    Creates the output directory and an initial manifest with
    status='running' immediately, then runs the experiment
    asynchronously. Poll GET /runs to track completion.
    """
    run_name_slug = (
        re.sub(r"[^a-zA-Z0-9_-]", "-", request.run_name.strip())
        if request.run_name.strip()
        else ""
    )
    timestamp = datetime.now(UTC).strftime("%Y-%m-%dT%H-%M")
    dir_name = f"{timestamp}-{run_name_slug}" if run_name_slug else timestamp
    out_dir = RESULTS_DIR / dir_name
    out_dir.mkdir(parents=True, exist_ok=True)
    run_result_store = _resolve_run_result_store()

    timestamp_iso = (
        datetime.strptime(timestamp, "%Y-%m-%dT%H-%M")
        .replace(tzinfo=UTC)
        .isoformat()
    )
    selected_models = request.models or _get_eval_models()
    selected_threads = request.threads if request.threads else list(ALL_THREADS)
    write_run_manifest(
        out_dir,
        run_id=dir_name,
        run_name=request.run_name or dir_name,
        timestamp=timestamp_iso,
        records=[],
        status="running",
        progress_message="Queued for execution...",
        expected_model_count=len(selected_models),
        expected_thread_count=len(selected_threads),
        expected_total_runs=(len(selected_models) * len(selected_threads)),
        store=run_result_store,
    )

    if not request.threads or all(
        thread in ALL_THREADS for thread in request.threads
    ):
        background_tasks.add_task(
            _run_experiment_background,
            models=request.models,
            run_name=request.run_name,
            run_id=dir_name,
            threads=request.threads,
            out_dir=out_dir,
            result_store=run_result_store,
        )
    else:
        background_tasks.add_task(
            _run_lms_experiment_background,
            models=request.models,
            run_name=request.run_name,
            run_id=dir_name,
            run_timestamp=timestamp_iso,
            thread_ids=request.threads,
            out_dir=out_dir,
            result_store=run_result_store,
        )

    return TriggerRunResponse(run_id=dir_name)


@protected_router.post(
    "/runs/live/trigger",
    response_model=LiveTriggerRunResponse,
    status_code=status.HTTP_200_OK,
)
async def trigger_live_run(
    request: LiveTriggerRunRequest,
) -> LiveTriggerRunResponse:
    """Run live facilitation for one LMS thread and persist run metadata."""
    settings = get_settings()
    lms_backend = LMSBackend.for_key(settings.lms_backend)
    if lms_backend is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Live runs require a configured LMS backend. "
                "Set FACILITATION_LMS_BACKEND."
            ),
        )

    run_result_store = _resolve_run_result_store()
    run_id = _live_run_id(request.thread_id)
    logger.info("Starting live run: %s thread=%s", run_id, request.thread_id)
    timestamp = datetime.now(UTC).isoformat()
    run_name = request.run_name.strip() or run_id
    out_dir = RESULTS_DIR / run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    write_run_manifest(
        out_dir,
        run_id=run_id,
        run_name=run_name,
        timestamp=timestamp,
        records=[],
        run_type="live",
        status="running",
        progress_message="Fetching LMS thread...",
        expected_model_count=1,
        expected_thread_count=1,
        expected_total_runs=1,
        store=run_result_store,
    )

    thread = await lms_backend.get_thread(request.thread_id)

    if not request.run_name.strip() and thread.title:
        run_name = thread.title

    if thread.closed:
        write_run_manifest(
            out_dir,
            run_id=run_id,
            run_name=run_name,
            timestamp=timestamp,
            records=[],
            run_type="live",
            status="noop",
            progress_message="Thread is closed. No action taken.",
            expected_model_count=1,
            expected_thread_count=1,
            expected_total_runs=1,
            store=run_result_store,
        )
        return LiveTriggerRunResponse(
            run_id=run_id,
            status="noop",
            thread_id=request.thread_id,
        )

    write_run_manifest(
        out_dir,
        run_id=run_id,
        run_name=run_name,
        timestamp=timestamp,
        records=[],
        run_type="live",
        status="running",
        progress_message="Running facilitation pipeline...",
        expected_model_count=1,
        expected_thread_count=1,
        expected_total_runs=1,
        store=run_result_store,
    )

    started_at = perf_counter()
    outcome = await facilitate_and_post(request.thread_id)
    duration_seconds = perf_counter() - started_at

    live_record = _live_run_record(
        model_name=settings.llm_model,
        thread=thread,
        outcome=outcome,
        duration_seconds=duration_seconds,
        lms_url=settings.lms_url,
    )
    write_run_manifest(
        out_dir,
        run_id=run_id,
        run_name=run_name,
        timestamp=timestamp,
        records=[live_record],
        run_type="live",
        status="completed",
        progress_message=None,
        expected_model_count=1,
        expected_thread_count=1,
        expected_total_runs=1,
        store=run_result_store,
    )

    return LiveTriggerRunResponse(
        run_id=run_id,
        status="completed",
        thread_id=request.thread_id,
        comment_posted=outcome.comment_posted,
        comment_id=outcome.comment_id,
    )


@protected_router.get(
    "/threads/{thread_id}/history",
    response_model=list[InterventionHistoryItem],
    status_code=status.HTTP_200_OK,
)
async def get_thread_history(thread_id: str) -> list[InterventionHistoryItem]:
    """Return recorded intervention history for a discussion thread."""
    store = _resolve_history_store()
    if store is None:
        return []

    records = store.get_history(thread_id)
    return [
        InterventionHistoryItem(
            thread_id=record.thread_id,
            timestamp=record.timestamp.isoformat(),
            role=record.role.value,
            technique=record.technique,
            reasoning=record.reasoning,
            response_text=record.response_text,
        )
        for record in records
    ]


@protected_router.get(
    "/runs/{run_id}",
    response_model=EvalRunDetail,
    status_code=status.HTTP_200_OK,
)
@protected_router.get(
    "/evals/runs/{run_id}",
    response_model=EvalRunDetail,
    status_code=status.HTTP_200_OK,
)
async def get_run(run_id: str) -> EvalRunDetail:
    """Return detailed grouped results for one historical run."""
    run = get_eval_run(run_id, store=_resolve_run_result_store())
    if run is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Run not found.",
        )
    return run


@protected_router.post(
    "/runs/{run_id}/cancel",
    status_code=status.HTTP_200_OK,
)
async def cancel_run_endpoint(run_id: str) -> JSONResponse:
    """Request cancellation of a running experiment run.

    Patches the manifest status to 'cancelling'. The background task
    stops after the current LLM call completes and writes 'cancelled'.
    Returns 404 if the run does not exist, 409 if it is not running.
    """
    result = cancel_run(run_id, store=_resolve_run_result_store())
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Run not found.",
        )
    if result != "cancelling":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Run cannot be cancelled (status: {result}).",
        )
    return JSONResponse({"status": "cancelling"})
