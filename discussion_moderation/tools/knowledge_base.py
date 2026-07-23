"""Knowledge base tool for retrieving facilitation techniques.

Provides on-demand access to the technique repertoire (ADR 0046)
without embedding the full repertoire in agent prompts. Agents
call these functions as pydantic-ai tools to retrieve only the
techniques relevant to their role and the current discussion state.
"""

from dataclasses import dataclass

from discussion_moderation.constants import (
    DiscussionState,
    FacilitationRole,
)


@dataclass
class Technique:
    """A facilitation technique from the repertoire.

    Attributes:
        name: Short identifier for the technique.
        description: What the technique does and when to use it.
            This field is shown to the agent.
        examples: Example applications of the technique.
            These are shown to the agent.
        source: Literature or ADR reference backing this technique.
            NOT shown to the agent - used for traceability and
            review only.
    """

    name: str
    description: str
    examples: list[str]
    source: str = ""


# Technique repertoire indexed by role, sourced from ADR 0046.
# Each role has a curated set of techniques with state-specific
# applicability notes.

ORGANIZATIONAL_TECHNIQUES = [
    Technique(
        name="launch_discussion",
        description=(
            "Open a new discussion with a content-based, open "
            "question that elicits critical thinking."
        ),
        examples=[
            (
                '"What are the ethical implications of X? Consider '
                'both individual and societal perspectives."'
            ),
            (
                "\"Looking at this week's reading on X, what aspects "
                'do you find most controversial and why?"'
            ),
        ],
        source="Garrison et al. 2001 (triggering event); ADR 0046 §1.1",
    ),
    Technique(
        name="summarize_progress",
        description=(
            "Summarize key arguments, areas of agreement and "
            "disagreement, and open questions."
        ),
        examples=[
            (
                '"So far, three perspectives have emerged: ... '
                'The main unresolved question is ..."'
            ),
            (
                '"Two threads have emerged in our discussion: X and Y. '
                "Before we move on, is there a perspective we haven't "
                'yet considered?"'
            ),
        ],
        source="Singh & Mørch 2022 (epistemic summarizing); ADR 0046 §1.6",
    ),
    Technique(
        name="redirect_off_topic",
        description=(
            "Reformulate the original question when responses "
            "drift from the topic. Acknowledge the tangent "
            "before redirecting."
        ),
        examples=[
            (
                '"Interesting point about Y - that could be its '
                "own discussion! For this thread, let's return to "
                'the original question: ..."'
            ),
            (
                "\"That's an interesting connection - let's explore it "
                "in a new thread. For now, can we return to the "
                'original question: ..."'
            ),
        ],
        source="Ho & Swan 2007 (Grice's Relevance maxim); ADR 0046 §1.8",
    ),
    Technique(
        name="close_discussion",
        description=(
            "Close a discussion that has reached its learning "
            "objectives. Summarize outcomes and name remaining "
            "open questions."
        ),
        examples=[
            (
                '"Great discussion! The key takeaways are: ... '
                'A question worth exploring further: ..."'
            ),
            (
                "\"We've reached some solid conclusions. The key "
                "insights are: ... One question worth carrying "
                'forward: ..."'
            ),
        ],
        source="Garrison et al. 2001 (resolution phase); ADR 0046 §1.6",
    ),
    Technique(
        name="phase_structuring",
        description=(
            "Signal a transition between discussion phases "
            "(e.g., from exploration to synthesis). Set "
            "expectations for the next phase."
        ),
        examples=[
            (
                "\"We've shared diverse perspectives. Let's now "
                "focus on finding common ground: which points do "
                'most of you agree on?"'
            ),
            (
                "\"We've been exploring the problem space. Now let's "
                "shift to solutions - what approaches have you seen "
                'in the literature?"'
            ),
        ],
        source="Garrison et al. 2001 (PIM phases); ADR 0046 §1.4",
    ),
]

