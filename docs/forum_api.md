# openedx/forum API reference

Internal service API consumed by edx-platform. Not the end-user LMS discussion API
(`/api/discussion/v1/`).

Both `/api/v1/` and `/api/v2/` prefixes expose the same routes.

## Authentication

Every endpoint accepts two authentication methods (tried in order):

| Method | How to use |
|--------|-----------|
| **JWT** | `Authorization: JWT <token>` — token issued by the LMS OAuth2/JWT provider |
| **Session** | `sessionid` cookie — standard Django session after browser login |

Permission class on all endpoints is `AllowAny`: the framework will attempt to
identify the caller but will not reject unauthenticated requests at the view
level. Authorization logic lives inside each view.

---

## Threads

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v2/course/threads` | Create a thread |
| `GET` | `/api/v2/threads/<thread_id>` | Get a thread |
| `PUT` | `/api/v2/threads/<thread_id>` | Update a thread |
| `DELETE` | `/api/v2/threads/<thread_id>` | Delete a thread |
| `GET` | `/api/v2/threads` | List threads for a user |
| `GET` | `/api/v2/search/threads` | Search threads |

## Comments

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v2/threads/<thread_id>/comments` | Create a top-level comment on a thread |
| `GET` | `/api/v2/comments/<comment_id>` | Get a comment |
| `POST` | `/api/v2/comments/<comment_id>` | Create a reply on a comment |
| `PUT` | `/api/v2/comments/<comment_id>` | Update a comment |
| `DELETE` | `/api/v2/comments/<comment_id>` | Delete a comment |

## Votes

| Method | Path | Description |
|--------|------|-------------|
| `PUT` | `/api/v2/threads/<thread_id>/votes` | Upvote or downvote a thread |
| `DELETE` | `/api/v2/threads/<thread_id>/votes` | Remove vote from a thread |
| `PUT` | `/api/v2/comments/<comment_id>/votes` | Upvote or downvote a comment |
| `DELETE` | `/api/v2/comments/<comment_id>/votes` | Remove vote from a comment |

## Flags (abuse reporting)

| Method | Path | Description |
|--------|------|-------------|
| `PUT` | `/api/v2/threads/<thread_id>/abuse_<action>` | Flag or unflag a thread (`action`: `flag` / `unflag`) |
| `PUT` | `/api/v2/comments/<comment_id>/abuse_<action>` | Flag or unflag a comment |

## Pins

| Method | Path | Description |
|--------|------|-------------|
| `PUT` | `/api/v2/threads/<thread_id>/pin` | Pin a thread |
| `PUT` | `/api/v2/threads/<thread_id>/unpin` | Unpin a thread |

## Subscriptions

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v2/users/<user_id>/subscriptions` | Subscribe a user to a thread |
| `DELETE` | `/api/v2/users/<user_id>/subscriptions` | Unsubscribe a user |
| `GET` | `/api/v2/users/<user_id>/subscribed_threads` | List a user's subscriptions |
| `GET` | `/api/v2/threads/<thread_id>/subscriptions` | List subscribers of a thread |

## Users

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v2/users` | Create a forum user |
| `GET` | `/api/v2/users/<user_id>` | Get a user |
| `PUT` | `/api/v2/users/<user_id>` | Update a user |
| `POST` | `/api/v2/users/<user_id>/replace_username` | Rename a user |
| `POST` | `/api/v2/users/<user_id>/read` | Mark content as read |
| `GET` | `/api/v2/users/<user_id>/active_threads` | List a user's active threads |
| `GET` | `/api/v2/users/<course_id>/stats` | Get user stats for a course |
| `POST` | `/api/v2/users/<course_id>/update_stats` | Update user stats for a course |
| `POST` | `/api/v2/users/<user_id>/retire` | Retire (anonymise) a user |

## Commentables

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v2/commentables/<course_id>/counts` | Get discussion topic counts for a course |
