"""Pydantic-ai tools for dynamic context enrichment.

Imports all backend implementations so their __init_subclass__ hooks
fire and register them into LMSBackend and ThreadHistoryStore registries.
"""

from discussion_moderation.tools.history import (
    InMemoryThreadStore,
    SQLiteThreadStore,
)
from discussion_moderation.tools.openedx import OpenEdXBackend
from discussion_moderation.tools.stub import StubLMSBackend

__all__ = [
    "InMemoryThreadStore",
    "OpenEdXBackend",
    "SQLiteThreadStore",
    "StubLMSBackend",
]
