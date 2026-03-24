"""Intellectual role agent.

Deepens thinking and promotes knowledge construction: Socratic
questions, tutorial dialogue ladder, counterarguments, evidence
solicitation, revoicing, IBIS structuring (ADR 0002, section 2).
"""

from discussion_moderation.agents.roles.base import (
    create_role_agent,
)
from discussion_moderation.common.constants import (
    FacilitationRole,
)

agent = create_role_agent(FacilitationRole.INTELLECTUAL)