INTELLECTUAL_TECHNIQUES = [
    Technique(
        name="socratic_clarification",
        description=(
            "Ask a clarification question when a statement is "
            "vague or ambiguous. Paul's taxonomy, level 1."
        ),
        examples=[
            (
                '"@Student, when you say "it depends on context", '
                'what specific contexts are you thinking of?"'
            ),
            (
                "\"@Student, what do you mean by 'context' in this "
                "case - are you thinking of technical, social, or "
                'institutional context?"'
            ),
        ],
        source="Paul & Elder 2006 (critical thinking taxonomy, L1); ADR 0046 §2.1",
    ),
    Technique(
        name="probe_assumptions",
        description=(
            "Surface unexamined premises in a student's "
            "argument. Paul's taxonomy, level 2."
        ),
        examples=[
            '"What are you assuming about X when you say ...?"',
            '"What would have to be true for this claim to hold in all cases?"',
        ],
        source="Paul & Elder 2006 (critical thinking taxonomy, L2); ADR 0046 §2.1",
    ),
    Technique(
        name="solicit_evidence",
        description=(
            "Ask for evidence or concrete examples to support a claim."
        ),
        examples=[
            (
                "\"That's an interesting claim. Can you point to "
                'a specific reading or example that supports it?"'
            ),
            (
                '"@Student, can you walk us through the data or case '
                'study that led you to this conclusion?"'
            ),
        ],
        source="Ho & Swan 2007 (Grice's Quality maxim); ADR 0046 §2.4",
    ),
    Technique(
        name="challenge_counterargument",
        description=(
            "Introduce an alternative perspective or "
            "counterexample to deepen analysis. Use selectively "
            "- can reduce psychological safety if overused."
        ),
        examples=[
            (
                '"How would someone who disagrees with this '
                "position respond? What's the strongest "
                'counterargument?"'
            ),
            (
                '"@Student makes a compelling case for X. @Others, '
                "what's the strongest reason to doubt this "
                'position?"'
            ),
        ],
        source="Lippert et al. 2020 (scaffolded dialogue); ADR 0046 §2.3",
    ),
    Technique(
        name="revoice",
        description=(
            "Paraphrase a student's contribution to clarify "
            "and elevate it, then connect it to another "
            "participant's point."
        ),
        examples=[
            (
                "\"@Student, it sounds like you're saying X. "
                "That connects to @OtherStudent's point about Y "
                '- do you see the same connection?"'
            ),
            (
                '"If I understand correctly, @Student is arguing that '
                "X implies Y. @Student2, does that connect to your "
                'point about Z?"'
            ),
        ],
        source="Lippert et al. 2020 (revoicing in ITS); ADR 0046 §2.5",
    ),
    Technique(
        name="tutorial_pump",
        description=(
            "Open elicitation: ask the student to elaborate "
            "without directing them. EMT level 1."
        ),
        examples=[
            '"Can you say more about that?"',
            '"That\'s a starting point - can you take it further?"',
        ],
        source="Lippert et al. 2020 (EMT ladder, L1); VanLehn 2011; ADR 0046 §2.2",
    ),
    Technique(
        name="tutorial_hint",
        description=(
            "Indirect hint: point toward relevant material "
            "without giving the answer. EMT level 2."
        ),
        examples=[
            '"Think about what we discussed regarding X..."',
            (
                '"Consider how the concept from section 3 of the '
                'reading might apply here."'
            ),
        ],
        source="Lippert et al. 2020 (EMT ladder, L2); VanLehn 2011; ADR 0046 §2.2",
    ),
    Technique(
        name="tutorial_prompt",
        description=(
            "Directive cue: name the specific concept or "
            "framework without stating the answer. Use only "
            "after pump and hint have not produced progress "
            "(check thread history). EMT level 3."
        ),
        examples=[
            (
                '"The trade-off between X and Y from the reading '
                "is directly relevant here - how does that fit "
                'your argument?"'
            ),
            (
                '"The concept we discussed in section 3 applies '
                "here. Can you see which part of your argument "
                'it challenges?"'
            ),
        ],
        source="Lippert et al. 2020 (EMT ladder, L3); VanLehn 2011; ADR 0046 §2.2",
    ),
    Technique(
        name="tutorial_assertion",
        description=(
            "Direct statement: give the key concept or "
            "explanation. RESERVED - use only at genuine "
            "impasse after levels 1-3 have been tried and "
            "produced no progress. In most discussion contexts "
            "prefer level 3. EMT level 4."
        ),
        examples=[
            (
                '"The key issue here is X: [brief explanation]. '
                "Now, how does that change your thinking about "
                'Y?"'
            ),
            (
                '"Let me be direct: the concept at play is X, '
                "which means Z. With that in mind, what would "
                'you change in your argument?"'
            ),
        ],
        source="Lippert et al. 2020 (EMT ladder, L4); VanLehn 2011; ADR 0046 §2.2",
    ),
]

