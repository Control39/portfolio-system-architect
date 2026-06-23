"""Core models for thought_architecture."""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel


class DecisionStatus(StrEnum):
    """Decision status enumeration."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    APPROVED = "approved"
    REJECTED = "rejected"
    IMPLEMENTED = "implemented"
    CANCELLED = "cancelled"


class ThoughtStatus(StrEnum):
    """Thought status enumeration."""

    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class Decision(BaseModel):
    """Decision model."""

    id: str
    title: str
    description: str
    status: DecisionStatus
    created_at: datetime
    updated_at: datetime | None = None


class ThoughtRecord(BaseModel):
    """Thought record model."""

    id: str
    content: str
    status: ThoughtStatus
    created_at: datetime
    tags: list[str] = []


__all__ = ["DecisionStatus", "ThoughtStatus", "Decision", "ThoughtRecord"]
