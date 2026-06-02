# -*- coding: utf-8 -*-
"""Orchestrator core module for infra_orchestrator and thought_architecture."""

from enum import Enum


class DecisionStatus(Enum):
    """Decision status enum."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    IN_PROGRESS = "in_progress"


class Orchestrator:
    """Base orchestrator class for managing decisions and workflows."""

    def __init__(self, name: str = "BaseOrchestrator"):
        """Initialize the orchestrator with a name."""
        self.name = name
        self.decisions = {}

    def make_decision(self, decision_id: str, status: DecisionStatus) -> None:
        """Record a decision with a given status."""
        self.decisions[decision_id] = status

    def get_decision_status(self, decision_id: str) -> DecisionStatus | None:
        """Return the status of a specific decision."""
        return self.decisions.get(decision_id)

    def clear_decisions(self) -> None:
        """Clear all recorded decisions."""
        self.decisions.clear()