SOCIAL_TECHNIQUES = [
    Technique(
        name="encourage_participation",
        description=(
            "Invite quieter participants by name, reference "
            "their expertise or background."
        ),
        examples=[
            (
                '"@Student, you mentioned experience with X in '
                "your introduction - what's your take on this?\""
            ),
            (
                "\"@Student, we haven't heard from you yet on this "
                "- what's your take?\""
            ),
        ],
        source="Rovai 2007 (social presence, participation balance); ADR 0046 §3.1",
    ),
    Technique(
        name="acknowledge_contribution",
        description=(
            "Recognize a specific contribution's value to the discussion."
        ),
        examples=[
            (
                '"@Student, thank you for bringing up the '
                "distinction between X and Y - that's a key "
                'nuance."'
            ),
            (
                '"The distinction @Student drew between X and Y has '
                "shifted how I'm thinking about this - it's worth "
                'building on."'
            ),
        ],
        source="Rovai 2007 (social presence); ADR 0046 §3.1",
    ),
    Technique(
        name="redistribute_attention",
        description=(
            "When one participant dominates, redirect focus to other voices."
        ),
        examples=[
            (
                "\"@Student has raised important points. I'd love "
                "to hear what others think - @Student2, @Student3, "
                "what's your perspective?\""
            ),
            (
                "\"We've heard a lot from a few voices. @Student3, "
                "@Student4 - what aspect of this resonates or "
                'concerns you?"'
            ),
        ],
        source="Rovai 2007 (participation balance); ADR 0046 §3.3",
    ),
    Technique(
        name="highlight_connections",
        description=(
            "Point out connections between different "
            "participants' contributions to build community."
        ),
        examples=[
            (
                "\"@Student and @Student2, you're both touching on "
                "the idea of X from different angles - there might "
                'be common ground here."'
            ),
            (
                "\"@Student's point about X and @Student2's point "
                "about Y are actually two sides of the same argument "
                '- does anyone see how they fit together?"'
            ),
        ],
        source="Rovai 2007 (community building); ADR 0046 §3.5",
    ),
    Technique(
        name="trajectory_engagement",
        description=(
            "Re-engage a participant whose contribution rate has "
            "declined after a period of activity. Reference their "
            "earlier contributions to signal their absence is "
            "noticed. Prioritize over participants who have never "
            "posted - re-engagement is more urgent than first "
            "activation."
        ),
        examples=[
            (
                '"@Student, you raised a great point earlier about '
                "X - we've moved on to Y since then. How do you "
                "think X connects to what we're discussing now?\""
            ),
            (
                '"@Student, you were very active in the early part '
                "of this discussion. We'd love to hear your take "
                "on where we've landed.\""
            ),
        ],
        source="Kim et al. 2021 (trajectory-based engagement); ADR 0046 §3.6",
    ),
]

