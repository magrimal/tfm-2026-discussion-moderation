"""HTTP routes for the facilitation service."""

import asyncio
import re
from datetime import UTC, datetime
from pathlib import Path

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
from discussion_moderation.models import (
    DiscussionThread,
    PipelineResult,
)


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
) -> None:
    """Wrapper that imports run_experiment lazily to keep router lean."""
    from discussion_moderation.evals.eval_models import run_experiment

    await run_experiment(
        models=models,
        run_name=run_name,
        threads=threads,
        out_dir=out_dir,
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

    write_run_manifest(
        out_dir,
        run_id=dir_name,
        run_name=request.run_name or dir_name,
        timestamp=datetime.strptime(timestamp, "%Y-%m-%dT%H-%M")
        .replace(tzinfo=UTC)
        .isoformat(),
        records=[],
        status="running",
    )

    background_tasks.add_task(
        _run_experiment_background,
        models=request.models,
        run_name=request.run_name,
        threads=request.threads,
        out_dir=out_dir,
    )

    return TriggerRunResponse(run_id=dir_name)


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
