"""Layer 1: pipeline wiring tests using pydantic_ai TestModel.

TestModel replaces the LLM with a deterministic stub that produces
minimal valid structured output and calls all registered tools.
These tests verify deps flow correctly, tools run without errors,
and each agent produces the right output type - without any API key.
"""

import json
from datetime import UTC, datetime

import pytest
from pydantic_ai.exceptions import UnexpectedModelBehavior
from pydantic_ai.messages import ModelResponse, TextPart, ToolCallPart
from pydantic_ai.models.function import FunctionModel
from pydantic_ai.models.test import TestModel

from discussion_moderation.agents.classification import (
    ClassificationAgent,
    ClassificationDeps,
)
from discussion_moderation.agents.intervention import (
    InterventionAgent,
    InterventionDeps,
)
from discussion_moderation.agents.orchestrator import (
    OrchestratorAgent,
    OrchestratorDeps,
)
from discussion_moderation.agents.roles import (
    ROLE_AGENT_CLASSES_BY_ROLE,
    RoleAgentDeps,
)
from discussion_moderation.constants import (
    ActionCategory,
    DiscourseQuality,
    DiscussionState,
    DiscussionTrajectory,
    FacilitationRole,
    InquiryPhase,
    ParticipationBalance,
)
from discussion_moderation.models import (
    ClassificationResult,
    DiscussionThread,
    FacilitationResponse,
    InterventionDecision,
    RoleSelection,
)
from discussion_moderation.tools.stub import StubLMSBackend

NOW = datetime(2026, 3, 12, 14, 0, tzinfo=UTC)

CONTEXT = "asynchronous academic discussion threads"


# --- Fixtures ---


def _thread() -> DiscussionThread:
    return DiscussionThread(
        id="t-test",
        course_id="course-v1:UCM+TFM+2026",
        title="Test thread",
        learning_objectives=["Understand X"],
        created_at=NOW,
        body="What is X?",
        author="alice",
    )


def _classification() -> ClassificationResult:
    return ClassificationResult(
        state=DiscussionState.STALLED,
        trajectory=DiscussionTrajectory.DECLINING,
        participation_balance=ParticipationBalance.DISTRIBUTED,
        discourse_quality=DiscourseQuality.MIXED,
        inquiry_phase=InquiryPhase.EXPLORATION,
        reasoning="Thread went quiet after one reply.",
    )


def _intervention() -> InterventionDecision:
    return InterventionDecision(
        should_intervene=True,
        reasoning="Declining trajectory warrants a nudge.",
    )


def _role_selection() -> RoleSelection:
    return RoleSelection(
        role=FacilitationRole.SOCIAL,
        reasoning="Re-engage the silent participants.",
    )


# --- Classification agent ---


@pytest.mark.anyio
async def test_classification_agent_returns_classification_result():
    deps = ClassificationDeps(
        stalled_threshold_hours=48,
        current_timestamp=NOW,
        discussion_context=CONTEXT,
    )
    agent = ClassificationAgent(model=TestModel())
    result, _ = await agent.run(_thread(), deps)

    assert isinstance(result, ClassificationResult)


@pytest.mark.anyio
async def test_classification_agent_result_has_valid_state():
    deps = ClassificationDeps(
        stalled_threshold_hours=48,
        current_timestamp=NOW,
        discussion_context=CONTEXT,
    )
    agent = ClassificationAgent(model=TestModel())
    result, _ = await agent.run(_thread(), deps)

    assert isinstance(result.state, DiscussionState)


@pytest.mark.anyio
async def test_classification_agent_result_has_reasoning():
    deps = ClassificationDeps(
        stalled_threshold_hours=48,
        current_timestamp=NOW,
        discussion_context=CONTEXT,
    )
    agent = ClassificationAgent(model=TestModel())
    result, _ = await agent.run(_thread(), deps)

    assert isinstance(result.reasoning, str)


# --- Intervention agent ---


