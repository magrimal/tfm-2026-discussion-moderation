"""Tests for preparing blinded LLM-judge inputs."""

from __future__ import annotations

import json
from pathlib import Path

from discussion_moderation.evals.prepare_judge_inputs import prepare_inputs


def test_prepare_inputs_blinds_model_and_excludes_non_responses(
    tmp_path: Path,
) -> None:
    manifest = {
        "run_id": "run-1",
        "total_runs": 4,
        "models": {
            "provider:model-a": {
                "threads": {
                    "answered": {
                        "thread_title": "Title",
                        "thread_body": "Opening",
                        "thread_comments": [{"author": "A", "body": "Comment"}],
                        "classification": {"state": "stalled"},
                        "intervention": {
                            "role": "intellectual",
                            "technique": "solicit_evidence",
                            "post_to_thread": True,
                        },
                        "response": {
                            "text": "What evidence supports that claim?",
                            "action_category": "intellectual",
                        },
                        "error": None,
                    },
                    "silent": {
                        "response": None,
                        "error": None,
                    },
                    "failed": {
                        "response": None,
                        "error": "timeout",
                    },
                }
            }
        },
    }
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    prompt_path = tmp_path / "prompt.md"
    prompt_path.write_text("rubric", encoding="utf-8")
    output_dir = tmp_path / "judge"

    metadata = prepare_inputs([manifest_path], output_dir, prompt_path)

    cases = [
        json.loads(line)
        for line in (output_dir / "judge_cases.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    ]
    assert len(cases) == 1
    assert "model" not in json.dumps(cases[0])
    assert cases[0]["case_id"].startswith("case-")
    assert cases[0]["pipeline_decision"]["assigned_state"] == "stalled"

    case_map = json.loads(
        (output_dir / "case_map.json").read_text(encoding="utf-8")
    )
    assert next(iter(case_map.values()))["model"] == "provider:model-a"
    assert metadata["included_cases"] == 1
    assert metadata["observed_executions"] == 3
    assert metadata["unrecorded_executions"] == 1
    assert metadata["excluded_no_response"] == 1
    assert metadata["excluded_error"] == 1
