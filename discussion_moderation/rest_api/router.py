"""HTTP routes for the facilitation service."""

import asyncio
import re
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter

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
    RESULTS_DIR,
    EvalRunDetail,
    EvalRunSummary,
    RunResultStore,
    get_eval_run,
    get_run_result_store,
    list_eval_runs,
    write_run_manifest,
)
from discussion_moderation.evals.fixtures.threads import ALL_THREADS
from discussion_moderation.graph.pipeline import run_pipeline
from discussion_moderation.models import (
    DiscussionThread,
    PipelineDeps,
    PipelineResult,
)
from discussion_moderation.tools.history import (
    SQLiteThreadStore,
    ThreadHistoryStore,
)
from discussion_moderation.tools.protocols import LMSBackend


def _get_eval_models() -> list[str]:
    """Return the list of models for eval runs.

    Reads EVAL_MODELS env var (comma-separated) if set, otherwise
    falls back to DEFAULT_MODELS from eval_models.
    """
    import os

    from discussion_moderation.evals.eval_models import DEFAULT_MODELS

    env = os.environ.get("EVAL_MODELS", "").strip()
    if env:
        return [m.strip() for m in env.split(",") if m.strip()]
    return list(DEFAULT_MODELS)

router = APIRouter()


def _resolve_run_result_store() -> RunResultStore:
    """Return the configured run result store backend."""
    settings = get_settings()
    try:
        if settings.run_results_backend == "mongo":
            return get_run_result_store(
                "mongo",
                mongo_uri=settings.run_results_mongo_uri,
                database_name=settings.run_results_mongo_database,
                collection_name=settings.run_results_mongo_collection,
            )
        return get_run_result_store("filesystem")
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Run result store configuration error: {exc}",
        ) from exc


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
) -> dict[str, object]:
    """Build one manifest record row from a live facilitation outcome."""
    classification = outcome.result.classification
    intervention = outcome.result.intervention
    role_selection = outcome.result.role_selection
    response = outcome.result.response

    return {
        "model": model_name,
        "thread": thread.id,
        "thread_title": thread.title,
        "expected_state": None,
        "state": classification.state.value,
        "trajectory": classification.trajectory.value,
        "participation_balance": (
            classification.participation_balance.value
        ),
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
        "error": None,
        "duration_seconds": duration_seconds,
    }


@router.post(
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


@router.post(
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


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
)
async def health() -> dict[str, str]:
    """Return service health status.

    Returns:
        Health status dictionary.
    """
    return {"status": "ok"}


@router.get(
    "/runs",
    response_model=list[EvalRunSummary],
    status_code=status.HTTP_200_OK,
)
@router.get(
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


@router.get(
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


@router.get(
    "/runs/models",
    response_model=list[str],
    status_code=status.HTTP_200_OK,
)
async def list_eval_models() -> list[str]:
    """Return the configured eval model list.

    Reads EVAL_MODELS env var if set, otherwise returns DEFAULT_MODELS.
    """
    return _get_eval_models()


class LmsThreadDescriptor(BaseModel):
    """A thread fetched from the Open edX LMS for monitoring."""

    id: str
    course_id: str
    title: str
    body: str = ""
    author: str = ""
    comment_count: int = 0
    comments: list[CommentSummary] = []


@router.get(
    "/lms/threads",
    response_model=list[LmsThreadDescriptor],
    status_code=status.HTTP_200_OK,
)
async def list_lms_threads(course_id: str) -> list[LmsThreadDescriptor]:
    """Return active threads from an Open edX course for monitoring.

    Calls GET /api/discussion/v1/threads/?course_id=<course_id> on the
    configured LMS URL. Fetches the first page of threads; each thread
    includes its opening body. Comment bodies are not fetched here
    because the list endpoint only provides counts — a separate call
    per thread would be required.

    Requires lms_url and lms_jwt_authentication_token to be configured.

    Raises:
        503: LMS not configured (lms_jwt_authentication_token missing).
        502: LMS responded with an unexpected status.
    """
    import httpx

    settings = get_settings()
    if not settings.lms_jwt_authentication_token:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "LMS not configured. Set LMS_JWT_AUTHENTICATION_TOKEN "
                "and FACILITATION_LMS_URL to enable LMS thread listing."
            ),
        )

    lms_url = settings.lms_url.rstrip("/")
    headers = {
        "Authorization": f"JWT {settings.lms_jwt_authentication_token}"
    }
    api_url = f"{lms_url}/api/discussion/v1/threads/"

    try:
        async with httpx.AsyncClient(headers=headers, timeout=15.0) as client:
            response = await client.get(
                api_url, params={"course_id": course_id, "page_size": 50}
            )
            response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                "LMS returned "
                f"{exc.response.status_code} for course {course_id!r}."
            ),
        ) from exc
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Could not reach LMS at {lms_url}: {exc}",
        ) from exc

    data = response.json()
    threads = data.get("results", [])
    return [
        LmsThreadDescriptor(
            id=t["id"],
            course_id=t.get("course_id", course_id),
            title=t.get("title", ""),
            body=t.get("raw_body", ""),
            author=t.get("author", ""),
            comment_count=t.get("comment_count", 0),
        )
        for t in threads
    ]


