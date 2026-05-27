"""Core models for thought_architecture."""
from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel

class DecisionStatus(str, Enum):
    """Decision status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    APPROVED = "approved"
    REJECTED = "rejected"
    IMPLEMENTED = "implemented"
    CANCELLED = "cancelled"

class ThoughtStatus(str, Enum):
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
    updated_at: Optional[datetime] = None

class ThoughtRecord(BaseModel):
    """Thought record model."""
    id: str
    content: str
    status: ThoughtStatus
    created_at: datetime
    tags: List[str] = []

__all__ = ["DecisionStatus", "ThoughtStatus", "Decision", "ThoughtRecord"]
