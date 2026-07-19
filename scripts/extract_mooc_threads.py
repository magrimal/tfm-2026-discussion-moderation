"""
Extract and reconstruct discussion threads from the Zenodo edX MOOC dataset.

The input file (filtered_forum_data_v2.mongo) is NDJSON with two relevant event types:
- edx.forum.thread.created: event.id, event.title, event.body, record.time, record.username
- edx.forum.comment.created: event.body, event.discussion.id (→ thread id), record.time, record.username

Output: JSON file with all candidate threads (≥3 comments, body >100 chars, English)
in the TFM thread format used by docs/threads/*.json.

Usage:
    python3 scripts/extract_mooc_threads.py \
        --input /path/to/filtered_forum_data_v2.mongo \
        --output scripts/mooc_thread_candidates.json \
        [--min-comments 3] [--min-body-len 100]
"""

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime, UTC


def is_english(text: str, threshold: float = 0.7) -> bool:
    """Rough heuristic: fraction of ASCII letters > threshold implies English."""
    if not text:
        return False
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return False
    ascii_letters = [c for c in letters if ord(c) < 128]
    return len(ascii_letters) / len(letters) >= threshold


def anonymize(username: str, user_map: dict) -> str:
    """Replace real usernames with stable generic ones."""
    if username not in user_map:
        idx = len(user_map) + 1
        user_map[username] = f"student{idx}"
    return user_map[username]


def parse_time(time_str: str) -> str:
    """Normalize timestamp to ISO 8601 UTC."""
    try:
        dt = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
        return dt.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    except Exception:
        return time_str


def extract(
    input_path: str, min_comments: int, min_body_len: int
) -> list[dict]:
    thread_map: dict[str, dict] = {}
    comments_map: dict[str, list[dict]] = defaultdict(list)

    with open(input_path, encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            if line_num % 100_000 == 0:
                print(f"  processed {line_num:,} lines...", file=sys.stderr)
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue

            event_type = record.get("event_type", "")
            raw_event = record.get("event", {})
            if isinstance(raw_event, str):
                try:
                    raw_event = json.loads(raw_event)
                except json.JSONDecodeError:
                    continue
            if not isinstance(raw_event, dict):
                continue

            username = record.get("username", "unknown")
            timestamp = parse_time(record.get("time", ""))

            if event_type == "edx.forum.thread.created":
                thread_id = raw_event.get("id", "")
                if not thread_id:
                    continue
                thread_map[thread_id] = {
                    "id": thread_id,
                    "title": raw_event.get("title", ""),
                    "body": raw_event.get("body", ""),
                    "time": timestamp,
                    "username": username,
                    "course_id": record.get("context", {}).get("course_id", ""),
                    "category": raw_event.get("category_name", ""),
                }

            elif event_type == "edx.forum.comment.created":
                thread_id = raw_event.get("discussion", {}).get("id", "")
                if not thread_id:
                    continue
                body = raw_event.get("body", "")
                if body:
                    comments_map[thread_id].append(
                        {
                            "body": body,
                            "time": timestamp,
                            "username": username,
                        }
                    )

    print(f"Threads found: {len(thread_map):,}", file=sys.stderr)
    print(f"Threads with comments: {len(comments_map):,}", file=sys.stderr)

    results = []
    for thread_id, thread in thread_map.items():
        comments = comments_map.get(thread_id, [])
        if len(comments) < min_comments:
            continue
        if len(thread["body"]) < min_body_len:
            continue
        if not is_english(thread["body"]):
            continue

        comments_sorted = sorted(comments, key=lambda c: c["time"])

        user_map: dict[str, str] = {}
        children = [
            {
                "username": anonymize(thread["username"], user_map),
                "body": thread["body"],
                "created_at": thread["time"],
            }
        ] + [
            {
                "username": anonymize(c["username"], user_map),
                "body": c["body"],
                "created_at": c["time"],
            }
            for c in comments_sorted
        ]

        results.append(
            {
                "id": f"real-{thread_id}",
                "course_id": "course-v1:OpenedX+DemoX+DemoCourse",
                "title": thread["title"],
                "created_at": thread["time"],
                "source_course": thread["course_id"],
                "source_category": thread["category"],
                "children": children,
            }
        )

    results.sort(key=lambda t: -len(t["children"]))
    print(f"Candidates after filtering: {len(results):,}", file=sys.stderr)
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input", required=True, help="Path to filtered_forum_data_v2.mongo"
    )
    parser.add_argument("--output", required=True, help="Output JSON file path")
    parser.add_argument("--min-comments", type=int, default=3)
    parser.add_argument("--min-body-len", type=int, default=100)
    args = parser.parse_args()

    print("Parsing dataset...", file=sys.stderr)
    threads = extract(args.input, args.min_comments, args.min_body_len)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(threads, f, indent=2, ensure_ascii=False)

    print(
        f"Written {len(threads)} candidates to {args.output}", file=sys.stderr
    )


if __name__ == "__main__":
    main()
