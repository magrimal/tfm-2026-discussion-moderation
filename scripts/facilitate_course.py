"""Trigger the facilitation pipeline for a set of forum threads.

Calls POST /facilitate/thread/{thread_id} for each thread ID and
prints a summary line per thread. Use this to simulate the webhook
calls that Open edX would make in a production integration.

Run against a local Tutor dev install:

    python scripts/facilitate_course.py \
        --api-url http://localhost:8080 \
        --thread-ids 6 7 8 9 10 11 12

Or read thread IDs from the JSON snapshot produced by the seed script:

    python scripts/facilitate_course.py \
        --api-url http://localhost:8080 \
        --from-json scripts/threads_api_output.json
"""

import argparse
import json
import sys

import httpx


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Trigger facilitation for a set of forum threads."
    )
    parser.add_argument(
        "--api-url",
        default="http://localhost:8080",
        help="Base URL of the facilitation service (default: http://localhost:8080)",
    )
    parser.add_argument(
        "--thread-ids",
        nargs="+",
        metavar="ID",
        help="Thread IDs to facilitate (e.g. 6 7 8 9 10 11 12)",
    )
    parser.add_argument(
        "--from-json",
        metavar="FILE",
        help=(
            "JSON file with a 'results' list of thread objects. "
            "Thread IDs are read from the 'id' field of each entry."
        ),
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=60.0,
        help="Request timeout in seconds (default: 60)",
    )
    return parser.parse_args()


def thread_ids_from_json(path: str) -> list[str]:
    """Extract thread IDs from a threads_api_output.json file."""
    with open(path) as f:
        data = json.load(f)
    results = data.get("results", [])
    if not results:
        print(f"No results found in {path}", file=sys.stderr)
        sys.exit(1)
    return [str(t["id"]) for t in results]


def main() -> None:
    """Run facilitation for each thread and print a summary table."""
    args = parse_args()

    if args.from_json:
        thread_ids = thread_ids_from_json(args.from_json)
    elif args.thread_ids:
        thread_ids = args.thread_ids
    else:
        print("Error: provide --thread-ids or --from-json.", file=sys.stderr)
        sys.exit(1)

    base_url = args.api_url.rstrip("/")
    print(
        f"\nFacilitating {len(thread_ids)} threads via {base_url}\n"
        f"{'ID':<6} {'State':<18} {'Intervene':<10} "
        f"{'Role':<20} {'Posted'}"
    )
    print("-" * 70)

    errors: list[str] = []
    with httpx.Client(timeout=args.timeout) as client:
        for thread_id in thread_ids:
            url = f"{base_url}/facilitate/thread/{thread_id}"
            try:
                resp = client.post(url)
                resp.raise_for_status()
                data = resp.json()

                result = data.get("result", {})
                classification = result.get("classification", {})
                intervention = result.get("intervention") or {}
                role_selection = result.get("role_selection") or {}

                state = classification.get("state", "—")
                should_intervene = intervention.get("should_intervene", False)
                role = role_selection.get("role", "—")
                comment_posted = data.get("comment_posted", False)
                comment_id = data.get("comment_id") or ""

                posted_str = f"yes ({comment_id})" if comment_posted else "no"
                print(
                    f"{thread_id:<6} {state:<18} {str(should_intervene):<10} "
                    f"{str(role):<20} {posted_str}"
                )
            except httpx.HTTPStatusError as exc:
                msg = f"Thread {thread_id}: HTTP {exc.response.status_code}"
                print(f"{thread_id:<6} ERROR — {msg}")
                errors.append(msg)
            except Exception as exc:
                msg = f"Thread {thread_id}: {exc}"
                print(f"{thread_id:<6} ERROR — {msg}")
                errors.append(msg)

    print()
    if errors:
        print(f"{len(errors)} error(s) encountered:")
        for e in errors:
            print(f"  {e}")
        sys.exit(1)
    else:
        print("Done.")


if __name__ == "__main__":
    main()