@pytest.mark.anyio
async def test_intervention_agent_returns_intervention_decision():
    deps = InterventionDeps(
        classification=_classification(),
        stalled_threshold_hours=48,
        current_timestamp=NOW,
        discussion_context=CONTEXT,
    )
    agent = InterventionAgent(model=TestModel())
    result, _ = await agent.run(_thread(), deps)

    assert isinstance(result, InterventionDecision)


@pytest.mark.anyio
async def test_intervention_agent_result_has_bool_should_intervene():
    deps = InterventionDeps(
        classification=_classification(),
        stalled_threshold_hours=48,
        current_timestamp=NOW,
        discussion_context=CONTEXT,
    )
    agent = InterventionAgent(model=TestModel())
    result, _ = await agent.run(_thread(), deps)

    assert isinstance(result.should_intervene, bool)


@pytest.mark.anyio
async def test_intervention_agent_caps_classification_reasoning():
    """Regression test: long classification reasoning used to be
    inlined verbatim into the intervention prompt (routinely several
    hundred words - see cap_reasoning in utils.py). Confirm it's
    capped in the actual system prompt sent to the model.
    """
    long_reasoning = "x" * 2000
    deps = InterventionDeps(
        classification=ClassificationResult(
            state=DiscussionState.STALLED,
            trajectory=DiscussionTrajectory.DECLINING,
            participation_balance=ParticipationBalance.DISTRIBUTED,
            discourse_quality=DiscourseQuality.MIXED,
            inquiry_phase=InquiryPhase.EXPLORATION,
            reasoning=long_reasoning,
        ),
        stalled_threshold_hours=48,
        current_timestamp=NOW,
        discussion_context=CONTEXT,
    )
    agent = InterventionAgent(model=TestModel())
    _, messages = await agent.run(_thread(), deps)

    system_prompt = next(
        part["content"]
        for message in messages
        for part in message["parts"]
        if part.get("part_kind") == "system-prompt"
    )
    assert long_reasoning not in system_prompt
    assert "[truncated]" in system_prompt


# --- Orchestrator agent ---


@pytest.mark.anyio
async def test_orchestrator_returns_role_selection():
    thread = _thread()
    deps = OrchestratorDeps(
        classification=_classification(),
        intervention=_intervention(),
        thread=thread,
        discussion_context=CONTEXT,
    )
    agent = OrchestratorAgent(model=TestModel())
    result, _ = await agent.run(thread, deps)

    assert isinstance(result, RoleSelection)


@pytest.mark.anyio
async def test_orchestrator_result_has_valid_role():
    thread = _thread()
    deps = OrchestratorDeps(
        classification=_classification(),
        intervention=_intervention(),
        thread=thread,
        discussion_context=CONTEXT,
    )
    agent = OrchestratorAgent(model=TestModel())
    result, _ = await agent.run(thread, deps)

    assert isinstance(result.role, FacilitationRole)


@pytest.mark.anyio
async def test_orchestrator_caps_reasoning_in_prompt():
    """Regression test: classification and intervention reasoning
    used to be inlined verbatim into the orchestrator prompt. Confirm
    both are capped in the actual system prompt sent to the model.
    """
    long_reasoning = "y" * 2000
    thread = _thread()
    deps = OrchestratorDeps(
        classification=ClassificationResult(
            state=DiscussionState.STALLED,
            trajectory=DiscussionTrajectory.DECLINING,
            participation_balance=ParticipationBalance.DISTRIBUTED,
            discourse_quality=DiscourseQuality.MIXED,
            inquiry_phase=InquiryPhase.EXPLORATION,
            reasoning=long_reasoning,
        ),
        intervention=InterventionDecision(
            should_intervene=True, reasoning=long_reasoning
        ),
        thread=thread,
        discussion_context=CONTEXT,
    )
    agent = OrchestratorAgent(model=TestModel())
    _, messages = await agent.run(thread, deps)

    system_prompt = next(
        part["content"]
        for message in messages
        for part in message["parts"]
        if part.get("part_kind") == "system-prompt"
    )
    assert long_reasoning not in system_prompt
    assert system_prompt.count("[truncated]") == 2


