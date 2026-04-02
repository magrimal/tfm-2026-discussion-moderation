"""Classifier agent: Phase 1 of the intervention model.

Classifies the discussion state and decides whether intervention
is warranted (ADR 0003, Fase 1).
"""

from dataclasses import dataclass
from datetime import datetime

from pydantic_ai import Agent, RunContext

from discussion_moderation.agents.base import AgentMixin
from discussion_moderation.models import ClassificationResult, DiscussionThread
from discussion_moderation.utils import format_thread


@dataclass
class ClassifierDeps:
    """Dependencies for the classifier agent.

    Attributes:
        stalled_threshold_hours: Hours without posts before a
            thread is considered stalled.
        current_timestamp: Reference time for recency judgments.
        context_type: Description of the discussion context.
    """

    stalled_threshold_hours: int
    current_timestamp: datetime
    context_type: str = "asynchronous academic discussion threads"


class ClassifierAgent(AgentMixin):
    """Classifier agent using the AgentMixin pattern."""

    PROMPT = """\
# Personality
You are a discussion analysis agent for {context_type}.

# Context
Current timestamp: {current_timestamp}
Stalled threshold: {stalled_threshold} hours without new posts

# Examples
No embedded examples. Classify based on state definitions below.

# Instructions
Read the thread and classify it as one of:
- **new**: No replies yet.
- **active**: Healthy exchange in progress.
- **stalled**: No new posts for {stalled_threshold}+ hours \
since the last post.
- **conflictive**: Aggressive, dismissive, or disrespectful \
language present.
- **convergent**: Participants are reaching agreement or \
conclusions.
- **off_topic**: Discussion has drifted from the assigned topic.

Then decide whether to intervene. Most states can result in \
"do not intervene". Prefer not intervening when the discussion \
is healthy.

In your reasoning, describe the participation trajectory: is \
engagement growing, declining, or stable? A declining thread \
(was active, now silent) requires different action than one \
that never started. Note trajectory explicitly so downstream \
agents can act on it.
"""

    def __init__(self) -> None:
        self.agent: Agent[ClassifierDeps, ClassificationResult] = Agent(
            "anthropic:claude-sonnet-4-20250514",
            output_type=ClassificationResult,
        )
        self._register_system_prompt()

    def _build_system_prompt(self, ctx: RunContext[ClassifierDeps]) -> str:
        return self.PROMPT.format(
            context_type=ctx.deps.context_type,
            stalled_threshold=ctx.deps.stalled_threshold_hours,
            current_timestamp=ctx.deps.current_timestamp.isoformat(),
        )

    async def run(
        self,
        thread: DiscussionThread,
        deps: ClassifierDeps,
    ) -> ClassificationResult:
        """Classify a discussion thread.

        Args:
            thread: The discussion thread to classify.
            deps: Classifier dependencies.

        Returns:
            ClassificationResult with state and intervention decision.
        """
        prompt = format_thread(thread, now=deps.current_timestamp)
        result = await self.agent.run(prompt, deps=deps)
        return result.output


classifier = ClassifierAgent()
