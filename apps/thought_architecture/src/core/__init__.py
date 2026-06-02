"""Core module for thought_architecture."""
from enum import Enum

class DecisionStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    IN_PROGRESS = "in_progress"
    IMPLEMENTED = "implemented"
    CANCELLED = "cancelled"

__all__ = ["DecisionStatus"]
