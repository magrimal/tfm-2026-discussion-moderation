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
    """

    NEW = "new"
    ACTIVE = "active"
    STALLED = "stalled"
    CONFLICTIVE = "conflictive"
    CONVERGENT = "convergent"
    OFF_TOPIC = "off_topic"


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
