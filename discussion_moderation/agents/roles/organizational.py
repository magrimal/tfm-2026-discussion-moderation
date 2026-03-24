"""Organizational role agent.

Structures discussions: launches topics, summarizes progress,
redirects off-topic threads, manages phases, and closes
discussions when objectives are met (ADR 0002, section 1).
"""

from discussion_moderation.agents.roles.base import (
    create_role_agent,
)
from discussion_moderation.common.constants import (
    FacilitationRole,
)

agent = create_role_agent(FacilitationRole.ORGANIZATIONAL)
