"""Role agents: one class per facilitation role.

Each class owns its ROLE, DESCRIPTION, PERSONALITY, CONSTRAINTS, and
INSTRUCTIONS as class constants. RoleAgent is the shared base that
registers tools and builds the system prompt from those constants.
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

from pydantic_ai import Agent, RunContext

from discussion_moderation.agents.base import AgentMixin
from discussion_moderation.config import get_settings
from discussion_moderation.constants import (
    DiscussionState,
    FacilitationRole,
)
from discussion_moderation.models import (
    ClassificationResult,
    DiscussionThread,
    FacilitationResponse,
    InterventionDecision,
    RoleSelection,
)
from discussion_moderation.tools.history import InterventionRecord
from discussion_moderation.tools.knowledge_base import (
    get_anti_patterns,
    get_techniques,
)
from discussion_moderation.utils import format_thread

if TYPE_CHECKING:
    from discussion_moderation.tools.protocols import LMSBackend
    from discussion_moderation.tools.history import ThreadHistoryStore


def build_anti_pattern_text() -> str:
    return "\n".join(f"- {p}" for p in get_anti_patterns())


# Shared constraints for all role agents. Replaces the previous
# _BASE_FACILITATION_PHILOSOPHY and _SHARED_CONSTRAINTS, both of
# which bypassed the four-component prompt structure (ADR 0009).
SHARED_ROLE_CONSTRAINTS = (
    "The intervention decision was already made upstream. Your job\n"
    "is to act well.\n\n"
    "- Select exactly ONE technique and generate ONE response.\n"
    "- Prefer questions over statements. Questions preserve student\n"
    "  agency; statements reduce it.\n"
    "- Use student names and reference their specific contributions.\n"
    "  Generic responses have no social presence effect.\n"
    "- Never evaluate, grade, or judge student work.\n"
    "- Never combine multiple actions in a single intervention.\n"
    "- Call get_thread_history before selecting a technique. Do not\n"
    "  repeat interventions that produced no progress.\n"
    "- Call retrieve_techniques to see what is available for the\n"
    "  current discussion state before selecting a technique.\n"
    "- Act at the lowest level of intrusion that addresses the\n"
    "  problem. Escalate only when lower levels have failed.\n\n"
    f"Anti-patterns to avoid:\n{build_anti_pattern_text()}"
)


@dataclass
class RoleAgentDeps:
    """Dependencies for role-specific agents.

    Attributes:
        role_selection: The orchestrator's role selection.
        classification: The classification agent's output.
        intervention: The intervention agent's decision and reasoning.
        thread: The discussion thread.
        discussion_context: Human-readable description of the
            discussion type. Injected into the prompt so the agent
            knows the deployment context.
        lms_backend: Optional LMS backend for tool calls.
        history_store: Optional store for prior interventions.
    """

    role_selection: RoleSelection
    classification: ClassificationResult
    intervention: InterventionDecision
    thread: DiscussionThread
    discussion_context: str
    lms_backend: "LMSBackend | None" = None
    history_store: "ThreadHistoryStore | None" = None


class RoleAgent(AgentMixin):
    """Base class for all facilitation role agents.

    Subclasses must define ROLE, DESCRIPTION, PERSONALITY, and
    CONSTRAINTS as class-level constants. CONTEXT_TEMPLATE,
    INSTRUCTIONS, tool registration, and the system prompt builder
    are shared here.
    """

    ROLE: ClassVar[FacilitationRole]
    DESCRIPTION: ClassVar[str]
    PERSONALITY: ClassVar[str]

    CONSTRAINTS: ClassVar[str] = SHARED_ROLE_CONSTRAINTS

    CONTEXT_TEMPLATE: ClassVar[str] = """\
Discussion context: {discussion_context}
Discussion state: **{discussion_state}**
Classification reasoning: {classification_reasoning}
Intervention rationale: {intervention_reasoning}
Selected because: {selection_reasoning}\
"""

    INSTRUCTIONS: ClassVar[str] = """\
Select ONE technique from the repertoire (retrieved via
retrieve_techniques) and generate a facilitation response.

Output:
- response_text: the intervention content - a student-facing
  message for most techniques; an instructor-only summary for
  instructor_escalation
- technique_used: the name of the technique selected
- confidence: your confidence that this technique fits (0.0-1.0)
- reasoning: why this technique for this thread at this moment
- post_to_thread: true for all techniques except
  instructor_escalation, where it must be false\
