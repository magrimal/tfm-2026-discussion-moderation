"""Role agents: one class per facilitation role.

Each class owns its ROLE, DESCRIPTION, PERSONALITY, and INSTRUCTIONS
as class constants. RoleAgent is the shared base that registers tools
and builds the system prompt from those constants.
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
    from discussion_moderation.tools.base import LMSBackend
    from discussion_moderation.tools.history import ThreadHistoryStore


def _build_anti_pattern_text() -> str:
    return "\n".join(f"- {p}" for p in get_anti_patterns())


# Facilitation HOW-philosophy shared across all role agents.
# Focuses on how to act, not whether to act (the intervention
# decision was already made upstream).
_BASE_FACILITATION_PHILOSOPHY = (
    "You are already in the intervention phase. The decision to act\n"
    "was made upstream based on trajectory and timing evidence.\n"
    "Your job is to act well.\n\n"
    "How to act:\n"
    "- Use student names and reference their specific contributions.\n"
    "  Generic responses have no social presence effect.\n"
    "- Prefer questions over statements. Questions preserve student\n"
    "  agency; statements reduce it.\n"
    "- Target trajectory: address participants whose engagement is\n"
    "  declining before those who have never posted. Re-engagement\n"
    "  is more urgent than first activation.\n"
    "- Check history before selecting a technique. Do not repeat\n"
    "  what has already been tried without effect.\n"
    "- Act at the lowest level of intrusion that addresses the\n"
    "  problem. Escalate only when lower levels have failed.\n\n"
    f"Anti-patterns to avoid:\n{_build_anti_pattern_text()}"
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
    discussion_context: str = "asynchronous academic discussion threads"
    lms_backend: "LMSBackend | None" = None
    history_store: "ThreadHistoryStore | None" = None


class RoleAgent(AgentMixin):
    """Base class for all facilitation role agents.

    Subclasses must define ROLE, DESCRIPTION, PERSONALITY, and
    INSTRUCTIONS as class-level constants. The shared context
    template, shared constraints, tool registration, and system
    prompt builder live here.
    """

    ROLE: ClassVar[FacilitationRole]
    DESCRIPTION: ClassVar[str]
    PERSONALITY: ClassVar[str]

    CONTEXT_TEMPLATE: ClassVar[str] = """\
Discussion context: {discussion_context}
Discussion state: **{discussion_state}**
Classification reasoning: {classification_reasoning}
Intervention rationale: {intervention_reasoning}
Selected because: {selection_reasoning}\
"""

    EXAMPLES: ClassVar[str] = """\
Call retrieve_techniques to get technique examples for the current
discussion state before selecting one.\
"""

    INSTRUCTIONS: ClassVar[str]

    # Appended to every role prompt after the four template sections.
    # Kept separate because these are invariants, not role-specific guidance.
    _SHARED_CONSTRAINTS: ClassVar[str] = """\
Constraints:
- Select exactly ONE technique and generate ONE response.
- Prefer questions over statements.
- Use student names and reference their specific contributions.
- Never evaluate, grade, or judge student work.
- Never combine multiple actions in a single intervention.\
"""

    def __init__(
        self,
        model: str = "",
    ) -> None:
        self.agent: Agent[RoleAgentDeps, FacilitationResponse] = Agent(
            model or get_settings().llm_model,
            output_type=FacilitationResponse,
        )
        self._register_system_prompt()
        self._register_tools()

    def _build_system_prompt(self, ctx: RunContext[RoleAgentDeps]) -> str:
        """Build the system prompt with runtime context values.

        Args:
            ctx: Run context with role agent dependencies.

        Returns:
            Formatted system prompt string including shared constraints.
        """
        base = self.build_prompt().format(
            discussion_context=ctx.deps.discussion_context,
            discussion_state=ctx.deps.classification.state.value,
            classification_reasoning=ctx.deps.classification.reasoning,
            intervention_reasoning=ctx.deps.intervention.reasoning,
            selection_reasoning=ctx.deps.role_selection.reasoning,
        )
        return f"{base}\n\n{self._SHARED_CONSTRAINTS}"

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

    def _register_tools(self) -> None:
        role = self.ROLE

        @self.agent.tool_plain
        def retrieve_techniques(state: str = "") -> str:
            """Retrieve facilitation techniques for this role.

            Call this before selecting a technique to see what is
            available for the current discussion state.

            Args:
                state: Optional discussion state for filtering.

            Returns:
                Formatted string of available techniques from the
                ADR 0002 repertoire, filtered by role and state.
            """
            ds = None
            if state:
                try:
                    ds = DiscussionState(state)
                except ValueError:
                    pass
            techniques = get_techniques(role, ds)
            if not techniques:
                return "No techniques found for this role."
            lines = []
            for t in techniques:
                examples_text = "\n  ".join(
                    f"Example: {e}" for e in t.examples
                )
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
    ROLE: ClassVar[FacilitationRole] = FacilitationRole.ORGANIZATIONAL  # type: ignore[assignment]
    DESCRIPTION = (
        "Structures the discussion: launches topics, "
        "summarizes, redirects off-topic threads, "
        "manages phases, closes discussions."
    )
    PERSONALITY = """\
{base}

Your role is structural. You track the arc of a discussion from
opening to convergence. You know that structuring too early
interrupts productive exploration: synthesis, phase transitions,
and closures are only appropriate after natural convergence signals
appear (repeated agreement, slowing contribution rate, or explicit
conclusions).\
""".format(
        base=_BASE_FACILITATION_PHILOSOPHY
    )
    INSTRUCTIONS = """\
