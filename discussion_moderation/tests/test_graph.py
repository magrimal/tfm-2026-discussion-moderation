"""Tests for graph node transitions and evaluator toggles."""

from discussion_moderation.common.constants import (
    ActionCategory,
    FacilitationRole,
)
from discussion_moderation.common.models import (
    FacilitationResponse,
)
from discussion_moderation.graph.nodes import (
    _run_response_rule_checks,
)


class TestResponseRuleChecks:
    """Validate rule-based response evaluation checks."""

    def test_valid_response_passes(self):
        """Check a valid response.

        Expected result: No issues returned.
        """
        response = FacilitationResponse(
            response_text="What do you think about X?",
            technique_used="socratic_clarification",
            action_category=ActionCategory.INTELLECTUAL,
        )

        issues = _run_response_rule_checks(
            response, FacilitationRole.INTELLECTUAL
        )

        assert issues == []

    def test_empty_response_fails(self):
        """Check an empty response.

        Expected result: Issue about empty response text.
        """
        response = FacilitationResponse(
            response_text="",
            technique_used="encourage_participation",
            action_category=ActionCategory.SOCIAL,
        )

        issues = _run_response_rule_checks(response, FacilitationRole.SOCIAL)

        assert any("empty" in i.lower() for i in issues)

    def test_missing_technique_fails(self):
        """Check a response with no technique specified.

        Expected result: Issue about missing technique.
        """
        response = FacilitationResponse(
            response_text="Good discussion!",
            technique_used="",
            action_category=ActionCategory.SOCIAL,
        )

        issues = _run_response_rule_checks(response, FacilitationRole.SOCIAL)

        assert any("technique" in i.lower() for i in issues)

    def test_evaluative_language_fails(self):
        """Check a response containing grading language.

        Expected result: Issue about evaluative language.
        """
        response = FacilitationResponse(
            response_text=("This is the correct answer. Good grade."),
            technique_used="validate_effort",
            action_category=ActionCategory.AFFECTIVE,
        )

        issues = _run_response_rule_checks(response, FacilitationRole.AFFECTIVE)

        assert any("evaluative" in i.lower() for i in issues)
