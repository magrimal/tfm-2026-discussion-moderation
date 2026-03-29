"""Tests for AgentMixin base class."""

import pytest
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.test import TestModel

from discussion_moderation.agents.base import AgentMixin


class ConcreteAgent(AgentMixin):
    def __init__(self) -> None:
        self.agent = Agent(TestModel())
        self._register_system_prompt()

    def _build_system_prompt(self, ctx: RunContext) -> str:
        return "test prompt"


class IncompleteAgent(AgentMixin):
    def __init__(self) -> None:
        self.agent = Agent(TestModel())
        self._register_system_prompt()


def test_concrete_subclass_can_be_instantiated():
    """A subclass that implements _build_system_prompt can be instantiated."""
    agent = ConcreteAgent()
    assert isinstance(agent, AgentMixin)


def test_abstract_subclass_cannot_be_instantiated():
    """A subclass that omits _build_system_prompt raises TypeError."""
    with pytest.raises(TypeError):
        IncompleteAgent()
