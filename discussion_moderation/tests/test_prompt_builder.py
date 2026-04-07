"""Unit tests for AgentMixin.build_prompt() — no LLM required."""

import pytest

from discussion_moderation.agents.base import AgentMixin
from discussion_moderation.agents.classification import ClassificationAgent
from discussion_moderation.agents.intervention import InterventionAgent
from discussion_moderation.agents.orchestrator import OrchestratorAgent
from discussion_moderation.agents.roles import (
    IntellectualAgent,
    ModeratorAgent,
    OrganizationalAgent,
    ROLE_AGENT_CLASSES,
    SHARED_ROLE_CONSTRAINTS,
)


# --- build_prompt section assembly ---


class _AllSections(AgentMixin):
    """Concrete subclass with all four sections populated."""

    PERSONALITY = "I am a persona."
    CONSTRAINTS = "I must not do X."
    CONTEXT_TEMPLATE = "Context: {value}"
    INSTRUCTIONS = "Do the task."

    def build_system_prompt(self, ctx):  # type: ignore[override]
        return self.build_prompt().format(value="test")


class _NoContext(AgentMixin):
    PERSONALITY = "Persona."
    CONSTRAINTS = "Constraints."
    INSTRUCTIONS = "Task."

    def build_system_prompt(self, ctx):  # type: ignore[override]
        return self.build_prompt()


class _OnlyPersonality(AgentMixin):
    PERSONALITY = "Just me."

    def build_system_prompt(self, ctx):  # type: ignore[override]
        return self.build_prompt()


def test_build_prompt_includes_all_four_headers():
    prompt = _AllSections.build_prompt()

    assert "# Persona" in prompt
    assert "# Constraints" in prompt
    assert "# Context" in prompt
    assert "# Task" in prompt


def test_build_prompt_section_order():
    prompt = _AllSections.build_prompt()

    assert prompt.index("# Persona") < prompt.index("# Constraints")
    assert prompt.index("# Constraints") < prompt.index("# Context")
    assert prompt.index("# Context") < prompt.index("# Task")


def test_build_prompt_omits_empty_sections():
    prompt = _NoContext.build_prompt()

    assert "# Context" not in prompt
    assert "# Persona" in prompt
    assert "# Constraints" in prompt
    assert "# Task" in prompt


def test_build_prompt_single_section_no_separator():
    prompt = _OnlyPersonality.build_prompt()

    assert prompt == "# Persona\nJust me."


def test_build_prompt_sections_separated_by_double_newline():
    prompt = _AllSections.build_prompt()

    # Each section boundary should be separated by exactly \n\n
    assert "\n\n# Constraints" in prompt
    assert "\n\n# Context" in prompt
    assert "\n\n# Task" in prompt


def test_build_prompt_content_appears_under_correct_header():
    prompt = _AllSections.build_prompt()

    persona_idx = prompt.index("# Persona")
    constraints_idx = prompt.index("# Constraints")

    between = prompt[persona_idx:constraints_idx]
    assert "I am a persona." in between


# --- Agent-specific prompt completeness ---


def test_classification_agent_has_all_four_sections():
    prompt = ClassificationAgent.build_prompt()

    assert "# Persona" in prompt
    assert "# Constraints" in prompt
    assert "# Context" in prompt
    assert "# Task" in prompt


def test_intervention_agent_has_all_four_sections():
    prompt = InterventionAgent.build_prompt()

    assert "# Persona" in prompt
    assert "# Constraints" in prompt
    assert "# Context" in prompt
    assert "# Task" in prompt


def test_orchestrator_agent_has_all_four_sections():
    prompt = OrchestratorAgent.build_prompt()

    assert "# Persona" in prompt
    assert "# Constraints" in prompt
    assert "# Context" in prompt
    assert "# Task" in prompt


@pytest.mark.parametrize("cls", ROLE_AGENT_CLASSES)
def test_role_agent_has_persona_and_constraints(cls):
    assert cls.PERSONALITY, f"{cls.__name__} has empty PERSONALITY"
    assert cls.CONSTRAINTS, f"{cls.__name__} has empty CONSTRAINTS"


@pytest.mark.parametrize("cls", ROLE_AGENT_CLASSES)
def test_role_agent_personality_in_prompt(cls):
    prompt = cls.build_prompt()

    assert "# Persona" in prompt
    assert cls.PERSONALITY in prompt


@pytest.mark.parametrize("cls", ROLE_AGENT_CLASSES)
def test_role_agent_shared_constraints_in_prompt(cls):
    # All role agents must carry the shared constraints.
    prompt = cls.build_prompt()

    # Check a distinctive phrase from SHARED_ROLE_CONSTRAINTS.
    assert "Select exactly ONE technique" in prompt


def test_shared_role_constraints_non_empty():
    assert SHARED_ROLE_CONSTRAINTS.strip()


def test_shared_role_constraints_includes_anti_patterns():
    # build_anti_pattern_text() is called at import time.
    assert "Anti-patterns to avoid" in SHARED_ROLE_CONSTRAINTS


def test_moderator_agent_adds_last_resort_constraint():
    prompt = ModeratorAgent.build_prompt()

    assert "last resort" in prompt.lower()


def test_organizational_agent_adds_synthesis_timing_constraint():
    prompt = OrganizationalAgent.build_prompt()

    assert "synthesis" in prompt.lower() or "closure" in prompt.lower()


def test_intellectual_agent_adds_emt_ladder_constraint():
    prompt = IntellectualAgent.build_prompt()

    assert "pump" in prompt.lower() or "L1" in prompt


def test_role_instructions_mention_post_to_thread():
    # All role agents share the same INSTRUCTIONS; check one.
    prompt = OrganizationalAgent.build_prompt()

    assert "post_to_thread" in prompt
