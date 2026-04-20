"""Unit tests for the Open edX thread mapper — no LLM, no HTTP."""

from datetime import UTC, datetime

from discussion_moderation.tools.openedx import (
    OpenEdXComment,
    OpenEdXThread,
    map_thread,
)

NOW = datetime(2026, 4, 7, 12, 0, tzinfo=UTC)


def _api_thread(**kwargs) -> OpenEdXThread:
    defaults = {
        "id": "42",
        "author": "instructor",
        "author_label": "Instructor",
        "created_at": NOW,
        "raw_body": "What do you think about X?",
        "title": "Discussion on X",
        "course_id": "course-v1:UCM+TFM+2026",
    }
    return OpenEdXThread(**{**defaults, **kwargs})


def _api_comment(**kwargs) -> OpenEdXComment:
    defaults = {
        "id": "1",
        "author": "alice",
        "created_at": NOW,
        "raw_body": "I think X is important.",
    }
    return OpenEdXComment(**{**defaults, **kwargs})


# --- Opening post ---


def test_map_thread_opening_post_is_first_child():
    thread = map_thread(_api_thread(), [])

    assert len(thread.children) == 1
    assert thread.children[0].username == "instructor"
    assert thread.children[0].body == "What do you think about X?"


def test_map_thread_opening_post_carries_author_label():
    thread = map_thread(_api_thread(author_label="Instructor"), [])

    assert thread.children[0].author_label == "Instructor"


def test_map_thread_opening_post_has_no_replies():
    thread = map_thread(_api_thread(), [])

    assert thread.children[0].replies == []


# --- Comments ---


def test_map_thread_comments_follow_opening_post():
    comment = _api_comment()
    thread = map_thread(_api_thread(), [comment])

    assert len(thread.children) == 2
    assert thread.children[1].username == "alice"


def test_map_thread_comment_fields_are_mapped():
    comment = _api_comment(
        author_label="Community TA",
        endorsed=True,
        abuse_flagged=True,
        vote_count=3,
    )
    thread = map_thread(_api_thread(), [comment])
    mapped = thread.children[1]

    assert mapped.author_label == "Community TA"
    assert mapped.endorsed is True
    assert mapped.abuse_flagged is True
    assert mapped.vote_count == 3


# --- Nested replies ---


def test_map_thread_preserves_one_level_of_nesting():
    reply = _api_comment(id="2", author="bob", raw_body="I agree.")
    comment = _api_comment(children=[reply])
    thread = map_thread(_api_thread(), [comment])

    assert len(thread.children[1].replies) == 1
    assert thread.children[1].replies[0].username == "bob"


def test_map_thread_preserves_two_levels_of_nesting():
    deep = _api_comment(id="3", author="carol", raw_body="Me too.")
    mid = _api_comment(
        id="2", author="bob", raw_body="I agree.", children=[deep]
    )
    top = _api_comment(children=[mid])
    thread = map_thread(_api_thread(), [top])

    assert thread.children[1].replies[0].replies[0].username == "carol"


# --- Thread-level fields ---


def test_map_thread_metadata_is_correct():
    thread = map_thread(_api_thread(), [])

    assert thread.id == "42"
    assert thread.course_id == "course-v1:UCM+TFM+2026"
    assert thread.title == "Discussion on X"
    assert thread.thread_type == "discussion"


def test_map_thread_closed_field_is_forwarded():
    thread = map_thread(_api_thread(closed=True), [])

    assert thread.closed is True


def test_map_thread_has_endorsed_is_forwarded():
    thread = map_thread(_api_thread(has_endorsed=True), [])

    assert thread.has_endorsed is True


def test_map_thread_last_activity_at_comes_from_updated_at():
    updated = datetime(2026, 4, 7, 14, 0, tzinfo=UTC)
    thread = map_thread(_api_thread(updated_at=updated), [])

    assert thread.last_activity_at == updated


def test_map_thread_learning_objectives_defaults_to_empty():
    thread = map_thread(_api_thread(), [])

    assert thread.learning_objectives == []


def test_map_thread_learning_objectives_injected_when_provided():
    los = ["Understand X", "Apply Y"]
    thread = map_thread(_api_thread(), [], learning_objectives=los)

    assert thread.learning_objectives == los


# --- Extra fields in API response are ignored ---


def test_openedx_thread_ignores_unknown_fields():
    data = {
        "id": "1",
        "author": "admin",
        "created_at": NOW,
        "raw_body": "Hello",
        "title": "Thread",
        "course_id": "course-v1:UCM+TFM+2026",
        "editable_fields": ["abuse_flagged", "title"],
        "rendered_body": "<p>Hello</p>",
        "preview_body": "Hello",
        "vote_count": 0,
        "pinned": False,
        "topic_id": "course",
    }
    thread = OpenEdXThread(**data)

    assert thread.id == "1"


def test_openedx_comment_ignores_unknown_fields():
    data = {
        "id": "1",
        "author": "alice",
        "created_at": NOW,
        "raw_body": "Hello",
        "voted": False,
        "editable_fields": [],
        "rendered_body": "<p>Hello</p>",
    }
    comment = OpenEdXComment(**data)

    assert comment.author == "alice"
