"""Evaluation suite for the facilitator agent.

Runs the agent against sample threads and checks whether:
- The discussion state is classified correctly.
- The intervention decision makes sense.
- The selected action category is appropriate.

Usage:
    uv run python -m discussion_moderation.evals.eval_facilitator
"""

from dataclasses import dataclass

from pydantic_evals import Case, Dataset

from discussion_moderation.agents.facilitator import facilitate
from discussion_moderation.evals.sample_threads import (
    ALL_THREADS,
)
from discussion_moderation.schemas.discussion import (
    DiscussionState,
    DiscussionThread,
    FacilitationResult,
)


@dataclass
class ExpectedBehavior:
    """What we expect the agent to do for a given thread."""

    expected_state: DiscussionState
    should_intervene: bool
    acceptable_categories: list[str] | None = None


EXPECTATIONS: dict[str, ExpectedBehavior] = {
    "new": ExpectedBehavior(
        expected_state=DiscussionState.NEW,
        should_intervene=True,
        acceptable_categories=["organizational", "social"],
    ),
    "active": ExpectedBehavior(
        expected_state=DiscussionState.ACTIVE,
        should_intervene=False,
    ),
    "stalled": ExpectedBehavior(
        expected_state=DiscussionState.STALLED,
        should_intervene=True,
        acceptable_categories=[
            "social",
            "intellectual",
            "organizational",
        ],
    ),
    "conflictive": ExpectedBehavior(
        expected_state=DiscussionState.CONFLICTIVE,
        should_intervene=True,
        acceptable_categories=["social", "moderation"],
    ),
    "convergent": ExpectedBehavior(
        expected_state=DiscussionState.CONVERGENT,
        should_intervene=False,
    ),
    "off_topic": ExpectedBehavior(
        expected_state=DiscussionState.OFF_TOPIC,
        should_intervene=True,
        acceptable_categories=["organizational"],
    ),
}


def build_dataset() -> Dataset[
    DiscussionThread, FacilitationResult, ExpectedBehavior
]:
    """Build the evaluation dataset from sample threads."""
    cases = []
    for name, thread_fn in ALL_THREADS.items():
        expected = EXPECTATIONS[name]
        cases.append(
            Case(
                name=name,
                inputs=thread_fn(),
                metadata=expected,
                expected_output=None,
            )
        )
    return Dataset(
        name="facilitator-poc",
        cases=cases,
    )


async def run_eval() -> None:
    """Run the evaluation and print the report."""
    dataset = build_dataset()
    report = await dataset.evaluate(facilitate)
    report.print()

    print("\n--- Detailed results ---\n")
    for case_result in report.cases:
        name = case_result.name
        expected = EXPECTATIONS[name]
        output = case_result.output

        print(f"[{name}]")
        print(
            f"  State: {output.classification.state} "
            f"(expected: {expected.expected_state})"
        )
        match = output.classification.state == expected.expected_state
        print(f"  State match: {'yes' if match else 'NO'}")
        print(
            f"  Should intervene: "
            f"{output.classification.should_intervene} "
            f"(expected: {expected.should_intervene})"
        )
        if output.action:
            cat = output.action.category
            ok_cats = expected.acceptable_categories or []
            cat_ok = cat in ok_cats
            print(f"  Action: {cat} ({'ok' if cat_ok else 'UNEXPECTED'})")
            print(f"  Action detail: {output.action.action}")
        if output.response:
            preview = output.response[:120]
            print(f"  Response: {preview}...")
        print(f"  Reasoning: {output.classification.reasoning}")
        print()


if __name__ == "__main__":
    import asyncio

    asyncio.run(run_eval())
