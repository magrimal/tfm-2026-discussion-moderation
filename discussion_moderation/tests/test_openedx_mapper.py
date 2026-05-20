"""Unit tests for the Open edX backend comment parser — no LLM, no HTTP."""

from datetime import UTC, datetime

from discussion_moderation.tools.openedx import OpenEdXBackend

NOW = datetime(2026, 4, 7, 12, 0, tzinfo=UTC)

backend = OpenEdXBackend()


def _comment_data(**kwargs) -> dict:
    defaults = {
        "username": "alice",
        "created_at": NOW,
        "body": "I think X is important.",
        "endorsed": False,
        "abuse_flagged": False,
        "votes": {"point": 0},
        "children": [],
    }
    return {**defaults, **kwargs}


def testparse_comment_maps_author_and_body():
    comment = backend.parse_comment(_comment_data())

    assert comment.author == "alice"
    assert comment.body == "I think X is important."


def testparse_comment_maps_optional_fields():
    comment = backend.parse_comment(
        _comment_data(endorsed=True, abuse_flagged=True, votes={"point": 3})
    )

    assert comment.endorsed is True
    assert comment.abuse_flagged is True
    assert comment.vote_count == 3


def testparse_comment_no_replies_when_children_empty():
    comment = backend.parse_comment(_comment_data())

    assert comment.replies == []


def testparse_comment_preserves_one_level_of_nesting():
    reply = _comment_data(username="bob", body="I agree.")
    comment = backend.parse_comment(_comment_data(children=[reply]))

    assert len(comment.replies) == 1
    assert comment.replies[0].author == "bob"


def testparse_comment_preserves_two_levels_of_nesting():
    deep = _comment_data(username="carol", body="Me too.")
    mid = _comment_data(username="bob", body="I agree.", children=[deep])
    top = backend.parse_comment(_comment_data(children=[mid]))

    assert top.replies[0].replies[0].author == "carol"
