"""Layer 1: pipeline wiring tests using pydantic_ai TestModel.

TestModel replaces the LLM with a deterministic stub that produces
minimal valid structured output and calls all registered tools.
These tests verify deps flow correctly, tools run without errors,
and each agent produces the right output type - without any API key.
"""

from datetime import UTC, datetime

import pytest
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
