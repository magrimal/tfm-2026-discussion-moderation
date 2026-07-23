"""Tests for discussion_moderation.json_repair."""

import json

import pytest

from discussion_moderation.json_repair import repair_and_extract_json


def test_valid_json_passes_through_unchanged():
    text = '{"a": 1, "b": "hello"}'
    assert json.loads(repair_and_extract_json(text)) == {"a": 1, "b": "hello"}


def test_escapes_raw_newline_inside_string():
    text = '{"note": "line1\nline2"}'
    repaired = repair_and_extract_json(text)
    assert json.loads(repaired) == {"note": "line1\nline2"}


def test_escapes_raw_tab_and_carriage_return_inside_string():
    text = '{"note": "a\tb\rc"}'
    repaired = repair_and_extract_json(text)
    assert json.loads(repaired) == {"note": "a\tb\rc"}


def test_strips_markdown_code_fence_preamble():
    text = 'Here is the result:\n```json\n{"a": 1}\n```'
    repaired = repair_and_extract_json(text)
    assert json.loads(repaired) == {"a": 1}


def test_strips_trailing_extra_brace():
    """Regression test: live model output ended with an extra stray
    "}" after the object's real closing brace.
    """
    text = '{"a": 1}\n}'
    repaired = repair_and_extract_json(text)
    assert json.loads(repaired) == {"a": 1}


def test_real_world_multiline_reasoning_field():
    """Regression test: the exact class of output pasted from a live
    idril run - valid content, wrong escaping in a multi-line
    "reasoning" field, plus a stray trailing brace.
    """
    text = (
        '{"response_text": "Some question?", '
        '"technique_used": "focused_reframing_prompt", '
        '"confidence": 0.95, '
        '"reasoning": "- point one\n'
        "   \n"
        '- point two", '
        '"post_to_thread": true}\n}'
    )
    repaired = repair_and_extract_json(text)
    parsed = json.loads(repaired)
    assert parsed["technique_used"] == "focused_reframing_prompt"
    assert "point one" in parsed["reasoning"]
    assert "point two" in parsed["reasoning"]


def test_no_json_object_raises():
    with pytest.raises(ValueError, match="No JSON object"):
        repair_and_extract_json("just some prose, no braces here")


def test_unterminated_object_raises():
    with pytest.raises(ValueError, match="Unterminated"):
        repair_and_extract_json('{"a": 1')
