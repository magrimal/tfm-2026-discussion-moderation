"""Unit tests for the technique knowledge base — no LLM required."""

import pytest

from discussion_moderation.constants import DiscussionState
from discussion_moderation.tools.knowledge_base import (
    TECHNIQUES,
    Technique,
    get_techniques,
)

TOTAL_TECHNIQUES = 30


# --- Technique count ---


def test_get_techniques_returns_all_techniques_without_filter():
    techniques = get_techniques()

    assert len(techniques) == TOTAL_TECHNIQUES


def test_get_techniques_with_state_filter_returns_all_techniques():
    # State filter is not used to restrict results - all techniques
    # are available to every agent. Passing a state must not reduce
    # the count below what get_techniques() returns without one.
    for state in DiscussionState:
        techniques = get_techniques(state=state)
        assert len(techniques) == TOTAL_TECHNIQUES, (
            f"Expected {TOTAL_TECHNIQUES} techniques for state {state}, "
            f"got {len(techniques)}"
        )


def test_techniques_list_length():
    assert len(TECHNIQUES) == TOTAL_TECHNIQUES


# --- Required techniques ---


def _technique_names() -> set[str]:
    return {t.name for t in TECHNIQUES}


def test_instructor_escalation_technique_exists():
    assert "instructor_escalation" in _technique_names()


def test_instructor_escalation_mentions_post_to_thread():
    technique = next(t for t in TECHNIQUES if t.name == "instructor_escalation")

    assert "post_to_thread" in technique.description.lower()


@pytest.mark.parametrize(
    "name",
    [
        "launch_discussion",
        "summarize_progress",
        "socratic_clarification",
        "revoice",
        "encourage_participation",
        "validate_effort",
        "flag_for_review",
        "de_escalate",
        "normalize_difficulty",
        "encourage_reengagement",
        "process_feedback",
        "boundary_statement",
        "redirect_to_norms",
    ],
)
def test_expected_technique_exists(name):
    assert name in _technique_names(), f"Technique '{name}' not found"


# --- Technique structure ---


def test_all_techniques_have_non_empty_name():
    for t in TECHNIQUES:
        assert t.name.strip(), "Found technique with empty name"


def test_all_techniques_have_non_empty_description():
    for t in TECHNIQUES:
        assert t.description.strip(), (
            f"Technique '{t.name}' has empty description"
        )


def test_all_techniques_have_at_least_one_example():
    for t in TECHNIQUES:
        assert t.examples, f"Technique '{t.name}' has no examples"


def test_all_techniques_have_source():
    # Source is required for traceability (ADR 0009).
    for t in TECHNIQUES:
        assert t.source.strip(), (
            f"Technique '{t.name}' is missing a source reference"
        )


def test_no_duplicate_technique_names():
    names = [t.name for t in TECHNIQUES]
    assert len(names) == len(set(names)), "Duplicate technique names found"


def test_get_techniques_returns_technique_instances():
    techniques = get_techniques()

    for t in techniques:
        assert isinstance(t, Technique)
