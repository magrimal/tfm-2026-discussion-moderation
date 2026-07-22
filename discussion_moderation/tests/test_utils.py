"""Tests for shared prompt-building utilities in utils.py."""

from discussion_moderation.utils import MAX_REASONING_CHARS, cap_reasoning


def test_cap_reasoning_leaves_short_text_untouched():
    text = "Short reasoning."
    assert cap_reasoning(text) == text


def test_cap_reasoning_truncates_long_text():
    text = "x" * (MAX_REASONING_CHARS + 200)
    capped = cap_reasoning(text)

    assert len(capped) < len(text)
    assert capped.endswith("[truncated]")