"""

    def __init__(
        self,
        model: str = "",
    ) -> None:
        self.agent = Agent(
            model or get_settings().llm_model,
            output_type=FacilitationResponse,
        )
        self.register_system_prompt()
        self.register_tools()

    def build_system_prompt(self, ctx: RunContext[RoleAgentDeps]) -> str:
        """Build the system prompt with runtime context values.

        Args:
            ctx: Run context with role agent dependencies.

        Returns:
            Formatted system prompt string including shared constraints.
        """
        return self.build_prompt().format(
            discussion_context=ctx.deps.discussion_context,
            discussion_state=ctx.deps.classification.state.value,
            classification_reasoning=ctx.deps.classification.reasoning,
            intervention_reasoning=ctx.deps.intervention.reasoning,
            selection_reasoning=ctx.deps.role_selection.reasoning,
        )

    async def run(
        self,
        thread: DiscussionThread,
        deps: RoleAgentDeps,
    ) -> FacilitationResponse:
        """Generate a facilitation response for the given thread.

        Args:
            thread: The discussion thread.
            deps: Role agent dependencies.

        Returns:
            FacilitationResponse with text, technique, and confidence.
        """
        prompt = format_thread(thread)
        result = await self.agent.run(prompt, deps=deps)
        return result.output

    def register_tools(self) -> None:
        """Register pydantic-ai tools on the agent.

        Registers retrieve_techniques and get_thread_history.
        Subclasses may override to add role-specific tools,
        calling super().register_tools() first.
        """
        @self.agent.tool_plain
        def retrieve_techniques(state: str = "") -> str:
            """Retrieve the full technique repertoire.

            Call this before selecting a technique. All techniques
            are available - use your persona and constraints to
            select the one that fits the current situation.

            Args:
                state: Optional discussion state for filtering.

            Returns:
                Formatted string of all techniques from the
                ADR 0002 repertoire.
            """
            ds = None
            if state:
                try:
                    ds = DiscussionState(state)
                except ValueError:
                    pass
            techniques = get_techniques(ds)
            if not techniques:
                return "No techniques found for this role."
            lines = []
            for t in techniques:
                examples_text = "\n  ".join(f"Example: {e}" for e in t.examples)
                lines.append(
                    f"- **{t.name}**: {t.description}\n  {examples_text}"
                )
            return "\n".join(lines)

        @self.agent.tool
        def get_thread_history(ctx: RunContext[RoleAgentDeps]) -> str:
            """Retrieve prior facilitation interventions for this thread.

            Call this before selecting a technique to avoid repeating
            interventions that produced no progress.

            Args:
                ctx: Run context providing access to the history store
                    and thread identifier.

            Returns:
                Formatted string of prior interventions oldest-first,
                or a message indicating no history is available.
            """
            if ctx.deps.history_store is None:
                return "No intervention history available."
            records: list[InterventionRecord] = (
                ctx.deps.history_store.get_history(ctx.deps.thread.id)
            )
            if not records:
                return "No prior interventions recorded for this thread."
            lines = [
                f"- [{r.timestamp.isoformat()}] "
                f"role={r.role.value} technique={r.technique}: "
                f"{r.response_text[:120]}"
                for r in records
            ]
            return "\n".join(lines)


class OrganizationalAgent(RoleAgent):
    """Facilitates discussion structure: launches, summarizes, redirects."""

    ROLE = FacilitationRole.ORGANIZATIONAL  # type: ignore[assignment]
    DESCRIPTION = (
        "Structures the discussion: launches topics, "
        "summarizes, redirects off-topic threads, "
        "manages phases, closes discussions."
    )
    PERSONALITY = """\
The Architect is structured and methodical. You view the discussion
as having an arc - from opening through exploration to convergence
and closure - and your job is to track where it stands in that arc.
You believe that high-level thinking emerges from well-designed
structure, but that structuring too early interrupts productive
exploration.\
"""
    CONSTRAINTS = (
        SHARED_ROLE_CONSTRAINTS
        + "\n\nDo not use synthesis, phase transition, or closure"
        " techniques while the discussion is still in active"
        " exploration. Wait for natural convergence signals (repeated"
        " agreement, slowing contribution rate, or explicit"
        " conclusions)."
    )


class IntellectualAgent(RoleAgent):
    """Deepens thinking through Socratic dialogue and scaffolding."""

    ROLE = FacilitationRole.INTELLECTUAL  # type: ignore[assignment]
    DESCRIPTION = (
        "Deepens thinking: asks Socratic questions, "
        "challenges with counterarguments, solicits "
        "evidence, revoices contributions, structures "
        "arguments."
    )
    PERSONALITY = """\
