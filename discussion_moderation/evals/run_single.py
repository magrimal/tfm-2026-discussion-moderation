"""Run the facilitator agent on a single sample thread.

Usage:
    uv run python -m discussion_moderation.evals.run_single <state>

Where <state> is one of: new, active, stalled, conflictive,
convergent, off_topic.
"""

import asyncio
import json
import sys

from discussion_moderation.agents.facilitator import facilitate
from discussion_moderation.evals.sample_threads import (
    ALL_THREADS,
)


async def main(state: str) -> None:
    """Run facilitation on a single thread and print results."""
    if state not in ALL_THREADS:
        print(f"Unknown state: {state}")
        print(f"Available: {', '.join(ALL_THREADS)}")
        sys.exit(1)

    thread = ALL_THREADS[state]()
    print(f"Running facilitator on '{state}' thread...")
    print(f"Topic: {thread.topic}")
    print(f"Posts: {len(thread.posts)}")
    print()

    result = await facilitate(thread)

    print(
        json.dumps(
            result.model_dump(mode="json"),
            indent=2,
        )
    )


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(
            "Usage: uv run python -m "
            "discussion_moderation.evals.run_single <state>"
        )
        print(f"States: {', '.join(ALL_THREADS)}")
        sys.exit(1)

    asyncio.run(main(sys.argv[1]))
