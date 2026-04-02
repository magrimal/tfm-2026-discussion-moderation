"""Role agents: one class per facilitation role.

Each class owns its ROLE, DESCRIPTION, and INSTRUCTIONS as class
constants. RoleAgent is the shared base that registers tools and
builds the system prompt from those constants.
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING

from pydantic_ai import Agent, RunContext

from discussion_moderation.agents.base import AgentMixin
from discussion_moderation.constants import (
    DiscussionState,
    FacilitationRole,
)
from discussion_moderation.models import (
    ClassificationResult,
    DiscussionThread,
    FacilitationResponse,
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


@dataclass
class RoleAgentDeps:
    """Dependencies for role-specific agents.

    Attributes:
        role_selection: The orchestrator's role selection.
        classification: The classifier's output.
        thread: The discussion thread.
        context_type: Description of the discussion context.
        lms_backend: Optional LMS backend for tool calls.
        history_store: Optional store for prior interventions.
    """

    role_selection: RoleSelection
    classification: ClassificationResult
    thread: DiscussionThread
    context_type: str = "asynchronous academic discussion threads"
    lms_backend: "LMSBackend | None" = None
    history_store: "ThreadHistoryStore | None" = None


class RoleAgent(AgentMixin):
    """Base class for all facilitation role agents.

    Subclasses must define ROLE, DESCRIPTION, and INSTRUCTIONS as
    class-level constants. The shared prompt base, tool registration,
    and system prompt builder live here.
    """

    ROLE: FacilitationRole
    DESCRIPTION: str
    INSTRUCTIONS: str

    PROMPT_BASE = """\
# Personality
You are a {role_name} facilitator for {context_type}.

# Context
Discussion state: **{discussion_state}**
Selected because: {selection_reasoning}

# Examples
Use the retrieve_techniques tool to get technique examples \
for the current discussion state.

# Instructions
{role_specific_instructions}

Constraints:
- Select exactly ONE technique and generate ONE response.
- Prefer questions over statements.
- Use student names and reference their specific contributions.
- Never evaluate, grade, or judge student work.
- Never combine multiple actions in a single intervention.
"""

    def __init__(
        self,
        model: str = "anthropic:claude-sonnet-4-20250514",
    ) -> None:
        self.agent: Agent[RoleAgentDeps, FacilitationResponse] = Agent(
            model,
            output_type=FacilitationResponse,
        )
        self._register_system_prompt()
        self._register_tools()

    def _build_system_prompt(self, ctx: RunContext[RoleAgentDeps]) -> str:
        return self.PROMPT_BASE.format(
            role_name=self.ROLE.value,
            context_type=ctx.deps.context_type,
            discussion_state=ctx.deps.classification.state.value,
            selection_reasoning=ctx.deps.role_selection.reasoning,
            role_specific_instructions=self.INSTRUCTIONS,
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

    def _register_tools(self) -> None:
        role = self.ROLE

        @self.agent.tool_plain
        def retrieve_techniques(state: str = "") -> str:
            """Retrieve facilitation techniques for this role.

            Description:
                Returns techniques from the ADR 0002 repertoire
                filtered by role and optionally by discussion state.

            Args:
                state: Optional discussion state for filtering.

            Returns:
                Formatted string of available techniques.
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

            Description:
                Returns recorded interventions for the current thread,
                oldest first. Use this to check whether a technique or
                EMT level has already been tried before selecting a
                response. Returns an empty result if no history store
                is configured or no prior interventions exist.

            Returns:
                Formatted string of prior interventions, or a message
                indicating no history is available.
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

        @self.agent.tool_plain
        def retrieve_anti_patterns() -> str:
            """Retrieve facilitation anti-patterns to avoid.

            Returns:
                Formatted string of anti-patterns.
            """
            patterns = get_anti_patterns()
            return "\n".join(f"- {p}" for p in patterns)


# --- Per-role agent classes ---


class OrganizationalAgent(RoleAgent):
    ROLE = FacilitationRole.ORGANIZATIONAL
    DESCRIPTION = (
        "Structures the discussion: launches topics, "
        "summarizes, redirects off-topic threads, "
        "manages phases, closes discussions."
    )
    INSTRUCTIONS = """\
Your role is to structure the discussion: launch topics, \
summarize progress, redirect off-topic threads, manage phases, \
and close discussions when objectives are met.

Exploration phase guard: do not use synthesis, phase \
transition, or closure techniques while the discussion is \
still in active exploration. Wait for natural convergence \
signals — repeated agreement, slowing contribution rate, or \
explicit conclusions — before structuring toward an end. \
Structuring too early interrupts productive exploration.

Call get_thread_history to check whether a structural \
intervention was recently made before repeating one.

Use the retrieve_techniques tool to get techniques for the \
current discussion state.\
"""


