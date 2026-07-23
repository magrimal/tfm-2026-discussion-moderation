"""Prepare anonymized LLM-judge inputs from experiment manifests."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

DEFAULT_PROMPT = (
    Path(__file__).parents[2] / "docs" / "experiments" / "llm-judge-prompt.md"
)


def _case_id(run_id: str, model: str, thread_key: str) -> str:
    """Return a stable opaque identifier without revealing the model."""
    source = f"{run_id}\0{model}\0{thread_key}".encode()
    return f"case-{hashlib.sha256(source).hexdigest()[:16]}"


def _iter_threads(manifest: dict[str, Any]):
    for model_name, model_result in manifest.get("models", {}).items():
        for thread_key, result in model_result.get("threads", {}).items():
            yield model_name, thread_key, result


def prepare_inputs(
    manifest_paths: list[Path],
    output_dir: Path,
    prompt_path: Path = DEFAULT_PROMPT,
) -> dict[str, Any]:
    """Write blinded judge cases, a private map, and run metadata."""
    output_dir.mkdir(parents=True, exist_ok=True)
    prompt_bytes = prompt_path.read_bytes()
    prompt_hash = hashlib.sha256(prompt_bytes).hexdigest()

    cases: list[dict[str, Any]] = []
    case_map: dict[str, dict[str, str]] = {}
    source_runs: list[str] = []
    expected_cases = 0
    observed_cases = 0
    excluded_no_response = 0
    excluded_error = 0

    for manifest_path in manifest_paths:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        run_id = str(manifest["run_id"])
        source_runs.append(run_id)
        expected_cases += int(manifest.get("total_runs", 0))

        for model_name, thread_key, result in _iter_threads(manifest):
            observed_cases += 1
            if result.get("error"):
                excluded_error += 1
                continue
            response = result.get("response")
            if not response or not response.get("text"):
                excluded_no_response += 1
                continue

            case_id = _case_id(run_id, model_name, thread_key)
            classification = result.get("classification") or {}
            intervention = result.get("intervention") or {}
            cases.append(
                {
                    "case_id": case_id,
                    "thread": {
                        "title": result.get("thread_title"),
                        "body": result.get("thread_body"),
                        "comments": result.get("thread_comments") or [],
                    },
                    "pipeline_decision": {
                        "assigned_state": classification.get("state"),
                        "role": intervention.get("role"),
                        "technique": intervention.get("technique"),
                        "action_category": response.get("action_category"),
                        "post_to_thread": intervention.get("post_to_thread"),
                    },
                    "response_text": response["text"],
                }
            )
            case_map[case_id] = {
                "run_id": run_id,
                "model": model_name,
                "thread_key": thread_key,
            }

    cases.sort(key=lambda item: item["case_id"])
    metadata = {
        "judge_model": "codex:gpt-5.6-sol",
        "prepared_at": datetime.now(UTC).isoformat(),
        "prompt_path": str(prompt_path),
        "prompt_sha256": prompt_hash,
        "source_runs": source_runs,
        "expected_executions": expected_cases,
        "observed_executions": observed_cases,
        "unrecorded_executions": max(expected_cases - observed_cases, 0),
        "included_cases": len(cases),
        "excluded_error": excluded_error,
        "excluded_no_response": excluded_no_response,
        "blinded_fields": ["model"],
    }

    cases_path = output_dir / "judge_cases.jsonl"
    cases_path.write_text(
        "".join(json.dumps(case, ensure_ascii=False) + "\n" for case in cases),
        encoding="utf-8",
    )
    (output_dir / "case_map.json").write_text(
        json.dumps(case_map, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (output_dir / "judge_run.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return metadata


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Prepare blinded LLM-judge inputs from run manifests."
    )
    parser.add_argument(
        "manifests",
        nargs="+",
        type=Path,
        help="Paths to run_manifest.json files.",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        type=Path,
        help="Directory for judge_cases.jsonl and metadata.",
    )
    parser.add_argument(
        "--prompt",
        type=Path,
        default=DEFAULT_PROMPT,
        help="Judge prompt whose SHA-256 is recorded.",
    )
    args = parser.parse_args()
    metadata = prepare_inputs(args.manifests, args.output_dir, args.prompt)
    print(json.dumps(metadata, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
