"""Tests for shared prompt-building utilities in utils.py."""

from discussion_moderation.utils import MAX_REASONING_CHARS, cap_reasoning


def test_cap_reasoning_leaves_short_text_untouched():
    text = "Short reasoning."
    assert cap_reasoning(text) == text


def test_cap_reasoning_truncates_long_text():
    text = "x" * (MAX_REASONING_CHARS + 200)
    capped = cap_reasoning(text)

    assert len(capped) < len(text)
    assert "shortened" in capped


def test_cap_reasoning_marker_does_not_say_truncated():
    """Regression test: a live idril trace showed the model reading a
    bare "[truncated]" marker as "the discussion thread is
    incomplete" and refusing to answer, even though only this
    reasoning summary was shortened - the actual thread is given in
    full elsewhere in the prompt, untouched. The marker text must not
    say "truncated" alone, since that's exactly what caused the
    misreading.
    """
    text = "x" * (MAX_REASONING_CHARS + 200)
    capped = cap_reasoning(text)

    assert "truncated" not in capped.lower()
