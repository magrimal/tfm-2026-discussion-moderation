"""Pydantic-ai tools for dynamic context enrichment."""

from discussion_moderation.tools.history import InMemoryThreadStore, SQLiteThreadStore
from discussion_moderation.tools.openedx import OpenEdXBackend
from discussion_moderation.tools.stub import StubLMSBackend

LMS_BACKENDS: dict[str, type] = {
    "openedx": OpenEdXBackend,
    "stub": StubLMSBackend,
}

HISTORY_BACKENDS: dict[str, type] = {
    "memory": InMemoryThreadStore,
    "sqlite": SQLiteThreadStore,
}