AFFECTIVE_TECHNIQUES = [
    Technique(
        name="normalize_difficulty",
        description=(
            "Explicitly name that this level of difficulty is "
            "expected and normal for this topic and stage. "
            "Distinguish productive struggle from being lost."
        ),
        examples=[
            (
                "\"@Student, the tension you're feeling between X "
                "and Y is exactly what makes this topic difficult "
                "- and exactly what we're here to work through.\""
            ),
            (
                '"Most students find this point genuinely hard. '
                "The difficulty isn't a sign you're missing "
                "something - it's the material.\""
            ),
        ],
        source="Kapur 2016 (productive failure); Sikstrom et al. 2022; ADR 0046 §4.3",
    ),
    Technique(
        name="encourage_reengagement",
        description=(
            "Invite a student who has gone quiet back into the "
            "discussion, acknowledging their earlier contribution "
            "and making return feel low-stakes."
        ),
        examples=[
            (
                '"@Student, you made a strong point earlier about '
                "X - we'd love to hear how your thinking has "
                'developed since then."'
            ),
            (
                "\"@Student, there's no pressure - even a short "
                "reaction to what others have said would add "
                'value here."'
            ),
        ],
        source="Rovai 2007 (social presence, participation); Sikstrom et al. 2022; ADR 0046 §4.3",
    ),
    Technique(
        name="process_feedback",
        description=(
            "Provide specific feedback on the student's thinking "
            "process and approach, not just the content of their "
            "contribution. Name what is working well."
        ),
        examples=[
            (
                '"@Student, the way you connected X to Y before '
                "challenging it is exactly the kind of reasoning "
                'this topic calls for."'
            ),
            (
                "\"@Student, asking that question shows you're "
                "tracking the right tension in the argument - "
                'keep pulling on that thread."'
            ),
        ],
        source="Hattie & Timperley 2007 (feedback model); Sikstrom et al. 2022; ADR 0046 §4.5",
    ),
    Technique(
        name="validate_effort",
        description=(
            "Acknowledge the effort and process, not just the outcome."
        ),
        examples=[
            (
                "\"@Student, I can see you've thought carefully "
                "about this - your analysis of X shows real "
                'depth."'
            ),
            (
                "\"Working through this topic isn't easy, @Student "
                "- the nuance you're grappling with here is exactly "
                'what makes it hard."'
            ),
        ],
        source="Sikstrom et al. 2022 (affective support in pedagogical agents); ADR 0046 §4.1",
    ),
    Technique(
        name="positive_framing",
        description=(
            "Reframe a negative or frustrated contribution in "
            "constructive terms."
        ),
        examples=[
            (
                "\"It sounds like you're frustrated with X - "
                "that's actually a sign you're engaging deeply. "
                'What specifically is bothering you about it?"'
            ),
            (
                '"Confusion at this stage is a sign of real '
                "engagement with the material. What specifically "
                'feels unclear?"'
            ),
        ],
        source="Sikstrom et al. 2022 (positive framing, register); ADR 0046 §4.4",
    ),
    Technique(
        name="emotional_support",
        description=(
            "Provide direct emotional support when a "
            "participant expresses difficulty or discouragement."
        ),
        examples=[
            (
                "\"This is a challenging topic and it's normal to "
                "feel uncertain. Your willingness to engage with "
                'it is valuable."'
            ),
            (
                "\"It's okay not to have a firm position yet "
                "- exploring the tension between X and Y is the "
                'goal here."'
            ),
        ],
        source="Sikstrom et al. 2022 (affective presence); ADR 0046 §4.2",
    ),
]

MODERATOR_TECHNIQUES = [
    Technique(
        name="flag_for_review",
        description=(
            "Flag content that may be inappropriate or violate "
            "community guidelines for instructor review."
        ),
        examples=[
            '"This post has been flagged for instructor review."',
            (
                '"This content has been flagged. The instructor '
                'will review it shortly."'
            ),
        ],
        source="Ho & Swan 2007 (Grice's Quality maxim violation); ADR 0046 §5.1",
    ),
    Technique(
        name="de_escalate",
        description=(
            "Intervene in escalating conflict by acknowledging "
            "the disagreement and redirecting to constructive "
            "engagement."
        ),
        examples=[
            (
                '"I can see there are strong feelings here. '
                "Let's take a step back and focus on the "
                'arguments rather than each other."'
            ),
            (
                "\"The disagreement here is valuable, but let's make "
                "sure we're engaging with each other's ideas rather "
                "than each other's tone.\""
            ),
        ],
        source="Rovai 2007 (conflictive state management); ADR 0046 §5.2",
    ),
    Technique(
        name="boundary_statement",
        description=(
            "State the discussion norms clearly when a post "
            "approaches or crosses acceptable boundaries. "
            "Address the behavior, not the person."
        ),
        examples=[
            (
                '"In this discussion we engage with ideas, not '
                "with people. Let's keep responses focused on "
                'the argument.\\"'
            ),
            (
                '"Personal comments are outside the scope of '
                "this discussion. Let's return to the question "
                'at hand.\\"'
            ),
        ],
        source="Rovai 2007 (community norms); ADR 0046 §5.3",
    ),
    Technique(
        name="redirect_to_norms",
        description=(
            "Redirect a post that drifts from expected norms "
            "back to the discussion standards, citing the norm "
            "explicitly."
        ),
        examples=[
            (
                '"Our discussion norms ask us to support claims '
                "with evidence. Can you share what's behind "
                'this position?\\"'
            ),
            (
                "\"Let's make sure we're engaging constructively "
                "- responses should address the argument, "
                'not the person.\\"'
            ),
        ],
        source="Ho & Swan 2007 (Grice's Manner maxim); ADR 0046 §5.4",
    ),
    Technique(
        name="instructor_escalation",
        description=(
            "Escalate silently to the instructor when the "
            "situation requires human judgment and cannot be "
            "addressed by automated facilitation. "
            "Set post_to_thread = false. "
            "Write a concise situation summary for the "
            "instructor - not a student-facing message."
        ),
        examples=[
            (
                "[Instructor note] Thread X shows a pattern of "
                "dismissive replies targeting @Student. The "
                "last three interventions produced no change. "
                "Human review recommended."
            ),
            (
                "[Instructor note] @Student's post contains "
                "content that may require policy review. "
                "Flagged for instructor attention."
            ),
        ],
        source="Koedinger & Aleven 2007 (assistance dilemma); ADR 0046 §5.5",
    ),
]

