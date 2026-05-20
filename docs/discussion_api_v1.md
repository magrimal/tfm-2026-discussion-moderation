# Open edX Discussion API v1: thread and comment schema

LMS-facing API at `/api/discussion/v1/`. This is the API the facilitation
system consumes. It differs from the internal forum service (`/forum/api/v2/`)
documented in `forum_api.md`.

Authentication: `Authorization: JWT <token>` or session cookie.

---

## Thread list

`GET /api/discussion/v1/threads/?course_id=<course_id>`

```json
{
  "results": [ ...thread objects ],
  "pagination": {
    "next": null,
    "previous": null,
    "count": 7,
    "num_pages": 1
  },
  "text_search_rewrite": null
}
```

## Thread object

A thread contains its opening argument directly in `raw_body`. Comments are
fetched separately via `comment_list_url`.

| Field | Type | Notes |
|-------|------|-------|
| `id` | string | Thread identifier |
| `title` | string | Thread title |
| `type` | string | `"discussion"` or `"question"` |
| `raw_body` | string | Opening argument, Markdown |
| `rendered_body` | string | Opening argument, HTML |
| `author` | string | Username |
| `author_label` | string / null | Role label (e.g. `"Instructor"`); null for students |
| `created_at` | ISO8601 | Creation timestamp |
| `updated_at` | ISO8601 | Last update timestamp |
| `course_id` | string | Course identifier |
| `topic_id` | string | Discussion category |
| `group_id` | integer / null | Cohort; null if not cohorted |
| `closed` | boolean | Whether the thread accepts new posts |
| `has_endorsed` | boolean | Whether a question thread has an accepted answer |
| `pinned` | boolean | |
| `vote_count` | integer | Upvotes |
| `abuse_flagged` | boolean | |
| `comment_count` | integer | Total comments |
| `comment_list_url` | string / null | URL to fetch comments (discussion threads only) |
| `endorsed_comment_list_url` | string / null | URL to fetch endorsed comments (question threads only) |
| `non_endorsed_comment_list_url` | string / null | URL to fetch non-endorsed comments (question threads only) |

Fields not relevant to the facilitation pipeline (editable_fields, voted,
unread_comment_count, preview_body, users, can_delete, anonymous,
anonymous_to_peers, following, read, last_edit, edit_by_label,
close_reason, closed_by, closed_by_label, abuse_flagged_count) are present
in the API response and can be ignored.

## Comment object

Comments are fetched from the URL in `comment_list_url`. Each comment may
contain nested replies in `children`.

| Field | Type | Notes |
|-------|------|-------|
| `id` | string | Comment identifier |
| `author` | string | Username |
| `author_label` | string / null | Role label; null for students |
| `created_at` | ISO8601 | |
| `raw_body` | string | Content, Markdown |
| `rendered_body` | string | Content, HTML |
| `endorsed` | boolean | Whether this is a marked accepted answer |
| `abuse_flagged` | boolean | |
| `vote_count` | integer | Upvotes |
| `children` | list | Nested replies, same schema (recursive) |

## Structure summary

```
Thread
  title               string
  raw_body            string   (opening argument)
  type                "discussion" | "question"
  comments            fetched from comment_list_url
    Comment
      raw_body        string
      author          string
      children        list[Comment]   (nested replies, unbounded depth)
```

The thread body (opening argument) and the comments are separate in the API.
There is no need to treat the opening post as a special first comment.

---

## Facilitation service endpoints that use this data

The local service layer exposes these endpoints for dashboard and integration
flows:

- `GET /lms/threads?course_id=<course_id>`: list active LMS threads via
  discussion v1 (`/api/discussion/v1/threads/`).
- `POST /runs/trigger`: experiment run trigger (fixtures and LMS snapshot
  threads).
- `POST /runs/live/trigger`: one live run against a real LMS thread.
- `GET /threads/{thread_id}/history`: intervention history for one thread.

Run-progress feedback during execution:

- `GET /runs`: each run summary includes `status`, `completed_runs`,
  `total_runs`, and `progress_message` for live stage visibility.
- `GET /runs/{run_id}`: detail view includes the same progress fields while
  the run is still `running`.