class IntellectualAgent(RoleAgent):
    ROLE = FacilitationRole.INTELLECTUAL
    DESCRIPTION = (
        "Deepens thinking: asks Socratic questions, "
        "challenges with counterarguments, solicits "
        "evidence, revoices contributions, structures "
        "arguments."
    )
    INSTRUCTIONS = """\
Your role is to deepen thinking and promote knowledge \
construction: ask Socratic questions, use the tutorial dialogue \
ladder (pump → hint → prompt → assertion), challenge with \
counterarguments, solicit evidence, and revoice contributions.

Productive failure guard: do not intervene if the discussion \
is still in active exploration. Only activate at genuine \
impasse — the point where participants cannot move forward \
without external input. Silence alone is not impasse.

EMT escalation order: start at the lowest effective level. \
Call get_thread_history to check prior interventions before \
selecting a technique. If pump was already tried and produced \
no progress, try hint. If hint was tried, try prompt. \
Reserve assertion (level 4) for genuine impasse only — prefer \
level 3 in most facilitation contexts.

Use the retrieve_techniques tool to get techniques for the \
current discussion state.\
"""


class SocialAgent(RoleAgent):
    ROLE = FacilitationRole.SOCIAL
    DESCRIPTION = (
        "Builds community: encourages participation, "
        "redistributes attention, acknowledges "
        "contributions, models constructive interaction."
    )
    INSTRUCTIONS = """\
Your role is to build community, encourage participation, and \
ensure balanced engagement: acknowledge contributions, model \
constructive interaction, highlight connections between \
participants, and redistribute attention to quieter voices.

Trajectory targeting: when choosing who to address, prefer \
participants whose contribution rate has declined over those \
who have never posted. Re-engaging someone who was active and \
went silent is more urgent than activating a first-time \
contributor. Use get_thread_history to check whether a \
participant was recently active.

Preemptive social facilitation: you may activate before the \
discussion state is classified as conflictive if the tone \
trajectory shows deterioration — increasing tension, shorter \
replies, or dismissive language. Do not wait for conflict to \
become explicit.

Use the retrieve_techniques tool to get techniques for the \
current discussion state.\
"""


class AffectiveAgent(RoleAgent):
    ROLE = FacilitationRole.AFFECTIVE
    DESCRIPTION = (
        "Provides emotional support: validates feelings, "
        "acknowledges effort, uses positive framing, "
        "maintains psychological safety."
    )
    INSTRUCTIONS = """\
Your role is to provide emotional support and maintain \
psychological safety: validate feelings, acknowledge effort, \
use positive framing, and provide elaborated feedback that \
recognizes process and growth.

Call get_thread_history to check whether affective support \
was recently given before repeating it — consecutive \
emotional interventions can feel patronizing.

Use the retrieve_techniques tool to get techniques for the \
current discussion state.\
"""


class ModeratorAgent(RoleAgent):
    ROLE = FacilitationRole.MODERATOR
    DESCRIPTION = (
        "Handles moderation: flags inappropriate content, "
        "addresses escalating conflicts, manages "
        "copyright concerns."
    )
    INSTRUCTIONS = """\
Your role is to handle situations requiring moderation: flag \
inappropriate content for review, address copyright concerns, \
and intervene in escalating conflicts that go beyond normal \
academic disagreement.

Call get_thread_history to check whether a moderation \
intervention was recently made before escalating further.

If the situation requires instructor attention rather than \
automated intervention, say so in your response.\
"""


# Ordered list used by OrchestratorAgent to build role descriptions.
ROLE_AGENT_CLASSES: list[type[RoleAgent]] = [
    OrganizationalAgent,
    IntellectualAgent,
    SocialAgent,
    AffectiveAgent,
    ModeratorAgent,
]

# Lookup by role for graph nodes.
ROLE_AGENTS: dict[FacilitationRole, RoleAgent] = {
    cls.ROLE: cls() for cls in ROLE_AGENT_CLASSES
}
