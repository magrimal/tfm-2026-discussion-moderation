"""Orchestrator agent: Phase 2 role selection.

Selects which facilitation role should handle the intervention
based on the classification and intervention decision (ADR 0004).
Does NOT select the action or technique; that is the role agent's
responsibility.
"""

from dataclasses import dataclass

from pydantic_ai import Agent, RunContext

from discussion_moderation.agents.base import AgentMixin
from discussion_moderation.agents.roles import ROLE_AGENT_CLASSES
from discussion_moderation.config import get_settings
from discussion_moderation.models import (
    ClassificationResult,
    DiscussionThread,
    InterventionDecision,
    RoleSelection,
)
from discussion_moderation.utils import format_thread


@dataclass
class OrchestratorDeps:
    """Dependencies for the orchestrator agent.

    Attributes:
        classification: The classification agent's output.
        intervention: The intervention agent's decision and reasoning.
        thread: The discussion thread being analyzed.
        discussion_context: Human-readable description of the
            discussion type. Passed through from settings so the
            agent understands the deployment context.
        previous_feedback: Feedback from a failed retry, if any.
    """

    classification: ClassificationResult
    intervention: InterventionDecision
    thread: DiscussionThread
    discussion_context: str
    previous_feedback: str | None = None


class OrchestratorAgent(AgentMixin):
    """Orchestrator agent using the AgentMixin pattern."""

    PERSONALITY = """\
You are an expert facilitation role selector for course discussions.\
"""

    CONSTRAINTS = """\
You do not select a specific technique or generate a response - those
belong to the role agent.

Selecting the wrong role is worse than not intervening at all: an
intellectual intervention during active exploration interrupts
productive struggle; a social intervention in a healthy debate is
unnecessary noise; an organizational closure too early shuts down
thinking.

When two roles seem equally appropriate, prefer the one that acts at
the lowest level of intrusion.\
"""

    CONTEXT_TEMPLATE = """\
Discussion context: {discussion_context}
Discussion state: **{discussion_state}**
Classification reasoning: {classification_reasoning}
Intervention rationale: {intervention_reasoning}

Available roles:
{role_descriptions}{retry_context}\
"""

    INSTRUCTIONS = """\
Select exactly ONE role. Do not select a specific action or
technique; the role agent decides that. Explain why this role
is the best fit for the current state and why the alternatives
were not chosen.\
"""

    def __init__(self, model: str = "") -> None:
        self.agent = Agent(
            model or get_settings().llm_model,
            output_type=RoleSelection,
        )
        self.register_system_prompt()

    @staticmethod
    def build_role_descriptions() -> str:
        """Build the role menu shown to the agent at selection time.

        Returns:
            Formatted string listing each role name and description.
        """
        return "\n".join(
            f"- **{cls.ROLE.value}**: {cls.DESCRIPTION}"
            for cls in ROLE_AGENT_CLASSES
        )

    def build_system_prompt(self, ctx: RunContext[OrchestratorDeps]) -> str:
        """Build the system prompt with runtime context values.

        Args:
            ctx: Run context with orchestrator dependencies.

        Returns:
            Formatted system prompt string.
        """
        retry_context = ""
        if ctx.deps.previous_feedback:
            retry_context = (
                f"\n\nPrevious attempt feedback: "
                f"{ctx.deps.previous_feedback}\n"
                "Select a DIFFERENT role this time."
            )
        return self.build_prompt().format(
            discussion_context=ctx.deps.discussion_context,
            discussion_state=ctx.deps.classification.state.value,
            classification_reasoning=ctx.deps.classification.reasoning,
            intervention_reasoning=ctx.deps.intervention.reasoning,
            role_descriptions=self.build_role_descriptions(),
            retry_context=retry_context,
        )

    async def run(
        self,
        thread: DiscussionThread,
        deps: OrchestratorDeps,
    ) -> RoleSelection:
        """Select a facilitation role for a classified thread.

        Args:
            thread: The discussion thread.
            deps: Orchestrator dependencies including classification
                and intervention decision.

        Returns:
            RoleSelection with the chosen role and reasoning.
        """
        prompt = format_thread(thread)
        result = await self.agent.run(prompt, deps=deps)
        return result.output


orchestrator = OrchestratorAgent()
