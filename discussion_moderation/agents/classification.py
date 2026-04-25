"""Classification agent: Phase 1a of the intervention model.

Detects the current discussion state and produces reasoning about
participation trajectory. Does not decide whether to intervene;
that is the intervention agent's responsibility (ADR 0003, Fase 1).
"""

from dataclasses import dataclass
from datetime import datetime

from pydantic_ai import Agent, RunContext
from pydantic_ai.models import Model
from pydantic_ai.output import PromptedOutput

from discussion_moderation.agents.base import AgentMixin
from discussion_moderation.config import build_model, get_settings
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
    discussion_context: str


class ClassificationAgent(AgentMixin):
    """Classification agent: detects discussion state and trajectory."""

    PERSONALITY = """\
You are a learning scientist reading an asynchronous academic
discussion thread.\
"""

    CONSTRAINTS = """\
You do not decide whether to intervene - that belongs to the next
pipeline node.

Your output is the primary signal the intervention agent uses to
decide whether and how to act. Accuracy here determines everything
downstream.\
"""

    CONTEXT_TEMPLATE = """\
Discussion context: {discussion_context}
Current timestamp: {current_timestamp}
Stalled threshold: {stalled_threshold} hours without new posts\
"""

    INSTRUCTIONS = """\
Read the thread and produce a structured classification across
five fields.

**state** - one of:
- new: No replies to the initial post.
- active: Posts exchanged within the expected time window.
- stalled: No new posts for {stalled_threshold}+ hours.
- conflictive: Aggressive, dismissive, or competitive language
  present - including dynamics that may be silencing participants.
- convergent: Participants reaching genuine synthesis or
  conclusions (not just stopping to post).
- off_topic: Discussion has drifted from the assigned topic.

**trajectory** - one of:
- growing: Engagement increasing over time.
- stable: Consistent participation, not growing or declining.
- declining: Was more active; pace is slowing or has stopped.
- never_started: Topic posted but never generated real exchange.

**participation_balance** - one of:
- distributed: Contributions spread across participants with
  student-to-student exchange present.
- dominated: One or two voices account for most posts; others
  are absent or silent after an initial post.
- instructor_centered: Most exchange is directed at the
  instructor rather than between students.

**discourse_quality** - one of:
- substantive: Posts express reasoning, build on prior
  contributions, or are supported by evidence.
- mixed: Some posts are substantive; others are formulaic.
- formulaic: Posts are surface-level ("I agree", "Good point")
  without reasoning or connection to prior contributions.

**inquiry_phase** - one of:
- triggering: A question or problem has been posed; responses
  are minimal or absent.
- exploration: Participants sharing perspectives, but ideas are
  not yet being connected.
- integration: Participants building on each other and
  connecting ideas across contributions.
- resolution: Thread converging toward conclusions or synthesis.

In **reasoning**, describe what you observed that led to each
classification. Note the nature of the last posts (opening
moves such as questions, or closing moves such as agreements)
as this informs intervention timing.\
"""

    def __init__(self, model: Model | str | None = None) -> None:
        """Initialize the classification agent.

        Args:
            model: Optional pydantic-ai model override. Defaults to the
                model configured via FACILITATION_CLASSIFICATION_MODEL
                or FACILITATION_LLM_MODEL.
        """
        settings = get_settings()
        self.agent = Agent(
            model
            or build_model(
                settings.model_for("classification"), settings.llm_api_key
            ),
            output_type=PromptedOutput(ClassificationResult),
            retries=3,
        )
        self.register_system_prompt()

    def build_system_prompt(self, ctx: RunContext[ClassificationDeps]) -> str:
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