# --- Role agents ---


@pytest.mark.anyio
@pytest.mark.parametrize("role", list(FacilitationRole))
async def test_role_agent_returns_facilitation_response(role):
    thread = _thread()
    deps = RoleAgentDeps(
        role_selection=_role_selection(),
        classification=_classification(),
        intervention=_intervention(),
        thread=thread,
        discussion_context=CONTEXT,
    )
    agent = ROLE_AGENT_CLASSES_BY_ROLE[role](model=TestModel())
    result, _ = await agent.run(thread, deps)

    assert isinstance(result, FacilitationResponse)


@pytest.mark.anyio
@pytest.mark.parametrize("role", list(FacilitationRole))
async def test_role_agent_result_has_technique_used(role):
    thread = _thread()
    deps = RoleAgentDeps(
        role_selection=_role_selection(),
        classification=_classification(),
        intervention=_intervention(),
        thread=thread,
        discussion_context=CONTEXT,
    )
    agent = ROLE_AGENT_CLASSES_BY_ROLE[role](model=TestModel())
    response, _ = await agent.run(thread, deps)

    assert isinstance(response.technique_used, str)


@pytest.mark.anyio
@pytest.mark.parametrize("role", list(FacilitationRole))
async def test_role_agent_result_has_valid_action_category(role):
    thread = _thread()
    deps = RoleAgentDeps(
        role_selection=_role_selection(),
        classification=_classification(),
        intervention=_intervention(),
        thread=thread,
        discussion_context=CONTEXT,
    )
    agent = ROLE_AGENT_CLASSES_BY_ROLE[role](model=TestModel())
    response, _ = await agent.run(thread, deps)

    assert isinstance(response.action_category, ActionCategory)


@pytest.mark.anyio
@pytest.mark.parametrize("role", list(FacilitationRole))
async def test_role_agent_confidence_in_valid_range(role):
    thread = _thread()
    deps = RoleAgentDeps(
        role_selection=_role_selection(),
        classification=_classification(),
        intervention=_intervention(),
        thread=thread,
        discussion_context=CONTEXT,
    )
    agent = ROLE_AGENT_CLASSES_BY_ROLE[role](model=TestModel())
    response, _ = await agent.run(thread, deps)

    assert 0.0 <= response.confidence <= 1.0


@pytest.mark.anyio
async def test_role_agent_tools_run_without_errors():
    """Verify retrieve_techniques and get_thread_history don't raise."""
    thread = _thread()
    deps = RoleAgentDeps(
        role_selection=_role_selection(),
        classification=_classification(),
        intervention=_intervention(),
        thread=thread,
        discussion_context=CONTEXT,
        history_store=None,
    )
    agent = ROLE_AGENT_CLASSES_BY_ROLE[FacilitationRole.SOCIAL](
        model=TestModel(call_tools="all")
    )
    response, _ = await agent.run(thread, deps)

    assert isinstance(response, FacilitationResponse)


@pytest.mark.anyio
async def test_get_thread_history_tolerates_hallucinated_thread_id():
    """Regression test: live idril runs show the model occasionally
    calling get_thread_history with a hallucinated thread_id argument
    despite the docstring saying it takes none, rejected with
    extra_forbidden - burning a retry in runs that are already
    struggling with format compliance. The tool must accept and
    ignore it instead.
    """
    call_state = {"called": False}

    def _call_with_bad_arg(messages, info):  # noqa: ARG001
        if not call_state["called"]:
            call_state["called"] = True
            return ModelResponse(
                parts=[
                    ToolCallPart(
                        tool_name="get_thread_history",
                        args={"thread_id": "hallucinated"},
                    )
                ]
            )
        return ModelResponse(
            parts=[
                ToolCallPart(
                    tool_name="final_result",
                    args={
                        "response_text": "hi",
                        "technique_used": "de_escalate",
                        "action_category": "moderation",
                        "confidence": 0.9,
                        "reasoning": "test",
                        "post_to_thread": True,
                    },
                )
            ]
        )

    thread = _thread()
    deps = RoleAgentDeps(
        role_selection=_role_selection(),
        classification=_classification(),
        intervention=_intervention(),
        thread=thread,
        discussion_context=CONTEXT,
        history_store=None,
    )
    agent = ROLE_AGENT_CLASSES_BY_ROLE[FacilitationRole.MODERATOR](
        model=FunctionModel(_call_with_bad_arg)
    )

    response, messages = await agent.run(thread, deps)

    assert isinstance(response, FacilitationResponse)
    tool_returns = [
        part
        for message in messages
        for part in message["parts"]
        if part.get("part_kind") == "tool-return"
        and part.get("tool_name") == "get_thread_history"
    ]
    assert tool_returns
    assert "No intervention history" in tool_returns[0]["content"]
    assert not any(
        part.get("part_kind") == "retry-prompt"
        for message in messages
        for part in message["parts"]
    )


