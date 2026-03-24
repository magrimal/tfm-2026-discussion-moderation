"""Classifier agent: Phase 1 of the intervention model.

Classifies the discussion state and decides whether intervention
is warranted (ADR 0003, Fase 1).
"""

from pydantic_ai import Agent, RunContext

from discussion_moderation.common.prompts import (
    CLASSIFIER_PROMPT,
    format_thread,
)
from discussion_moderation.common.types import (
    ClassificationResult,
    ClassifierDeps,
    DiscussionThread,
)

classifier_agent: Agent[ClassifierDeps, ClassificationResult] = Agent(
    "anthropic:claude-sonnet-4-20250514",
    output_type=ClassificationResult,
)


@classifier_agent.system_prompt
async def _build_system_prompt(
    ctx: RunContext[ClassifierDeps],
) -> str:
    """Build the classifier system prompt from deps.

    Description:
        Fills the classifier prompt template with runtime values
        from the agent dependencies.

    Args:
        ctx: Run context with classifier dependencies.

    Returns:
        The parameterized system prompt string.
    """
    return CLASSIFIER_PROMPT.format(
        context_type="asynchronous academic discussion threads",
        stalled_threshold=ctx.deps.stalled_threshold_hours,
        current_timestamp=(ctx.deps.current_timestamp.isoformat()),
    )


async def classify(
    thread: DiscussionThread,
    deps: ClassifierDeps,
) -> ClassificationResult:
    """Classify a discussion thread and decide on intervention.

    Description:
        Runs the classifier agent against the given thread,
        producing a classification result with state, intervention
        decision, and reasoning.

    Args:
        thread: The discussion thread to classify.
        deps: Classifier dependencies (threshold, timestamp).

    Returns:
        ClassificationResult with state and intervention decision.
    """
    prompt = format_thread(thread, now=deps.current_timestamp)
    result = await classifier_agent.run(prompt, deps=deps)
    return result.output
