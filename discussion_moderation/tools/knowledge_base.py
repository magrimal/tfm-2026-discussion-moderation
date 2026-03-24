"""Knowledge base tool for retrieving facilitation techniques.

Provides on-demand access to the technique repertoire (ADR 0002)
without embedding the full repertoire in agent prompts. Agents
call these functions as pydantic-ai tools to retrieve only the
techniques relevant to their role and the current discussion state.
"""

from dataclasses import dataclass

from discussion_moderation.common.constants import (
    DiscussionState,
    FacilitationRole,
)


@dataclass
class Technique:
    """A facilitation technique from the repertoire.

    Attributes:
        name: Short identifier for the technique.
        description: What the technique does and when to use it.
        example: An example application of the technique.
    """

    name: str
    description: str
    example: str


# Technique repertoire indexed by role, sourced from ADR 0002.
# Each role has a curated set of techniques with state-specific
# applicability notes.

_ORGANIZATIONAL_TECHNIQUES = [
    Technique(
        name="launch_discussion",
        description=(
            "Open a new discussion with a content-based, open "
            "question that elicits critical thinking (ADR 0002, "
            "section 1.1)."
        ),
        example=(
            '"What are the ethical implications of X? Consider '
            'both individual and societal perspectives."'
        ),
    ),
    Technique(
        name="summarize_progress",
        description=(
            "Summarize key arguments, areas of agreement and "
            "disagreement, and open questions (ADR 0002, "
            "section 1.6)."
        ),
        example=(
            '"So far, three perspectives have emerged: ... '
            'The main unresolved question is ..."'
        ),
    ),
    Technique(
        name="redirect_off_topic",
        description=(
            "Reformulate the original question when responses "
            "drift from the topic. Acknowledge the tangent "
            "before redirecting (ADR 0002, section 1.8)."
        ),
        example=(
            '"Interesting point about Y — that could be its '
            "own discussion! For this thread, let's return to "
            'the original question: ..."'
        ),
    ),
    Technique(
        name="close_discussion",
        description=(
            "Close a discussion that has reached its learning "
            "objectives. Summarize outcomes and name remaining "
            "open questions (ADR 0002, section 1.6)."
        ),
        example=(
            '"Great discussion! The key takeaways are: ... '
            'A question worth exploring further: ..."'
        ),
    ),
    Technique(
        name="phase_structuring",
        description=(
            "Signal a transition between discussion phases "
            "(e.g., from exploration to synthesis). Set "
            "expectations for the next phase (ADR 0002, "
            "section 1.4)."
        ),
        example=(
            "\"We've shared diverse perspectives. Let's now "
            "focus on finding common ground: which points do "
            'most of you agree on?"'
        ),
    ),
]

_INTELLECTUAL_TECHNIQUES = [
    Technique(
        name="socratic_clarification",
        description=(
            "Ask a clarification question when a statement is "
            "vague or ambiguous. Paul's taxonomy, level 1 "
            "(ADR 0002, section 2.1)."
        ),
        example=(
            '"@Student, when you say "it depends on context", '
            'what specific contexts are you thinking of?"'
        ),
    ),
    Technique(
        name="probe_assumptions",
        description=(
            "Surface unexamined premises in a student's "
            "argument. Paul's taxonomy, level 2 "
            "(ADR 0002, section 2.1)."
        ),
        example=('"What are you assuming about X when you say ...?"'),
    ),
    Technique(
        name="solicit_evidence",
        description=(
            "Ask for evidence or concrete examples to support "
            "a claim (ADR 0002, section 2.4)."
        ),
        example=(
            "\"That's an interesting claim. Can you point to "
            'a specific reading or example that supports it?"'
        ),
    ),
    Technique(
        name="challenge_counterargument",
        description=(
            "Introduce an alternative perspective or "
            "counterexample to deepen analysis. Use selectively "
            "— can reduce psychological safety if overused "
            "(ADR 0002, section 2.3)."
        ),
        example=(
            '"How would someone who disagrees with this '
            "position respond? What's the strongest "
            'counterargument?"'
        ),
    ),
    Technique(
        name="revoice",
        description=(
            "Paraphrase a student's contribution to clarify "
            "and elevate it, then connect it to another "
            "participant's point (ADR 0002, section 2.5)."
        ),
        example=(
            "\"@Student, it sounds like you're saying X. "
            "That connects to @OtherStudent's point about Y "
            '— do you see the same connection?"'
        ),
    ),
    Technique(
        name="tutorial_pump",
        description=(
            "Open elicitation: ask the student to elaborate "
            "without directing them. EMT level 1 "
            "(ADR 0002, section 2.2)."
        ),
        example='"Can you say more about that?"',
    ),
    Technique(
        name="tutorial_hint",
        description=(
            "Indirect hint: point toward relevant material "
            "without giving the answer. EMT level 2 "
            "(ADR 0002, section 2.2)."
        ),
        example=('"Think about what we discussed regarding X..."'),
    ),
]

