"""Model comparison experiment runner.

Runs the facilitation pipeline across multiple free-tier models and
all built-in thread scenarios. Writes structured JSON results and a
markdown summary to docs/experiments/results/<timestamp>/.

Usage:
    uv run --env-file .env eval-models

The LLM_API_KEY env var must be an OpenRouter key for the default
model list. Override EVAL_MODELS (comma-separated) to test different
model strings.

Rate limiting: calls are sequential with a configurable inter-call
delay (EVAL_DELAY_SECONDS, default 3). On 429 / rate-limit errors,
the runner retries up to 3 times with exponential back-off.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import re
import time
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path

import httpx
import pydantic

from discussion_moderation.config import Settings
from discussion_moderation.evals.artifacts import write_run_manifest
from discussion_moderation.evals.fixtures.threads import ALL_THREADS
from discussion_moderation.evals.store import RunResultStore, load_manifest
from discussion_moderation.graph.nodes import ClassificationNode
from discussion_moderation.graph.pipeline import facilitation_graph
from discussion_moderation.models import PipelineDeps, PipelineState

logger = logging.getLogger(__name__)

DEFAULT_MODELS = [
    "openrouter:openai/gpt-oss-120b:free",
    "openrouter:google/gemma-4-31b-it:free",
    "openrouter:qwen/qwen3-coder:free",
    "openrouter:meta-llama/llama-3.3-70b-instruct:free",
    "openrouter:cognitivecomputations/dolphin-mistral-24b-venice-edition:free",
    "openrouter:nousresearch/hermes-3-llama-3.1-405b:free",
]

OPENROUTER_MODELS_URL = "https://openrouter.ai/api/v1/models"

RESULTS_DIR = Path(__file__).parents[2] / "docs" / "experiments" / "results"


@dataclass
class RunRecord:
    """Result of one pipeline run against one thread with one model."""

    model: str
    thread: str
    thread_title: str
    # Classification
    state: str | None
    trajectory: str | None
    participation_balance: str | None
    discourse_quality: str | None
    inquiry_phase: str | None
    classification_reasoning: str | None
    # Intervention
    should_intervene: bool | None
    intervention_reasoning: str | None
    # Role selection
    role: str | None
    role_reasoning: str | None
    # Confidence per stage (self-assessed, research parameter only)
    classification_confidence: float | None
    intervention_confidence: float | None
    role_confidence: float | None
    # Facilitation response
    technique: str | None
    action_category: str | None
    response_confidence: float | None
    post_to_thread: bool | None
    response_reasoning: str | None
    response_text: str | None
    # Meta
    error: str | None
    raw_response: str | None
    duration_seconds: float
    messages: list[dict] = field(default_factory=list)
    pipeline_messages: dict[str, list[dict]] = field(default_factory=dict)


def _slug(model: str) -> str:
    """Convert a model string to a filename-safe slug."""
    return re.sub(r"[^a-zA-Z0-9_-]", "_", model)


async def _run_once(
    model_str: str,
    thread_name: str,
    api_key: str,
    delay_seconds: float,
    max_retries: int = 3,
) -> RunRecord:
    """Run the pipeline for one model/thread pair with retry on rate limit.

    Args:
        model_str: Provider-prefixed model string.
        thread_name: Thread fixture name from ALL_THREADS.
        api_key: API key forwarded to the provider.
        delay_seconds: Seconds to wait before the call.
        max_retries: Maximum retry attempts on rate-limit errors.

    Returns:
        RunRecord with the result or error details.
    """
    await asyncio.sleep(delay_seconds)

    settings = Settings(
        llm_model=model_str,
        llm_api_key=api_key,
        lms_backend="stub",
        history_backend="memory",
        response_eval_enabled=False,
    )
    deps = PipelineDeps(settings=settings)
    thread = ALL_THREADS[thread_name]()

    def build_record(
        state: PipelineState,
        error: str | None,
        duration: float,
    ) -> RunRecord:
        """Build a RunRecord from whatever pipeline state was populated."""
        classification = state.classification
        intervention = state.intervention
        role_selection = state.role_selection
        response = state.response
        return RunRecord(
            model=model_str,
            thread=thread_name,
            thread_title=thread.title,
            state=classification.state.value if classification else None,
            trajectory=(
                classification.trajectory.value if classification else None
            ),
            participation_balance=(
                classification.participation_balance.value
                if classification
                else None
            ),
            discourse_quality=(
                classification.discourse_quality.value
                if classification
                else None
            ),
            inquiry_phase=(
                classification.inquiry_phase.value if classification else None
            ),
            classification_reasoning=(
                classification.reasoning if classification else None
            ),
            should_intervene=(
                intervention.should_intervene if intervention else None
            ),
            intervention_reasoning=(
                intervention.reasoning if intervention else None
            ),
            role=role_selection.role.value if role_selection else None,
            role_reasoning=role_selection.reasoning if role_selection else None,
            classification_confidence=(
                classification.confidence if classification else None
            ),
            intervention_confidence=(
                intervention.confidence if intervention else None
            ),
            role_confidence=(
                role_selection.confidence if role_selection else None
            ),
            technique=response.technique_used if response else None,
            action_category=(
                response.action_category.value if response else None
            ),
            response_confidence=response.confidence if response else None,
            post_to_thread=response.post_to_thread if response else None,
            response_reasoning=response.reasoning if response else None,
            response_text=response.response_text if response else None,
            error=error,
            raw_response=state.raw_response,
            duration_seconds=round(duration, 2),
            messages=state.messages,
            pipeline_messages=state.pipeline_messages,
        )

    for attempt in range(max_retries):
        start = time.monotonic()
        state = PipelineState(thread=thread)
        try:
            await facilitation_graph.run(
                start_node=ClassificationNode(),
                state=state,
                deps=deps,
            )
            duration = time.monotonic() - start
            # state was mutated in-place by the graph nodes
            return build_record(state, None, duration)
        except Exception as exc:
            logger.exception(
                "Error on attempt %d for model %s / thread %s: %s",
                attempt + 1,
                model_str,
                thread_name,
                exc,
            )
            duration = time.monotonic() - start
            exc_str = str(exc)

            is_rate_limit = (
                "429" in exc_str
                or "rate" in exc_str.lower()
                or "quota" in exc_str.lower()
            )

            if is_rate_limit and attempt < max_retries - 1:
                wait = 10.0 * (2**attempt)
                logger.warning(
                    "[%s/%s] Rate limited (attempt %d). Retrying in %.0fs...",
                    model_str,
                    thread_name,
                    attempt + 1,
                    wait,
                )
                await asyncio.sleep(wait)
                continue

            # Walk the exception chain for the raw model text.
            # json.JSONDecodeError.doc has the string that failed to parse;
            # pydantic.ValidationError str() includes the failing input.
            raw: str | None = None
            cause: BaseException | None = exc
            while cause is not None:
                if isinstance(cause, json.JSONDecodeError) and cause.doc:
                    raw = cause.doc
                    break
                if isinstance(cause, pydantic.ValidationError):
                    raw = str(cause)
                    break
                body = getattr(cause, "body", None)
                if body:
                    raw = str(body)
                    break
                cause = cause.__cause__

            state.raw_response = raw
            logger.error("[%s/%s] Failed: %s", model_str, thread_name, exc_str)
            if raw:
                logger.error(
                    "[%s/%s] Raw model output: %s", model_str, thread_name, raw
                )
            # state holds whatever nodes completed before the failure
            return build_record(state, exc_str, duration)

    return build_record(
        PipelineState(thread=thread), "Max retries exceeded", 0.0
    )


def _details_block(
    summary_label: str, *sections: tuple[str, str | None]
) -> list[str]:
    """Build a collapsible <details> block with labelled sections.

    Args:
        summary_label: Text for the <summary> tag.
        sections: (label, content) pairs; None content sections are skipped.

    Returns:
        Lines for the markdown block.
    """
    body: list[str] = []
    for label, content in sections:
        if content:
            body += [f"**{label}**", "", content, ""]

    if not body:
        return []

    return [
        f"<details><summary>{summary_label}</summary>",
        "",
        *body,
        "</details>",
        "",
    ]


def _write_summary(
    out_dir: Path, records: list[RunRecord], models: list[str]
) -> None:
    """Write docs/experiments/results/<dir>/summary.md.

    Args:
        out_dir: Directory containing the run.
        records: All run records.
        models: Ordered list of models tested.
    """
    lines: list[str] = [
        "# Model Comparison — Experiment Summary",
        "",
        f"**Date**: {datetime.now(UTC).strftime('%Y-%m-%d %H:%M UTC')}",
        f"**Models**: {len(models)}",
        f"**Threads**: {len(ALL_THREADS)}",
        f"**Total runs**: {len(records)}",
        "",
        "## Results by model",
        "",
    ]

    by_model: dict[str, list[RunRecord]] = {}
    for r in records:
        by_model.setdefault(r.model, []).append(r)

    for model in models:
        model_records = by_model.get(model, [])
        errors = [r for r in model_records if r.error]
        ok = [r for r in model_records if not r.error]
        total_dur = sum(r.duration_seconds for r in model_records)
        avg_duration = (
            round(total_dur / len(model_records), 1) if model_records else 0.0
        )
        run_summary = f"{len(ok)} ok, {len(errors)} errors"

        lines += [
            f"### `{model}`",
            "",
            f"- Runs: {len(model_records)} ({run_summary})",
            f"- Avg duration: {avg_duration}s",
            "",
            "| Thread | State | Trajectory | Balance"
            " | Intervene | Role | Technique | c_conf | i_conf | r_conf |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        ]

        for r in model_records:
            intervene = (
                str(r.should_intervene)
                if r.should_intervene is not None
                else "-"
            )
            c_conf = (
                f"{r.classification_confidence:.2f}"
                if r.classification_confidence is not None
                else "-"
            )
            i_conf = (
                f"{r.intervention_confidence:.2f}"
                if r.intervention_confidence is not None
                else "-"
            )
            r_conf = (
                f"{r.response_confidence:.2f}"
                if r.response_confidence is not None
                else "-"
            )
            lines.append(
                f"| {r.thread} — *{r.thread_title}* | {r.state or 'ERROR'}"
                f" | {r.trajectory or '-'}"
                f" | {r.participation_balance or '-'}"
                f" | {intervene}"
                f" | {r.role or '-'}"
                f" | {r.technique or '-'}"
                f" | {c_conf} | {i_conf} | {r_conf} |"
            )

        lines.append("")

        for r in model_records:
            if r.error:
                lines += _details_block(
                    f"{r.thread}: error",
                    ("Error", f"```\n{r.error[:500]}\n```"),
                    (
                        "Raw model output",
                        f"```\n{r.raw_response}\n```"
                        if r.raw_response
                        else None,
                    ),
                )
            else:
                lines += _details_block(
                    f"{r.thread}: full pipeline output",
                    ("Classification reasoning", r.classification_reasoning),
                    ("Intervention reasoning", r.intervention_reasoning),
                    ("Role reasoning", r.role_reasoning),
                    ("Response reasoning", r.response_reasoning),
                    ("Response text", r.response_text),
                )

    # Cross-model comparison by thread
    thread_names = list(ALL_THREADS)
    by_thread: dict[str, list[RunRecord]] = {}
    for r in records:
        by_thread.setdefault(r.thread, []).append(r)

    lines += [
        "## Cross-model comparison by thread",
        "",
    ]

    for thread_name in thread_names:
        thread_records = by_thread.get(thread_name, [])
        title = ALL_THREADS[thread_name]().title
        lines += [
            f"### {thread_name} — {title}",
            "",
            "| Model | State | Intervene | Role | Technique |",
            "| --- | --- | --- | --- | --- |",
        ]
        for r in thread_records:
            if r.should_intervene is not None:
                intervene = str(r.should_intervene)
            else:
                intervene = "-"
            lines.append(
                f"| `{r.model}` | {r.state or 'ERROR'}"
                f" | {intervene}"
                f" | {r.role or '-'}"
                f" | {r.technique or '-'} |"
            )
        lines.append("")

        for r in thread_records:
            if r.response_text:
                lines += _details_block(
                    f"{r.model}: response",
                    ("Response text", r.response_text),
                )

    lines += [
        "## Observations",
        "",
        "*(Fill in after reviewing results.)*",
        "",
        "## Conclusions",
        "",
        "*(Fill in after reviewing results.)*",
    ]

    (out_dir / "summary.md").write_text("\n".join(lines), encoding="utf-8")


async def validate_openrouter_models(
    models: list[str], api_key: str
) -> list[str]:
    """Check which models exist on OpenRouter and return the valid subset.

    Fetches the OpenRouter model catalogue and filters the requested list
    to only those that appear in it. Logs a warning for each missing model.
    Returns the valid subset so the experiment can proceed with whatever
    is available, rather than failing completely.

    Args:
        models: Provider-prefixed model strings, e.g.
            ["openrouter:google/gemma-4-31b-it:free"].
        api_key: OpenRouter API key, used in the Authorization header.

    Returns:
        Subset of models that exist in the OpenRouter catalogue.
    """
    openrouter_ids = {m for m in models if m.startswith("openrouter:")}
    if not openrouter_ids:
        return models

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                OPENROUTER_MODELS_URL,
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=10.0,
            )
            response.raise_for_status()
        catalogue = {m["id"] for m in response.json().get("data", [])}
    except Exception as exc:
        logger.warning(
            "Could not fetch OpenRouter model catalogue (%s). "
            "Skipping availability check.",
            exc,
        )
        return models

    valid: list[str] = []
    for model in models:
        if not model.startswith("openrouter:"):
            valid.append(model)
            continue
        model_id = model.removeprefix("openrouter:")
        if model_id in catalogue:
            logger.info("  [ok] %s", model)
            valid.append(model)
        else:
            logger.warning(
                "  [not in catalogue] %s: will attempt anyway",
                model,
            )
            valid.append(model)

    return valid


async def run_experiment(
    models: list[str] | None = None,
    delay_seconds: float = 3.0,
    run_name: str = "",
    threads: list[str] | None = None,
    out_dir: Path | None = None,
    result_store: RunResultStore | None = None,
) -> list[RunRecord]:
    """Run the full model comparison experiment.

    Args:
        models: Model strings to test. Defaults to DEFAULT_MODELS.
        delay_seconds: Seconds to wait between consecutive API calls.
        run_name: Human-readable name for this run. Falls back to
            EVAL_NAME env var.
        threads: Thread fixture keys to include. Defaults to all
            threads (or EVAL_THREADS env var).
        out_dir: Pre-computed output directory. Created from
            timestamp + name if omitted.
        result_store: Optional run result store to mirror persisted
            run manifests (e.g., mongo).

    Returns:
        All RunRecords from the experiment.
    """
    if models is None:
        env_models = os.environ.get("EVAL_MODELS", "")
        models = [
            m.strip() for m in env_models.split(",") if m.strip()
        ] or DEFAULT_MODELS

    api_key = os.environ.get("LLM_API_KEY", "")
    if not api_key:
        raise ValueError(
            "LLM_API_KEY is required. Set it in .env or the environment."
        )

    logger.info("Checking model availability on OpenRouter...")
    models = await validate_openrouter_models(models, api_key)
    if not models:
        raise ValueError("No valid models found. Aborting.")

    if threads is None:
        env_threads = os.environ.get("EVAL_THREADS", "")
        threads = [
            t.strip() for t in env_threads.split(",") if t.strip()
        ] or list(ALL_THREADS)
    thread_names = threads
    unknown = [t for t in thread_names if t not in ALL_THREADS]
    if unknown:
        raise ValueError(
            f"Unknown thread(s): {unknown}. Available: {list(ALL_THREADS)}"
        )

    total = len(models) * len(thread_names)
    logger.info(
        "Starting experiment: %d models x %d threads = %d runs",
        len(models),
        len(thread_names),
        total,
    )

    if out_dir is None:
        if not run_name:
            run_name = os.environ.get("EVAL_NAME", "").strip()
        run_name_slug = (
            re.sub(r"[^a-zA-Z0-9_-]", "-", run_name) if run_name else ""
        )
        timestamp = datetime.now(UTC).strftime("%Y-%m-%dT%H-%M")
        dir_name = (
            f"{timestamp}-{run_name_slug}" if run_name_slug else timestamp
        )
        out_dir = RESULTS_DIR / dir_name
        out_dir.mkdir(parents=True, exist_ok=True)
    else:
        dir_name = out_dir.name
        out_dir.mkdir(parents=True, exist_ok=True)
        ts_match = re.match(r"^(\d{4}-\d{2}-\d{2}T\d{2}-\d{2})", dir_name)
        timestamp = (
            ts_match.group(1)
            if ts_match
            else datetime.now(UTC).strftime("%Y-%m-%dT%H-%M")
        )
    logger.info("Writing results to %s", out_dir)

    log_handler = logging.FileHandler(out_dir / "run.log", encoding="utf-8")
    log_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S"
        )
    )
    logging.getLogger().addHandler(log_handler)

    records: list[RunRecord] = []
    count = 0
    cancelled = False

    write_run_manifest(
        out_dir,
        run_id=dir_name,
        run_name=run_name or dir_name,
        timestamp=datetime.strptime(timestamp, "%Y-%m-%dT%H-%M")
        .replace(tzinfo=UTC)
        .isoformat(),
        records=[],
        status="running",
        progress_message="Preparing experiment run...",
        expected_model_count=len(models),
        expected_thread_count=len(thread_names),
        expected_total_runs=total,
        store=result_store,
    )

    try:
        for model in models:
            for thread_name in thread_names:
                current = load_manifest(out_dir)
                if current is not None and current.status == "cancelling":
                    cancelled = True
                    break
                count += 1
                logger.info("[%d/%d] %s / %s", count, total, model, thread_name)
                record = await _run_once(
                    model_str=model,
                    thread_name=thread_name,
                    api_key=api_key,
                    delay_seconds=delay_seconds if count > 1 else 0.0,
                )
                records.append(record)

                filename = f"{_slug(record.model)}__{record.thread}.json"
                (out_dir / filename).write_text(
                    json.dumps(asdict(record), indent=2), encoding="utf-8"
                )

                write_run_manifest(
                    out_dir,
                    run_id=dir_name,
                    run_name=run_name or dir_name,
                    timestamp=datetime.strptime(timestamp, "%Y-%m-%dT%H-%M")
                    .replace(tzinfo=UTC)
                    .isoformat(),
                    records=[asdict(r) for r in records],
                    status="running" if count < total else "completed",
                    progress_message=(
                        f"[{count}/{total}] {model} / {thread_name}"
                        if count < total
                        else "Finalizing summary..."
                    ),
                    expected_model_count=len(models),
                    expected_thread_count=len(thread_names),
                    expected_total_runs=total,
                    store=result_store,
                )

                status = "ok" if not record.error else "ERROR"
                logger.info(
                    "  -> %s | state=%s intervene=%s role=%s (%.1fs)",
                    status,
                    record.state,
                    record.should_intervene,
                    record.role,
                    record.duration_seconds,
                )
            if cancelled:
                logger.info("Run cancelled after %d/%d steps.", count, total)
                break
    except (KeyboardInterrupt, asyncio.CancelledError):
        logger.warning(
            "Interrupted after %d/%d runs. Writing partial summary...",
            len(records),
            total,
        )
    finally:
        if records:
            _write_summary(out_dir, records, models)
            summary_markdown = (out_dir / "summary.md").read_text(
                encoding="utf-8"
            )
            write_run_manifest(
                out_dir,
                run_id=dir_name,
                run_name=run_name or dir_name,
                timestamp=datetime.strptime(timestamp, "%Y-%m-%dT%H-%M")
                .replace(tzinfo=UTC)
                .isoformat(),
                records=[asdict(record) for record in records],
                status=(
                    "cancelled"
                    if cancelled
                    else "completed"
                    if len(records) == total
                    else "partial"
                ),
                progress_message=None,
                expected_model_count=len(models),
                expected_thread_count=len(thread_names),
                expected_total_runs=total,
                store=result_store,
                summary_markdown=summary_markdown,
            )
            logger.info("Summary written to %s", out_dir)
        logging.getLogger().removeHandler(log_handler)
        log_handler.close()

    errors = sum(1 for r in records if r.error)
    logger.info(
        "Done: %d/%d succeeded, %d errors",
        len(records),
        total,
        errors,
    )

    return records


def main() -> None:
    """Entry point for the eval-models script."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )
    # Suppress noisy third-party loggers, keep our own at INFO.
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("discussion_moderation").setLevel(logging.INFO)

    if os.environ.get("LOGFIRE_TOKEN"):
        import logfire

        logfire.configure()
        logfire.instrument_pydantic_ai()

    delay = float(os.environ.get("EVAL_DELAY_SECONDS", "3"))
    asyncio.run(run_experiment(delay_seconds=delay))