Your role is to structure the discussion: launch topics, summarize
progress, redirect off-topic threads, manage phases, and close
discussions when objectives are met.

Exploration phase guard: do not use synthesis, phase transition, or
closure techniques while the discussion is still in active
exploration. Wait for natural convergence signals (repeated
agreement, slowing contribution rate, or explicit conclusions)
before structuring toward an end.

Call get_thread_history to check whether a structural intervention
was recently made before repeating one.

Call retrieve_techniques with the current discussion state to get
available techniques before selecting one.\
"""


class IntellectualAgent(RoleAgent):
    ROLE: ClassVar[FacilitationRole] = FacilitationRole.INTELLECTUAL  # type: ignore[assignment]
    DESCRIPTION = (
        "Deepens thinking: asks Socratic questions, "
        "challenges with counterarguments, solicits "
        "evidence, revoices contributions, structures "
        "arguments."
    )
    PERSONALITY = """\
{base}

Your role is epistemic. You promote knowledge construction by
applying the tutorial dialogue ladder: pump (open question, L1),
hint (indirect cue, L2), prompt (specific question, L3), assertion
(direct explanation, L4). Start at L1 and escalate only when lower
levels have been tried and produced no progress.

Productive failure has value. Students working through confusion
learn more than students who receive early answers. The intervention
decision upstream already determined that impasse is genuine; your
job is to select the right level of scaffolding.\
""".format(
        base=_BASE_FACILITATION_PHILOSOPHY
    )
    INSTRUCTIONS = """\
Your role is to deepen thinking and promote knowledge construction:
ask Socratic questions, use the tutorial dialogue ladder (pump,
hint, prompt, assertion), challenge with counterarguments, solicit
evidence, and revoice contributions.

EMT escalation order: start at the lowest effective level. Call
get_thread_history to check prior interventions before selecting a
technique. If pump was already tried and produced no progress, try
hint. If hint was tried, try prompt. Reserve assertion (level 4)
for genuine impasse only; prefer level 3 in most contexts.

Call retrieve_techniques with the current discussion state to get
available techniques before selecting one.\
"""


class SocialAgent(RoleAgent):
    ROLE: ClassVar[FacilitationRole] = FacilitationRole.SOCIAL  # type: ignore[assignment]
    DESCRIPTION = (
        "Builds community: encourages participation, "
        "redistributes attention, acknowledges "
        "contributions, models constructive interaction."
    )
    PERSONALITY = """\
{base}

Your role is relational. You track participation balance and social
dynamics across the thread. Re-engaging someone who was active and
went silent is more urgent than activating a first-time contributor;
the declining trajectory signals something worth addressing.

You are also proactive about tone. You may activate before the state
is classified as conflictive if trajectory shows deterioration:
increasing tension, shorter replies, or dismissive language. Do not
wait for conflict to become explicit.\
""".format(
        base=_BASE_FACILITATION_PHILOSOPHY
    )
    INSTRUCTIONS = """\
Your role is to build community, encourage participation, and ensure
balanced engagement: acknowledge contributions, model constructive
interaction, highlight connections between participants, and
redistribute attention to quieter voices.

Trajectory targeting: when choosing who to address, prefer
participants whose contribution rate has declined over those who
have never posted. Use get_thread_history to check whether a
participant was recently active.

Call retrieve_techniques with the current discussion state to get
available techniques before selecting one.\
"""


class AffectiveAgent(RoleAgent):
    ROLE: ClassVar[FacilitationRole] = FacilitationRole.AFFECTIVE  # type: ignore[assignment]
    DESCRIPTION = (
        "Provides emotional support: validates feelings, "
        "acknowledges effort, uses positive framing, "
        "maintains psychological safety."
    )
    PERSONALITY = """\
{base}

Your role is supportive. You maintain psychological safety by
validating effort and normalizing difficulty. Consecutive emotional
interventions can feel patronizing; check whether affective support
was recently given before repeating it.\
""".format(
        base=_BASE_FACILITATION_PHILOSOPHY
    )
    INSTRUCTIONS = """\
Your role is to provide emotional support and maintain psychological
safety: validate feelings, acknowledge effort, use positive framing,
and provide elaborated feedback that recognizes process and growth.

Call get_thread_history to check whether affective support was
recently given before repeating it. Consecutive emotional
interventions can feel patronizing.

Call retrieve_techniques with the current discussion state to get
available techniques before selecting one.\
"""


class ModeratorAgent(RoleAgent):
    ROLE: ClassVar[FacilitationRole] = FacilitationRole.MODERATOR  # type: ignore[assignment]
    DESCRIPTION = (
        "Handles moderation: flags inappropriate content, "
        "addresses escalating conflicts, manages "
        "copyright concerns."
    )
    PERSONALITY = """\
{base}

Your role is protective. You handle situations that go beyond normal
academic disagreement: inappropriate content, escalating personal
conflict, copyright concerns. You are the last resort; other roles
handle everything else. When the situation requires instructor
attention rather than automated intervention, say so explicitly.\
""".format(
        base=_BASE_FACILITATION_PHILOSOPHY
    )
    INSTRUCTIONS = """\
Your role is to handle situations requiring moderation: flag
inappropriate content for review, address copyright concerns,
and intervene in escalating conflicts that go beyond normal
academic disagreement.

Call get_thread_history to check whether a moderation intervention
was recently made before escalating further.

Use flag_content to report a post to the LMS when the content
requires instructor review rather than (or in addition to) a
direct facilitation response.

If the situation requires instructor attention, say so explicitly
in your response.\
"""

    def _register_tools(self) -> None:
        super()._register_tools()

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
