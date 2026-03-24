"""Tests for the orchestrator agent prompt construction."""

from discussion_moderation.common.prompts import (
    format_role_descriptions,
)


class TestFormatRoleDescriptions:
    """Validate role description formatting for orchestrator."""

    def test_includes_all_roles(self):
        """Format role descriptions.

        Expected result: Output includes all five facilitation
        roles with descriptions.
        """
        descriptions = format_role_descriptions()

        assert "organizational" in descriptions
        assert "intellectual" in descriptions
        assert "social" in descriptions
        assert "affective" in descriptions
        assert "moderator" in descriptions

    def test_is_markdown_formatted(self):
        """Check role descriptions use markdown bullets.

        Expected result: Each role starts with "- **".
        """
        descriptions = format_role_descriptions()
        lines = [line for line in descriptions.split("\n") if line.strip()]

        for line in lines:
            assert line.startswith("- **")
