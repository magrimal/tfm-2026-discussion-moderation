"""Affective role agent.

Provides emotional support and maintains psychological safety:
validates effort, positive framing, emotional support
(ADR 0002, sections 3.1-3.2, 4.4).
"""

from discussion_moderation.agents.roles.base import (
    create_role_agent,
)
from discussion_moderation.common.constants import (
    FacilitationRole,
)

agent = create_role_agent(FacilitationRole.AFFECTIVE)