@pytest.mark.anyio
async def test_get_thread_history_second_call_in_same_response_is_refused():
    """Regression test: live idril runs show the model calling
    get_thread_history/retrieve_techniques again after already getting
    a result, ignoring the "call at most once" prompt instruction.
    The second call must be refused in the tool result itself rather
    than silently returning the same payload again.
    """

    def _call_twice(messages, info):  # noqa: ARG001
        tool_call_count = sum(
            1
            for m in messages
            if isinstance(m, ModelResponse)
            for p in m.parts
            if getattr(p, "tool_name", None) == "get_thread_history"
        )
        if tool_call_count < 2:
            return ModelResponse(
                parts=[ToolCallPart(tool_name="get_thread_history", args={})]
            )
        return ModelResponse(
            parts=[
                ToolCallPart(
                    tool_name="final_result",
                    args={
                        "response_text": "hi",
                        "technique_used": "de_escalate",
                        "action_category": "moderation",
                        "confidence": 0.9,
                        "reasoning": "test",
                        "post_to_thread": True,
                    },
                )
            ]
        )

    thread = _thread()
    deps = RoleAgentDeps(
        role_selection=_role_selection(),
        classification=_classification(),
        intervention=_intervention(),
        thread=thread,
        discussion_context=CONTEXT,
        history_store=None,
    )
    agent = ROLE_AGENT_CLASSES_BY_ROLE[FacilitationRole.MODERATOR](
        model=FunctionModel(_call_twice)
    )

    _, messages = await agent.run(thread, deps)

    tool_returns = [
        part["content"]
        for message in messages
        for part in message["parts"]
        if part.get("part_kind") == "tool-return"
        and part.get("tool_name") == "get_thread_history"
    ]
    assert len(tool_returns) == 2
    assert "already called" in tool_returns[1]


@pytest.mark.anyio
async def test_moderator_flag_content_tool_reaches_backend():
    """Regression test: flag_content used to raise AttributeError against
    every LMSBackend (none of them implemented it - see
    docs/experiments/test-sheets/reliability-security.csv row 06). Forcing
    TestModel to call every Moderator tool, including flag_content,
    against a StubLMSBackend verifies the call now succeeds end-to-end.
    """
    thread = _thread()
    backend = StubLMSBackend({thread.id: thread})
    deps = RoleAgentDeps(
        role_selection=RoleSelection(
            role=FacilitationRole.MODERATOR,
            reasoning="Overt hostility requires moderator review.",
        ),
        classification=_classification(),
        intervention=_intervention(),
        thread=thread,
        discussion_context=CONTEXT,
        lms_backend=backend,
        history_store=None,
    )
    agent = ROLE_AGENT_CLASSES_BY_ROLE[FacilitationRole.MODERATOR](
        model=TestModel(call_tools="all")
    )
    response, _ = await agent.run(thread, deps)

    assert isinstance(response, FacilitationResponse)
    assert len(backend.flagged_content) == 1
    assert backend.flagged_content[0]["post_id"]


