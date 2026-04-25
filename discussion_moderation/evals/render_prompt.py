"""Render the actual messages and tool definitions sent to the model.

Shows what pydantic-ai sends in tool-calling mode (default) vs
PromptedOutput mode (text JSON) for the classification agent.

Usage:
    uv run --env-file .env.local render-prompt | less
"""

import asyncio
import json
from datetime import UTC, datetime
from typing import Any

from pydantic_ai import Agent
from pydantic_ai.messages import ModelResponse, TextPart
from pydantic_ai.models.function import AgentInfo, FunctionModel, ModelRequest
from pydantic_ai.output import PromptedOutput

from discussion_moderation.agents.classification import (
    ClassificationAgent,
    ClassificationDeps,
)
from discussion_moderation.config import get_settings
from discussion_moderation.models import ClassificationResult, DiscussionThread
from discussion_moderation.utils import format_thread

_MINIMAL_VALID_JSON = json.dumps(
    {
        "state": "new",
        "trajectory": "never_started",
        "participation_balance": "instructor_centered",
        "discourse_quality": "formulaic",
        "inquiry_phase": "triggering",
        "reasoning": "render-only",
    }
)


async def _capture(
    output_type: Any, deps: ClassificationDeps, thread: DiscussionThread
) -> dict:
    """Run the classification agent with a capturing FunctionModel."""
    store: dict = {}

    def _fn(messages: list[ModelRequest], info: AgentInfo) -> ModelResponse:
        store["messages"] = messages
        store["info"] = info
        return ModelResponse(parts=[TextPart(content=_MINIMAL_VALID_JSON)])

    # Create a fresh Agent with the correct output_type at instantiation time.
    # pydantic-ai bakes tool schema into the agent at creation, so we cannot
    # swap _output_type after the fact.
    inner = Agent(FunctionModel(_fn), output_type=output_type, retries=3)
    # Borrow ClassificationAgent's system prompt without running __init__.
    proxy = ClassificationAgent.__new__(ClassificationAgent)
    proxy.agent = inner
    proxy.register_system_prompt()

    try:
        prompt = format_thread(thread, now=deps.current_timestamp)
        await inner.run(prompt, deps=deps)
    except Exception:
        pass

    return store


def _sep(title: str) -> None:
    print()
    print("=" * 72)
    print(f"  {title}")
    print("=" * 72)
    print()


def _print_messages(messages: list) -> None:
    for msg in messages:
        for part in msg.parts:
            label = type(part).__name__
            content = getattr(part, "content", repr(part))
            print(f"[{label}]")
            print(content)
            print()


def _print_tools(tools: list) -> None:
    if not tools:
        print("(none)")
        return
    for t in tools:
        print(f"name        : {t.name}")
        desc = (
            (t.description or "")[:100] + "..."
            if len(t.description or "") > 100
            else t.description
        )
        print(f"description : {desc}")
        print("schema      :")
        print(json.dumps(t.parameters_json_schema, indent=2))
        print()


async def main_async() -> None:
    settings = get_settings()
    thread = DiscussionThread(
        id="render-test",
        course_id="course-v1:UCM+TFM+2026",
        title="What are the main privacy risks in LLM training data?",
        body="Please share your thoughts on this topic.",
        author="prof.garcia",
        author_label="Instructor",
        created_at=datetime(2026, 3, 12, 9, 0, tzinfo=UTC),
    )
    deps = ClassificationDeps(
        stalled_threshold_hours=settings.stalled_threshold_hours,
        current_timestamp=datetime.now(UTC),
        discussion_context=settings.discussion_context,
    )

    _sep("MODE A: default output type — tool-calling")
    a = await _capture(ClassificationResult, deps, thread)
    if a.get("messages"):
        _print_messages(a["messages"])
        print("--- output tools ---")
        _print_tools(a["info"].output_tools)
        print(f"allow_text_output: {a['info'].allow_text_output}")

    _sep("MODE B: PromptedOutput — text JSON")
    b = await _capture(PromptedOutput(ClassificationResult), deps, thread)
    if b.get("messages"):
        _print_messages(b["messages"])
        print("--- output tools ---")
        _print_tools(b["info"].output_tools)
        print(f"allow_text_output: {b['info'].allow_text_output}")


def main() -> None:
    asyncio.run(main_async())