async def _run_experiment_background(
    models: list[str] | None,
    run_name: str,
    threads: list[str] | None,
    out_dir: Path,
    result_store: RunResultStore,
) -> None:
    """Wrapper that imports run_experiment lazily to keep router lean."""
    from discussion_moderation.evals.eval_models import run_experiment

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
    thread_ids: list[str],
    out_dir: Path,
    result_store: RunResultStore,
) -> None:
    """Run an experiment over real LMS threads (snapshot mode).

    This runner does not post to LMS and does not write to intervention
    history, because it is still an experiment flow.
    """
    settings = get_settings()
    selected_models = models or _get_eval_models()
    lms_backend = LMSBackend.for_key(settings.lms_backend)
    if lms_backend is None:
        raise ValueError(
            "LMS experiments require FACILITATION_LMS_BACKEND."
        )

    records: list[dict[str, object]] = []
    for model_name in selected_models:
        model_settings = settings.model_copy(
            update={
                "llm_model": model_name,
                "history_backend": "memory",
            }
        )
        deps = PipelineDeps(settings=model_settings, lms_backend=lms_backend)

        for thread_id in thread_ids:
            started_at = perf_counter()
            try:
                thread = await lms_backend.get_thread(thread_id)
                result = await run_pipeline(thread, deps)
                duration_seconds = perf_counter() - started_at
                records.append(
                    _live_run_record(
                        model_name=model_name,
                        thread=thread,
                        outcome=FacilitationOutcome(
                            result=result,
                            comment_posted=False,
                        ),
                        duration_seconds=duration_seconds,
                    )
                )
            except Exception as exc:
                duration_seconds = perf_counter() - started_at
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
                        "error": str(exc),
                        "duration_seconds": duration_seconds,
                    }
                )

    summary_lines = [
        "# LMS Experiment Summary",
        "",
        f"Run: {run_name}",
        f"Models: {len(selected_models)}",
        f"Threads: {len(thread_ids)}",
        f"Records: {len(records)}",
    ]
    summary_markdown = "\n".join(summary_lines) + "\n"
    (out_dir / "summary.md").write_text(summary_markdown, encoding="utf-8")

    write_run_manifest(
        out_dir,
        run_id=out_dir.name,
        run_name=run_name or out_dir.name,
        timestamp=datetime.now(UTC).isoformat(),
        records=records,
        run_type="experiment",
        status="completed",
        store=result_store,
        summary_markdown=summary_markdown,
    )


@router.post(
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

    write_run_manifest(
        out_dir,
        run_id=dir_name,
        run_name=request.run_name or dir_name,
        timestamp=datetime.strptime(timestamp, "%Y-%m-%dT%H-%M")
        .replace(tzinfo=UTC)
        .isoformat(),
        records=[],
        status="running",
        store=run_result_store,
    )

    if not request.threads or all(
        thread in ALL_THREADS for thread in request.threads
    ):
        background_tasks.add_task(
            _run_experiment_background,
            models=request.models,
            run_name=request.run_name,
            threads=request.threads,
            out_dir=out_dir,
            result_store=run_result_store,
        )
    else:
        background_tasks.add_task(
            _run_lms_experiment_background,
            models=request.models,
            run_name=request.run_name,
            thread_ids=request.threads,
            out_dir=out_dir,
            result_store=run_result_store,
        )

    return TriggerRunResponse(run_id=dir_name)


@router.post(
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

    thread = await lms_backend.get_thread(request.thread_id)
    run_result_store = _resolve_run_result_store()
    run_id = _live_run_id(request.thread_id)
    timestamp = datetime.now(UTC).isoformat()
    run_name = request.run_name.strip() or run_id

    if thread.closed:
        out_dir = RESULTS_DIR / run_id
        out_dir.mkdir(parents=True, exist_ok=True)
        write_run_manifest(
            out_dir,
            run_id=run_id,
            run_name=run_name,
            timestamp=timestamp,
            records=[],
            run_type="live",
            status="noop",
            store=run_result_store,
        )
        return LiveTriggerRunResponse(
            run_id=run_id,
            status="noop",
            thread_id=request.thread_id,
        )

    started_at = perf_counter()
    outcome = await facilitate_and_post(request.thread_id)
    duration_seconds = perf_counter() - started_at

    out_dir = RESULTS_DIR / run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    live_record = _live_run_record(
        model_name=settings.llm_model,
        thread=thread,
        outcome=outcome,
        duration_seconds=duration_seconds,
    )
    write_run_manifest(
        out_dir,
        run_id=run_id,
        run_name=run_name,
        timestamp=timestamp,
        records=[live_record],
        run_type="live",
        status="completed",
        store=run_result_store,
    )

    return LiveTriggerRunResponse(
        run_id=run_id,
        status="completed",
        thread_id=request.thread_id,
        comment_posted=outcome.comment_posted,
        comment_id=outcome.comment_id,
    )


@router.get(
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


@router.get(
    "/runs/{run_id}",
    response_model=EvalRunDetail,
    status_code=status.HTTP_200_OK,
)
@router.get(
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