@pytest.mark.anyio
async def test_role_agent_failure_preserves_partial_messages():
    """Regression test: when output validation retries are exhausted,
    the raw model turns must not be silently lost. Live idril runs
    with ollama:qwen3.5:27b hit "Exceeded maximum retries" with no
    pipeline_messages["role"] recorded at all - no way to see what
    the model actually produced. A model that only ever emits
    unparseable text forces the same exhaustion deterministically;
    the exception raised must carry a `partial_messages` attribute
    with the model's actual (failed) turns.
    """

    def _always_invalid(messages, info):  # noqa: ARG001
        return ModelResponse(parts=[TextPart(content="not json at all")])

    thread = _thread()
    deps = RoleAgentDeps(
        role_selection=_role_selection(),
        classification=_classification(),
        intervention=_intervention(),
        thread=thread,
        discussion_context=CONTEXT,
        history_store=None,
    )
    agent = ROLE_AGENT_CLASSES_BY_ROLE[FacilitationRole.SOCIAL](
        model=FunctionModel(_always_invalid)
    )

    with pytest.raises(UnexpectedModelBehavior) as exc_info:
        await agent.run(thread, deps)

    partial_messages = exc_info.value.partial_messages  # type: ignore[attr-defined]
    assert partial_messages
    assert any(
        "not json at all" in json.dumps(msg) for msg in partial_messages
    )


@pytest.mark.anyio
async def test_role_agent_salvages_good_content_with_bad_json_escaping():
    """Regression test: a live idril run produced a FacilitationResponse
    with entirely valid, on-topic content, but pydantic-ai rejected it
    outright because a multi-line "reasoning" field used literal
    newlines instead of "\\n" escapes - the exact defect
    json_repair.py targets. Confirm the agent salvages it instead of
    raising, once pydantic-ai's own retries are exhausted.
    """
    malformed = (
        '{"response_text": "Some question?", '
        '"technique_used": "focused_reframing_prompt", '
        '"action_category": "intellectual", '
        '"confidence": 0.95, '
        '"reasoning": "- point one\n'
        "   \n"
        '- point two", '
        '"post_to_thread": true}'
    )

    def _always_malformed(messages, info):  # noqa: ARG001
        return ModelResponse(parts=[TextPart(content=malformed)])

    thread = _thread()
    deps = RoleAgentDeps(
        role_selection=_role_selection(),
        classification=_classification(),
        intervention=_intervention(),
        thread=thread,
        discussion_context=CONTEXT,
        history_store=None,
    )
    agent = ROLE_AGENT_CLASSES_BY_ROLE[FacilitationRole.SOCIAL](
        model=FunctionModel(_always_malformed)
    )

    response, messages = await agent.run(thread, deps)

    assert response.technique_used == "focused_reframing_prompt"
    assert "point one" in response.reasoning
    assert "point two" in response.reasoning
    assert messages


@pytest.mark.anyio
async def test_retrieve_techniques_caps_examples_per_technique():
    """Regression test: retrieve_techniques used to return every example
    for all ~30 techniques, embedded in the growing role-agent
    conversation on every retry. Live idril runs show input_tokens
    pinning at ~4096 (Ollama's default context window) on longer
    role-agent runs, right after this tool gets called - capping
    examples to 1 per technique is one of the fixes to reduce that.
    """
    thread = _thread()
    deps = RoleAgentDeps(
        role_selection=_role_selection(),
        classification=_classification(),
        intervention=_intervention(),
        thread=thread,
        discussion_context=CONTEXT,
        history_store=None,
    )
    agent = ROLE_AGENT_CLASSES_BY_ROLE[FacilitationRole.SOCIAL](
        model=TestModel(call_tools=["retrieve_techniques"])
    )

    _, messages = await agent.run(thread, deps)

    tool_returns = [
        part
        for message in messages
        for part in message["parts"]
        if part.get("part_kind") == "tool-return"
        and part.get("tool_name") == "retrieve_techniques"
    ]
    assert tool_returns
    techniques = json.loads(tool_returns[0]["content"])
    assert techniques
    assert all(len(t["examples"]) <= 1 for t in techniques)
