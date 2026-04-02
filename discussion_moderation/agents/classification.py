"""Classification agent: Phase 1a of the intervention model.

Detects the current discussion state and produces reasoning about
participation trajectory. Does not decide whether to intervene;
that is the intervention agent's responsibility (ADR 0003, Fase 1).
"""

from dataclasses import dataclass
from datetime import datetime

from pydantic_ai import Agent, RunContext

from discussion_moderation.agents.base import AgentMixin
from discussion_moderation.config import get_settings
from discussion_moderation.models import ClassificationResult, DiscussionThread
from discussion_moderation.utils import format_thread


@dataclass
class ClassificationDeps:
    """Dependencies for the classification agent.

    Attributes:
        stalled_threshold_hours: Hours without posts before a
            thread is considered stalled.
        current_timestamp: Reference time for recency judgments.
        discussion_context: Human-readable description of the
            discussion type, e.g. "asynchronous academic discussion
            threads". Injected into the prompt so the agent knows
            the deployment context.
    """

    stalled_threshold_hours: int
    current_timestamp: datetime
    discussion_context: str = "asynchronous academic discussion threads"


class ClassificationAgent(AgentMixin):
    """Classification agent: detects discussion state and trajectory."""

    PERSONALITY = """\
You are a learning scientist observing course discussions.
Your only job is to observe and categorize: you detect the current
state of the thread and describe the participation trajectory.
You do not decide whether to intervene; that is a separate step.

Describe what you see accurately, including trajectory (engagement
growing, stable, or declining). A thread that was active and has
gone quiet is a different observation from one that never started.
Note this distinction explicitly because it matters for downstream
decisions.\
"""

    CONTEXT_TEMPLATE = """\
Discussion context: {discussion_context}
Current timestamp: {current_timestamp}
Stalled threshold: {stalled_threshold} hours without new posts\
"""

    INSTRUCTIONS = """\
Read the thread and classify it as one of:
- **new**: No replies yet.
- **active**: Healthy exchange in progress.
- **stalled**: No new posts for {stalled_threshold}+ hours since
  the last post.
- **conflictive**: Aggressive, dismissive, or disrespectful
  language present.
- **convergent**: Participants are reaching agreement or
  conclusions.
- **off_topic**: Discussion has drifted from the assigned topic.

In your reasoning, describe the participation trajectory: is
engagement growing, declining, or stable? A declining thread
(was active, now silent) requires different action than one
that never started. Note trajectory explicitly so downstream
agents can act on it.\
"""

    def __init__(self, model: str = "") -> None:
        self.agent: Agent[ClassificationDeps, ClassificationResult] = Agent(
            model or get_settings().llm_model,
            output_type=ClassificationResult,
        )
        self._register_system_prompt()

    def _build_system_prompt(
        self, ctx: RunContext[ClassificationDeps]
    ) -> str:
        """Build the system prompt with runtime context values.

        Args:
            ctx: Run context with classification dependencies.

        Returns:
            Formatted system prompt string.
        """
        return self.build_prompt().format(
            discussion_context=ctx.deps.discussion_context,
            stalled_threshold=ctx.deps.stalled_threshold_hours,
            current_timestamp=ctx.deps.current_timestamp.isoformat(),
        )

    async def run(
        self,
        thread: DiscussionThread,
        deps: ClassificationDeps,
    ) -> ClassificationResult:
        """Classify the discussion state of a thread.

        Args:
            thread: The discussion thread to classify.
            deps: Classification dependencies.

        Returns:
            ClassificationResult with state and trajectory reasoning.
        """
        prompt = format_thread(thread, now=deps.current_timestamp)
        result = await self.agent.run(prompt, deps=deps)
        return result.output


classification_agent = ClassificationAgent()
