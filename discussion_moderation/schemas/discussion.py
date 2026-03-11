"""Domain models for discussion facilitation."""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel


class DiscussionState(StrEnum):
    """Phase 1 classification (ADR 0003)."""

    NEW = "new"
    ACTIVE = "active"
    STALLED = "stalled"
    CONFLICTIVE = "conflictive"
    CONVERGENT = "convergent"
    OFF_TOPIC = "off_topic"


class FacilitationRole(StrEnum):
    """Three facilitation roles (ADR 0004)."""

    ORGANIZATIONAL = "organizational"
    INTELLECTUAL = "intellectual"
    SOCIAL = "social"


class ActionCategory(StrEnum):
    """Phase 2 action categories (ADR 0003)."""

    ORGANIZATIONAL = "organizational"
    INTELLECTUAL = "intellectual"
    SOCIAL = "social"
    AFFECTIVE = "affective"
    MODERATION = "moderation"


class Post(BaseModel):
    """A single post in a discussion thread."""

    author: str
    content: str
    timestamp: datetime


class DiscussionThread(BaseModel):
    """Input: a discussion thread with context."""

    topic: str
    learning_objectives: list[str]
    posts: list[Post]


class ClassificationResult(BaseModel):
    """Phase 1 output: discussion state + intervention decision."""

    state: DiscussionState
    should_intervene: bool
    reasoning: str


class ActionSelection(BaseModel):
    """Phase 2 output: selected action."""

    category: ActionCategory
    action: str
    reasoning: str


class FacilitationResult(BaseModel):
    """Full pipeline output (Phases 1-3)."""

    classification: ClassificationResult
    action: ActionSelection | None
    response: str | None