The Sage-Facilitator is academically rigorous and inquisitive. You
act as a More Knowledgeable Other who uses epistemic agency to
bridge the gap between a student's current understanding and their
potential. You believe productive struggle has value: confusion is
the entry point to deeper understanding, not a problem to resolve
immediately.\
"""
    CONSTRAINTS = (
        SHARED_ROLE_CONSTRAINTS
        + "\n\nApply the EMT ladder strictly: pump (L1) → hint (L2)"
        " → prompt (L3) → assertion (L4). Start at L1 and escalate"
        " only when lower levels have been tried without progress."
        " The upstream intervention decision already confirmed that"
        " impasse is genuine."
    )


class SocialAgent(RoleAgent):
    """Builds community, encourages participation, and balances engagement."""

    ROLE = FacilitationRole.SOCIAL  # type: ignore[assignment]
    DESCRIPTION = (
        "Builds community: encourages participation, "
        "redistributes attention, acknowledges "
        "contributions, models constructive interaction."
    )
    PERSONALITY = """\
The Connector is warm, inclusive, and community-minded. You focus on
participation balance and social dynamics - tracking who is
contributing, who has gone quiet, and what the relational texture of
the thread feels like. You believe a trusting environment is a
prerequisite for the intellectual risk-taking that deep academic
discourse requires.\
"""
    CONSTRAINTS = (
        SHARED_ROLE_CONSTRAINTS
        + "\n\nRe-engaging a participant who was active and went"
        " silent is more urgent than activating a first-time"
        " contributor. You may act before the state is classified as"
        " conflictive if trajectory shows deterioration: increasing"
        " tension, shorter replies, or dismissive tone."
    )


class AffectiveAgent(RoleAgent):
    """Maintains psychological safety through emotional support."""

    ROLE = FacilitationRole.AFFECTIVE  # type: ignore[assignment]
    DESCRIPTION = (
        "Provides emotional support: validates feelings, "
        "acknowledges effort, uses positive framing, "
        "maintains psychological safety."
    )
    PERSONALITY = """\
The Lifeguard is empathic and vigilant. You monitor where productive
struggle tips into demotivation or panic. You believe psychological
safety is not separate from learning - it is its precondition. You
act when students need to feel seen before they can think clearly.\
"""
    CONSTRAINTS = (
        SHARED_ROLE_CONSTRAINTS
        + "\n\nDo not repeat affective support that was recently"
        " given - consecutive emotional interventions feel"
        " patronizing. Affective support must stay on-task: validate"
        " effort and normalize difficulty in relation to the specific"
        " learning challenge, not in general."
    )


class ModeratorAgent(RoleAgent):
    """Handles escalated situations: conflicts, inappropriate content."""

    ROLE = FacilitationRole.MODERATOR  # type: ignore[assignment]
    DESCRIPTION = (
        "Handles moderation: flags inappropriate content, "
        "addresses escalating conflicts, manages "
        "copyright concerns."
    )
    PERSONALITY = """\
The Balancer is strategically patient and protective. You handle
situations that go beyond normal academic disagreement: inappropriate
content, escalating personal conflict, copyright concerns. You are
the last resort - other roles handle everything else. You know that
the right moment to act is not always the earliest one.\
"""
    CONSTRAINTS = (
        SHARED_ROLE_CONSTRAINTS
        + "\n\nYou are the last resort. Activate only when other"
        " roles cannot address the situation. When the situation"
        " requires instructor attention rather than automated"
        " intervention, say so explicitly in the response. Use"
        " flag_content to report posts requiring human review."
    )

    def register_tools(self) -> None:
        """Register tools, adding flag_content on top of the base tools."""
        super().register_tools()

        @self.agent.tool
        async def flag_content(
            ctx: RunContext[RoleAgentDeps],
            post_id: str,
            reason: str,
        ) -> str:
            """Flag a post for instructor review via the LMS backend.

            Use this when content requires human review rather than
            (or in addition to) an automated facilitation response.

            Args:
                ctx: Run context providing access to the LMS backend.
                post_id: The platform-specific ID of the post to flag.
                reason: Human-readable explanation of why this post
                    is being flagged.

            Returns:
                Confirmation message, or an error if no backend is
                configured.
            """
            if ctx.deps.lms_backend is None:
                return "No LMS backend configured; cannot flag content."
            await ctx.deps.lms_backend.flag_content(post_id, reason)
            return f"Post {post_id} flagged for review: {reason}"


ROLE_AGENT_CLASSES: list[type[RoleAgent]] = [
    OrganizationalAgent,
    IntellectualAgent,
    SocialAgent,
    AffectiveAgent,
    ModeratorAgent,
]

ROLE_AGENTS: dict[FacilitationRole, RoleAgent] = {
    cls.ROLE: cls() for cls in ROLE_AGENT_CLASSES
}
