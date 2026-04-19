"""Enumerations shared across agents, tools, and evaluations.

These constants define the vocabulary of the facilitation system.
Changes here affect all agents and should be reflected in ADRs.
"""

from enum import StrEnum


class DiscussionState(StrEnum):
    """Classification of a discussion thread's current state.

    Description:
        Phase 1 output categories from the three-phase
        intervention model (ADR 0003, Fase 1). Each state maps
        to different intervention strategies.

    # TODO: Can a thread be both stalled and off_topic? The current
    # taxonomy forces a single label. If both conditions apply
    # simultaneously, the chosen label determines which intervention
    # fires - this may suppress the other signal. Consider whether
    # state should be a set or whether priority rules are needed.

    # TODO: conflictive currently catches overt aggression. Rovai (2007)
    # also identifies subtler silencing dynamics - competitive or
    # dismissive tone that doesn't cross into hostility. Consider
    # extending the definition or adding a separate state for this.
    """

    NEW = "new"
    ACTIVE = "active"
    STALLED = "stalled"
    CONFLICTIVE = "conflictive"
    CONVERGENT = "convergent"
    OFF_TOPIC = "off_topic"


class DiscussionTrajectory(StrEnum):
    """Temporal engagement pattern of a discussion thread.

    Grounded in Chang & D-N-M (2019) and VanLehn (2011) via
    intervention-model.md: declining engagement requires different
    treatment than a thread that never started.
    """

    GROWING = "growing"
    STABLE = "stable"
    DECLINING = "declining"
    NEVER_STARTED = "never_started"


class ParticipationBalance(StrEnum):
    """Participation structure across contributors.

    Grounded in Rovai (2007): student-to-student exchange and
    distributed participation are markers of healthy discussion.
    Dominated or instructor-centered patterns signal a need for
    social facilitation.
    """

    DISTRIBUTED = "distributed"
    DOMINATED = "dominated"
    INSTRUCTOR_CENTERED = "instructor_centered"


class DiscourseQuality(StrEnum):
    """Quality of discourse in the thread.

    Grounded in Ho & Swan (2007): posting Quality (substantive,
    evidence-backed, builds on prior contributions) is the strongest
    predictor of whether a post generates a direct response.
    """

    SUBSTANTIVE = "substantive"
    MIXED = "mixed"
    FORMULAIC = "formulaic"


class InquiryPhase(StrEnum):
    """Phase of practical inquiry reached by the thread.

    Grounded in Garrison, Anderson & Archer (2001) Community of
    Inquiry framework. The phase informs which facilitation role
    is appropriate: organizational at triggering, intellectual at
    exploration/integration, organizational at resolution.
    """

    TRIGGERING = "triggering"
    EXPLORATION = "exploration"
    INTEGRATION = "integration"
    RESOLUTION = "resolution"


class FacilitationRole(StrEnum):
    """Facilitation roles that can be activated by the orchestrator.

    Description:
        Five roles grounded in converging literature on online
        discussion facilitation (ADR 0004). The orchestrator
        selects one role per intervention; the role agent then
        selects the specific technique and generates the response.

        The three core roles (organizational, intellectual, social)
        originate from Paulsen (1995) and converge across Berge
        (1995), Coppola (2002), Pilkington (2003), and Abdous
        (2011). Affective and moderator are transversal categories
        from ADR 0003.
    """

    ORGANIZATIONAL = "organizational"
    INTELLECTUAL = "intellectual"
    SOCIAL = "social"
    AFFECTIVE = "affective"
    MODERATOR = "moderator"


class ActionCategory(StrEnum):
    """Phase 2 action categories from the intervention model.

    Description:
        Categories for the specific actions a role agent can
        select (ADR 0003, Fase 2). Each role maps to one primary
        category but may draw from adjacent categories when
        appropriate.
    """

    ORGANIZATIONAL = "organizational"
    INTELLECTUAL = "intellectual"
    SOCIAL = "social"
    AFFECTIVE = "affective"
    MODERATION = "moderation"
