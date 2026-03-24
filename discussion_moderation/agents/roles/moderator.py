"""Moderator role agent.

Handles moderation situations: flags inappropriate content,
addresses escalating conflicts, manages copyright concerns.
"""

from discussion_moderation.agents.roles.base import (
    create_role_agent,
)
from discussion_moderation.common.constants import (
    FacilitationRole,
)

agent = create_role_agent(FacilitationRole.MODERATOR)
