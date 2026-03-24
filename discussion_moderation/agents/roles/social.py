"""Social role agent.

Builds community and encourages balanced participation:
acknowledges contributions, models interaction, highlights
connections, redistributes attention (ADR 0002, section 3).
"""

from discussion_moderation.agents.roles.base import (
    create_role_agent,
)
from discussion_moderation.common.constants import (
    FacilitationRole,
)

agent = create_role_agent(FacilitationRole.SOCIAL)
