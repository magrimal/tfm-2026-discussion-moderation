"""Classifier agent: Phase 1 of the intervention model.

Classifies the discussion state and decides whether intervention
is warranted (ADR 0003, Fase 1).
"""

from pydantic_ai import Agent, RunContext

from discussion_moderation.agents.base import AgentMixin
from discussion_moderation.common.models import (
    ClassificationResult,
    ClassifierDeps,
)
from discussion_moderation.common.prompts import CLASSIFIER_PROMPT


class ClassifierAgent(AgentMixin):
    """Classifier agent using the AgentMixin pattern."""

    def __init__(self) -> None:
        self.agent: Agent[ClassifierDeps, ClassificationResult] = Agent(
            "anthropic:claude-sonnet-4-20250514",
            output_type=ClassificationResult,
        )
        self._register_system_prompt()

    def _build_system_prompt(self, ctx: RunContext[ClassifierDeps]) -> str:
        return CLASSIFIER_PROMPT.format(
            context_type=ctx.deps.context_type,
            stalled_threshold=ctx.deps.stalled_threshold_hours,
            current_timestamp=(ctx.deps.current_timestamp.isoformat()),
        )


classify = ClassifierAgent().agent
