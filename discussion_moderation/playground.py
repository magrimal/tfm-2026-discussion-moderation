"""Playground CLI for ad-hoc pipeline testing.

Usage:
    uv run facilitate thread.json
    uv run facilitate thread.json --pretty

The input file must be a JSON object matching the DiscussionThread
schema. See docs/playground-example.json for a minimal example.

Runs the facilitation pipeline and prints the result to stdout.
Useful for testing the system with custom threads without writing
code or running evals.
"""

import argparse
import asyncio
import json
import sys

from discussion_moderation.api.facilitation import facilitate
from discussion_moderation.models import DiscussionThread


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the facilitation pipeline on a thread JSON file.",
    )
    parser.add_argument(
        "thread_file",
        help="Path to a JSON file containing a DiscussionThread.",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print the full pipeline result as JSON.",
    )
    return parser.parse_args()


def _load_thread(path: str) -> DiscussionThread:
    try:
        with open(path) as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: invalid JSON in {path}: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        return DiscussionThread.model_validate(data)
    except Exception as e:
        print(
            f"Error: file does not match DiscussionThread schema: {e}",
            file=sys.stderr,
        )
        sys.exit(1)


def _print_result(result, pretty: bool) -> None:
    if pretty:
        print(result.model_dump_json(indent=2))
        return

    print(f"State:       {result.classification.state}")
    print(f"Trajectory:  {result.classification.trajectory}")
    print(f"Inquiry:     {result.classification.inquiry_phase}")

    if result.intervention is None:
        print("Intervention: not evaluated")
    elif not result.intervention.should_intervene:
        print("Intervention: NO - thread does not need intervention")
    else:
        print("Intervention: YES")

    if result.role_selection:
        print(f"Role:        {result.role_selection.role}")

    if result.response:
        print(f"Technique:   {result.response.technique_used}")
        print(f"Post:        {result.response.post_to_thread}")
        print(f"Confidence:  {result.response.confidence:.2f}")
        print()
        print("--- Response ---")
        print(result.response.response_text)
    else:
        print("No facilitation response generated.")


async def _run(path: str, pretty: bool) -> None:
    thread = _load_thread(path)
    print(f"Thread: {thread.title!r} [{thread.id}]", file=sys.stderr)
    result = await facilitate(thread)
    _print_result(result, pretty)


def main() -> None:
    """Entry point for uv run facilitate."""
    args = _parse_args()
    asyncio.run(_run(args.thread_file, args.pretty))


if __name__ == "__main__":
    main()