_SOCIAL_TECHNIQUES = [
    Technique(
        name="encourage_participation",
        description=(
            "Invite quieter participants by name, reference "
            "their expertise or background (ADR 0002, "
            "section 3.1)."
        ),
        example=(
            '"@Student, you mentioned experience with X in '
            "your introduction — what's your take on this?\""
        ),
    ),
    Technique(
        name="acknowledge_contribution",
        description=(
            "Recognize a specific contribution's value to the "
            "discussion (ADR 0002, section 3.1)."
        ),
        example=(
            '"@Student, thank you for bringing up the '
            "distinction between X and Y — that's a key "
            'nuance."'
        ),
    ),
    Technique(
        name="redistribute_attention",
        description=(
            "When one participant dominates, redirect focus to "
            "other voices (ADR 0002, section 3.3)."
        ),
        example=(
            "\"@Student has raised important points. I'd love "
            "to hear what others think — @Student2, @Student3, "
            "what's your perspective?\""
        ),
    ),
    Technique(
        name="highlight_connections",
        description=(
            "Point out connections between different "
            "participants' contributions to build community "
            "(ADR 0002, section 3.5)."
        ),
        example=(
            "\"@Student and @Student2, you're both touching on "
            "the idea of X from different angles — there might "
            'be common ground here."'
        ),
    ),
]

_AFFECTIVE_TECHNIQUES = [
    Technique(
        name="validate_effort",
        description=(
            "Acknowledge the effort and process, not just the "
            "outcome (ADR 0002, section 3.1)."
        ),
        example=(
            "\"@Student, I can see you've thought carefully "
            "about this — your analysis of X shows real "
            'depth."'
        ),
    ),
    Technique(
        name="positive_framing",
        description=(
            "Reframe a negative or frustrated contribution in "
            "constructive terms (ADR 0002, section 4.4)."
        ),
        example=(
            "\"It sounds like you're frustrated with X — "
            "that's actually a sign you're engaging deeply. "
            'What specifically is bothering you about it?"'
        ),
    ),
    Technique(
        name="emotional_support",
        description=(
            "Provide direct emotional support when a "
            "participant expresses difficulty or discouragement "
            "(ADR 0002, section 3.2)."
        ),
        example=(
            "\"This is a challenging topic and it's normal to "
            "feel uncertain. Your willingness to engage with "
            'it is valuable."'
        ),
    ),
]

_MODERATOR_TECHNIQUES = [
    Technique(
        name="flag_for_review",
        description=(
            "Flag content that may be inappropriate or violate "
            "community guidelines for instructor review."
        ),
        example=('"This post has been flagged for instructor review."'),
    ),
    Technique(
        name="de_escalate",
        description=(
            "Intervene in escalating conflict by acknowledging "
            "the disagreement and redirecting to constructive "
            "engagement."
        ),
        example=(
            '"I can see there are strong feelings here. '
            "Let's take a step back and focus on the "
            'arguments rather than each other."'
        ),
    ),
]

_TECHNIQUES_BY_ROLE: dict[FacilitationRole, list[Technique]] = {
    FacilitationRole.ORGANIZATIONAL: _ORGANIZATIONAL_TECHNIQUES,
    FacilitationRole.INTELLECTUAL: _INTELLECTUAL_TECHNIQUES,
    FacilitationRole.SOCIAL: _SOCIAL_TECHNIQUES,
    FacilitationRole.AFFECTIVE: _AFFECTIVE_TECHNIQUES,
    FacilitationRole.MODERATOR: _MODERATOR_TECHNIQUES,
}

# State-to-role relevance: which roles are most relevant for each
# discussion state. Used to filter technique suggestions.
_STATE_ROLE_RELEVANCE: dict[DiscussionState, list[FacilitationRole]] = {
    DiscussionState.NEW: [
        FacilitationRole.ORGANIZATIONAL,
        FacilitationRole.SOCIAL,
    ],
    DiscussionState.ACTIVE: [
        FacilitationRole.INTELLECTUAL,
        FacilitationRole.SOCIAL,
    ],
    DiscussionState.STALLED: [
        FacilitationRole.SOCIAL,
        FacilitationRole.INTELLECTUAL,
        FacilitationRole.ORGANIZATIONAL,
    ],
    DiscussionState.CONFLICTIVE: [
        FacilitationRole.MODERATOR,
        FacilitationRole.SOCIAL,
        FacilitationRole.AFFECTIVE,
    ],
    DiscussionState.CONVERGENT: [
        FacilitationRole.ORGANIZATIONAL,
        FacilitationRole.INTELLECTUAL,
    ],
    DiscussionState.OFF_TOPIC: [
        FacilitationRole.ORGANIZATIONAL,
    ],
}

ANTI_PATTERNS = [
    "Intervening in a healthy, active discussion unnecessarily.",
    "Combining multiple actions in a single intervention.",
    "Using evaluative or grading language.",
    "Overusing the contrarian persona — reduces psychological "
    "safety (Yan, 2025).",
    "Providing answers instead of scaffolding toward them.",
    "Ignoring student contributions in the response.",
    "Using generic encouragement without referencing specific contributions.",
]


def get_techniques(
    role: FacilitationRole,
    state: DiscussionState | None = None,
) -> list[Technique]:
    """Retrieve techniques for a role, optionally filtered by state.

    Description:
        Returns the technique repertoire for the given role. When
        a discussion state is provided, prioritizes techniques
        from roles most relevant to that state.

    Args:
        role: The facilitation role to retrieve techniques for.
        state: Optional discussion state for relevance filtering.

    Returns:
        List of Technique objects for the role.
    """
    return list(_TECHNIQUES_BY_ROLE.get(role, []))


def get_anti_patterns() -> list[str]:
    """Retrieve the list of facilitation anti-patterns.

    Description:
        Returns patterns to avoid during facilitation, grounded
        in the literature review (ADR 0002).

    Returns:
        List of anti-pattern descriptions.
    """
    return list(ANTI_PATTERNS)
