"""Validate, join, and summarize blinded LLM-judge outputs."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from statistics import mean
from typing import Any

DIMENSIONS = (
    "relevance_and_grounding",
    "intervention_necessity_and_timing",
    "cognitive_activation",
    "dialogic_openness",
    "social_safety_and_inclusion",
    "scaffolding_and_next_step",
    "facilitation_function_fidelity",
    "clarity_and_response_load",
)
CRITICAL_CHECKS = (
    "hallucination_detected",
    "evaluative_or_grading_language",
    "unsafe_moderation_or_publication",
)


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def summarize_results(
    run_dir: Path,
    batch_paths: list[Path],
) -> dict[str, Any]:
    """Validate judge batches and write joined scores and summaries."""
    cases = {
        row["case_id"]: row
        for row in (
            json.loads(line)
            for line in (run_dir / "judge_cases.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
            if line
        )
    }
    case_map = _load_json(run_dir / "case_map.json")

    evaluations: list[dict[str, Any]] = []
    for path in batch_paths:
        evaluations.extend(_load_json(path)["evaluations"])

    ids = [item["case_id"] for item in evaluations]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate case_id in judge outputs")
    if set(ids) != set(cases):
        missing = sorted(set(cases) - set(ids))
        extra = sorted(set(ids) - set(cases))
        raise ValueError(f"Case mismatch; missing={missing}, extra={extra}")

    joined: list[dict[str, Any]] = []
    for item in evaluations:
        applicable = [
            score for score in item["scores"].values() if score is not None
        ]
        calculated_mean = round(mean(applicable), 3)
        if abs(calculated_mean - item["mean_score"]) > 0.001:
            raise ValueError(
                f"{item['case_id']}: mean {item['mean_score']} "
                f"!= {calculated_mean}"
            )
        has_critical = any(item["critical_checks"].values())
        has_one = any(score == 1 for score in applicable)
        if item["requires_review"] != (has_critical or has_one):
            raise ValueError(
                f"{item['case_id']}: inconsistent requires_review"
            )

        mapping = case_map[item["case_id"]]
        joined.append({**mapping, **item})

    joined.sort(key=lambda item: (item["model"], item["thread_key"]))
    (run_dir / "judge_scores.jsonl").write_text(
        "".join(json.dumps(item, ensure_ascii=False) + "\n" for item in joined),
        encoding="utf-8",
    )

    by_model: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in joined:
        by_model[item["model"]].append(item)

    model_summaries: dict[str, Any] = {}
    for model, items in sorted(by_model.items()):
        dimension_means = {}
        for dimension in DIMENSIONS:
            values = [
                item["scores"][dimension]
                for item in items
                if item["scores"][dimension] is not None
            ]
            dimension_means[dimension] = (
                round(mean(values), 3) if values else None
            )
        model_summaries[model] = {
            "evaluated_interventions": len(items),
            "mean_score": round(mean(i["mean_score"] for i in items), 3),
            "requires_review": sum(i["requires_review"] for i in items),
            "critical_checks": {
                check: sum(i["critical_checks"][check] for i in items)
                for check in CRITICAL_CHECKS
            },
            "dimension_means": dimension_means,
        }

    summary = {
        "judge_model": "codex:gpt-5.6-sol",
        "evaluated_at": datetime.now(UTC).isoformat(),
        "evaluated_cases": len(joined),
        "requires_review": sum(item["requires_review"] for item in joined),
        "critical_checks": {
            check: sum(item["critical_checks"][check] for item in joined)
            for check in CRITICAL_CHECKS
        },
        "overall_mean_score": round(
            mean(item["mean_score"] for item in joined), 3
        ),
        "scope_note": (
            "Scores are conditional on a generated intervention. Model sample "
            "sizes differ, so means do not form a controlled model ranking."
        ),
        "batch_sha256": {
            path.name: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in batch_paths
        },
        "models": model_summaries,
    }
    (run_dir / "judge_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    lines = [
        "# LLM-as-judge summary",
        "",
        f"- Judge: `{summary['judge_model']}`",
        f"- Evaluated interventions: {summary['evaluated_cases']}",
        f"- Overall mean: {summary['overall_mean_score']:.3f}/5",
        f"- Cases requiring review: {summary['requires_review']}",
        f"- Hallucinations detected: "
        f"{summary['critical_checks']['hallucination_detected']}",
        f"- Evaluative/grading language: "
        f"{summary['critical_checks']['evaluative_or_grading_language']}",
        f"- Unsafe moderation/publication: "
        f"{summary['critical_checks']['unsafe_moderation_or_publication']}",
        "",
        "## By model",
        "",
        "| Model | n | Mean | Review | Hallucination | Evaluative | Unsafe |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for model, item in model_summaries.items():
        checks = item["critical_checks"]
        lines.append(
            f"| `{model}` | {item['evaluated_interventions']} | "
            f"{item['mean_score']:.3f} | {item['requires_review']} | "
            f"{checks['hallucination_detected']} | "
            f"{checks['evaluative_or_grading_language']} | "
            f"{checks['unsafe_moderation_or_publication']} |"
        )
    lines.extend(
        [
            "",
            "The scores estimate ex-ante adequacy under the documented rubric. "
            "They do not measure effects on subsequent discussion or learning.",
            "",
            "Only runs that generated an intervention were scored. "
            "Sample sizes therefore differ by model, and these means must not "
            "be interpreted as a controlled model ranking. DeepSeek produced "
            "no scoreable intervention before its EC2 run was cancelled.",
            "",
        ]
    )
    (run_dir / "judge_summary.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )
    return summary


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("batches", nargs="+", type=Path)
    args = parser.parse_args()
    summary = summarize_results(args.run_dir, args.batches)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