# All techniques available to all role agents. Each role's persona
# and constraints guide which techniques are appropriate - role
# agents are not restricted to a per-role subset (ADR 0009).
TECHNIQUES: list[Technique] = (
    ORGANIZATIONAL_TECHNIQUES
    + INTELLECTUAL_TECHNIQUES
    + SOCIAL_TECHNIQUES
    + AFFECTIVE_TECHNIQUES
    + MODERATOR_TECHNIQUES
)

# State-to-role relevance: which roles are most relevant for each
# discussion state. Used to filter technique suggestions.
STATE_ROLE_RELEVANCE: dict[DiscussionState, list[FacilitationRole]] = {
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
    "Intervening in a healthy, active discussion unnecessarily "
    "(Kim et al., 2006: prefer non-intervention when discussion "
    "is self-sustaining).",
    "Combining multiple actions in a single intervention "
    "(ADR 0046: one technique per intervention).",
    "Using evaluative or grading language "
    "(thesis invariant: the system facilitates, it does not grade).",
    "Overusing the contrarian persona; reduces psychological safety "
    "(Yan, 2025).",
    "Providing answers instead of scaffolding toward them "
    "(ADR 0046, section 2: tutorial dialogue ladder).",
    "Ignoring student contributions in the response "
    "(ADR 0046, section 3.1: acknowledge contributions).",
    "Using generic encouragement without referencing specific contributions "
    "(ADR 0046, section 3.1: specificity is required for social presence).",
    # AP-1: Timing: intervene at impasse, not silence (ADR 0008, §1)
    "Intervening intellectually before the discussion reaches genuine impasse; "
    "premature intervention disrupts productive failure and interrupts the "
    "struggle that generates deep learning (VanLehn, 2011; Kapur, 2016).",
    # AP-2: Timing: respect cooldown between interventions (ADR 0008, §5)
    "Re-intervening without cooldown after a recent intervention; consecutive "
    "interventions shift the discussion from student-centered to "
    "facilitator-centered (Rovai, 2007).",
    # AP-3: Timing: trajectory over snapshot (ADR 0008, §2)
    "Deciding based on a snapshot of current state without considering "
    "trajectory; a declining thread requires different action than one "
    "that has never started (Chang & Danescu-Niculescu-Mizil, 2019).",
    # AP-4: Timing: abstain under ambiguity (ADR 0008, §3-4)
    "Choosing to intervene under ambiguity rather than abstaining; when "
    "intervention signal is weak, false positives are more harmful than "
    "false negatives (Koedinger & Aleven, 2007; Anthropic, 2025).",
]


def get_techniques(
    state: DiscussionState | None = None,
) -> list[Technique]:
    """Retrieve the full technique repertoire.

    All techniques are available to all role agents. Each role's
    persona and constraints guide appropriate selection without
    hard per-role filtering.

    Args:
        state: Reserved for future state-based filtering.
            Currently unused.

    Returns:
        Full list of Technique objects.
    """
    return list(TECHNIQUES)


def get_anti_patterns() -> list[str]:
    """Retrieve the list of facilitation anti-patterns.

    Description:
        Returns patterns to avoid during facilitation, grounded
        in the literature review (ADR 0046).

    Returns:
        List of anti-pattern descriptions.
    """
    return list(ANTI_PATTERNS)
