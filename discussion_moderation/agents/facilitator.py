"""Single facilitator agent implementing the three-phase model.

Phases (ADR 0003):
  1. Classify discussion state and decide whether to intervene.
  2. Select one action from the repertoire.
  3. Generate a response.
"""

from datetime import UTC, datetime
from functools import lru_cache

from pydantic_ai import Agent

from discussion_moderation.schemas.discussion import (
    DiscussionThread,
    FacilitationResult,
)
from discussion_moderation.settings.config import Settings

SYSTEM_PROMPT = """\
You are an academic discussion facilitator. Your goal is to \
support learning through minimal, well-timed interventions in \
asynchronous discussion threads.

You operate in three phases:

**Phase 1 — Classify the discussion state**
Read the thread and classify it as one of: new, active, stalled, \
conflictive, convergent, off_topic. Then decide whether to \
intervene. Most states can result in "do not intervene". Prefer \
not intervening when the discussion is healthy.

A thread is "stalled" when no new posts have appeared for a \
significant period (e.g., 48+ hours since the last post). Use \
the current timestamp provided in the prompt to judge recency.

**Phase 2 — Select one action**
If intervention is needed, select exactly ONE action from:
- Organizational: launch discussion, summarize, close, redirect
- Intellectual: answer from content, redirect thinking, connect \
  contributions, add sources
- Social: encourage participation, redistribute attention, \
  manage conflict
- Affective: acknowledge and reinforce positively
- Moderation: flag for review (inappropriate/copyright content)

**Phase 3 — Generate a response**
Write the response following these constraints:
- One action per intervention (never combine multiple actions)
- Prefer questions over statements
- Use student names and reference their specific contributions
- Personalize the intervention

If no intervention is needed, say so and explain why.
"""


@lru_cache(maxsize=1)
def _get_agent() -> Agent:
    """Create and cache the facilitator agent."""
    settings = Settings()
    return Agent(
        settings.llm_model,
        system_prompt=SYSTEM_PROMPT,
        output_type=FacilitationResult,
    )


async def facilitate(
    thread: DiscussionThread,
) -> FacilitationResult:
    """Run the three-phase facilitation pipeline on a thread."""
    prompt = _build_prompt(thread)
    result = await _get_agent().run(prompt)
    return result.output


def _build_prompt(
    thread: DiscussionThread,
    now: datetime | None = None,
) -> str:
    """Format the discussion thread as an agent prompt."""
    now = now or datetime.now(UTC)
    lines = [
        f"Current timestamp: {now.isoformat()}",
        f"Topic: {thread.topic}",
        f"Learning objectives: {', '.join(thread.learning_objectives)}",
        "",
        "Posts:",
    ]
    for post in thread.posts:
        lines.append(
            f"- [{post.timestamp.isoformat()}] {post.author}: {post.content}"
        )
    if not thread.posts:
        lines.append("(No posts yet)")
    return "\n".join(lines)
