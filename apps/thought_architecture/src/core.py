"""Thought Architecture Core — System for tracking and analyzing technical decisions."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class DecisionStatus(str, Enum):
    """Статус архитектурного решения."""

    PROPOSED = "proposed"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    SUPERSEDED = "superseded"


class DecisionLevel(str, Enum):
    """Уровень важности решения."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Decision:
    """Архитектурное решение."""

    id: str
    title: str
    description: str
    status: DecisionStatus = DecisionStatus.PROPOSED
    level: DecisionLevel = DecisionLevel.MEDIUM
    context: str = ""
    consequences: str = ""
    alternatives: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def approve(self) -> None:
        """Утвердить решение."""
        self.status = DecisionStatus.ACCEPTED
        self.updated_at = datetime.now()

    def reject(self, reason: str = "") -> None:
        """Отклонить решение."""
        self.status = DecisionStatus.REJECTED
        self.metadata["rejection_reason"] = reason
        self.updated_at = datetime.now()

    def supersede(self, replacement_id: str) -> None:
        """Заместить решение новым."""
        self.status = DecisionStatus.SUPERSEDED
        self.metadata["replacement_id"] = replacement_id
        self.updated_at = datetime.now()


@dataclass
class ArchitectureRecord:
    """Запись архитектурного решения."""

    decision: Decision
    evidence: list[str] = field(default_factory=list)
    reviews: list[dict[str, Any]] = field(default_factory=list)

    def add_evidence(self, url: str) -> None:
        """Добавить доказательство."""
        self.evidence.append(url)

    def add_review(self, reviewer: str, comments: str, approved: bool) -> None:
        """Добавить отзыв ревьюера."""
        self.reviews.append(
            {
                "reviewer": reviewer,
                "comments": comments,
                "approved": approved,
                "timestamp": datetime.now().isoformat(),
            }
        )


class ThoughtArchitect:
    """Основной класс для управления архитектурными решениями."""

    def __init__(self, project_name: str = "Project"):
        self.project_name = project_name
        self.decisions: dict[str, Decision] = {}
        self.records: dict[str, ArchitectureRecord] = {}
        self._counter = 0

    def create_decision(
        self,
        title: str,
        description: str,
        level: DecisionLevel = DecisionLevel.MEDIUM,
        context: str = "",
        tags: list[str] | None = None,
    ) -> Decision:
        """Создать новое архитектурное решение."""
        self._counter += 1
        decision_id = f"{self.project_name.lower().replace(' ', '-')}-{self._counter:04d}"

        decision = Decision(
            id=decision_id,
            title=title,
            description=description,
            level=level,
            context=context,
            tags=tags or [],
        )

        self.decisions[decision_id] = decision
        self.records[decision_id] = ArchitectureRecord(decision=decision)

        return decision

    def get_decision(self, decision_id: str) -> Decision | None:
        """Получить решение по ID."""
        return self.decisions.get(decision_id)

    def list_decisions(
        self,
        status: DecisionStatus | None = None,
        level: DecisionLevel | None = None,
        tag: str | None = None,
    ) -> list[Decision]:
        """Список решений с фильтрами."""
        result = list(self.decisions.values())

        if status:
            result = [d for d in result if d.status == status]
        if level:
            result = [d for d in result if d.level == level]
        if tag:
            result = [d for d in result if tag in d.tags]

        return result

    def approve_decision(self, decision_id: str) -> bool:
        """Утвердить решение."""
        decision = self.get_decision(decision_id)
        if decision:
            decision.approve()
            return True
        return False

    def reject_decision(self, decision_id: str, reason: str = "") -> bool:
        """Отклонить решение."""
        decision = self.get_decision(decision_id)
        if decision:
            decision.reject(reason)
            return True
        return False

    def get_statistics(self) -> dict[str, Any]:
        """Получить статистику решений."""
        stats = {
            "total": len(self.decisions),
            "by_status": {},
            "by_level": {},
            "recent": [],
        }

        for decision in self.decisions.values():
            # Статусы
            status_key = decision.status.value
            stats["by_status"][status_key] = stats["by_status"].get(status_key, 0) + 1

            # Уровни
            level_key = decision.level.value
            stats["by_level"][level_key] = stats["by_level"].get(level_key, 0) + 1

        # Последние 5 решений
        sorted_decisions = sorted(
            self.decisions.values(),
            key=lambda d: d.created_at,
            reverse=True,
        )
        stats["recent"] = [d.id for d in sorted_decisions[:5]]

        return stats

    def find_by_tag(self, tag: str) -> list[Decision]:
        """Найти решения по тегу."""
        return [d for d in self.decisions.values() if tag in d.tags]

    def get_pending_decisions(self) -> list[Decision]:
        """Получить ожидающие решения."""
        return [d for d in self.decisions.values() if d.status == DecisionStatus.PROPOSED]
