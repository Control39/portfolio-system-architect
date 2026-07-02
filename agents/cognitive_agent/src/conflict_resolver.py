#!/usr/bin/env python3
"""
Conflict Resolver module for cognitive agent

Протокол разрешения конфликтов между агентом и разработчиком.

КРИТИЧЕСКОЕ ПРАВИЛО: ConflictResolver НИКОГДА не применяет изменения автоматически.
Он только:
- Обнаруживает конфликты
- Создаёт proposals
- Логирует через TransparencyLogger
- Ждёт ручного разрешения от разработчика
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import structlog

logger = structlog.get_logger(__name__)


class ConflictResolver:
    """
    Протокол разрешения конфликтов между агентом и разработчиком

    Ключевые принципы:
    - Human-in-the-loop: разработчик всегда имеет приоритет
    - NO automatic recovery: агент никогда не восстанавливает файлы без одобрения
    - Transparency: все конфликты логируются через TransparencyLogger
    - Audit trail: каждый конфликт сохраняется в файл proposals/
    """

    def __init__(self, transparency_logger: Any = None):
        """
        Инициализация ConflictResolver.

        Args:
            transparency_logger: Экземпляр TransparencyLogger для логирования (опционально)
        """
        self.conflicts: list[dict[str, Any]] = []
        self.proposals_dir = Path(".agent_data/proposals")
        self.proposals_dir.mkdir(parents=True, exist_ok=True)
        self.transparency_logger = transparency_logger
        self._resolutions: dict[str, dict[str, Any]] = {}

        logger.info(
            "ConflictResolver initialized",
            proposals_dir=str(self.proposals_dir),
        )

    def detect_conflict(
        self,
        config_path: str,
        human_change: dict[str, Any],
        agent_preference: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Обнаружить конфликт между действиями разработчика и агента.

        КРИТИЧЕСКОЕ ПРАВИЛО: Этот метод НИКОГДА не восстанавливает старые значения.
        Он только:
        - Обнаруживает конфликт
        - Создаёт proposal
        - Логирует через TransparencyLogger
        - Возвращает информацию о конфликте

        Args:
            config_path: Путь к конфигурационному файлу
            human_change: Что сделал разработчик
            agent_preference: Что хотел сделать агент

        Returns:
            Словарь с информацией о конфликте
        """
        conflict = {
            "id": str(uuid.uuid4()),
            "config": config_path,
            "human_change": human_change,
            "agent_preference": agent_preference,
            "timestamp": datetime.now().isoformat(),
            "status": "pending",
            "human_wins_by_default": True,
        }

        # Создать proposal вместо автоматического восстановления
        proposal_id = self._create_proposal(conflict)
        conflict["proposal_id"] = proposal_id

        # Добавить в список конфликтов
        self.conflicts.append(conflict)
        self._resolutions[conflict["id"]] = {
            "status": "pending",
            "resolution": None,
            "resolved_at": None,
        }

        # Логирование через TransparencyLogger
        if self.transparency_logger:
            self.transparency_logger.log_action(
                {
                    "planned": f"Apply agent preference: {agent_preference}",
                    "executed": f"Created proposal {proposal_id} (human wins by default)",
                    "status": "blocked",
                    "confidence": 1.0,
                    "user_approval": False,
                }
            )

        logger.info(
            "Conflict detected",
            conflict_id=conflict["id"],
            config=config_path,
            proposal_id=proposal_id,
            human_change=human_change,
            agent_preference=agent_preference,
        )

        return conflict

    def _create_proposal(self, conflict: dict[str, Any]) -> str:
        """
        Создать файл предложения для конфликта.

        Args:
            conflict: Словарь с информацией о конфликте

        Returns:
            ID конфликта (proposal_id)
        """
        proposal_file = self.proposals_dir / f"proposal_{conflict['id']}.json"

        proposal_data = {
            "conflict_id": conflict["id"],
            "config": conflict["config"],
            "human_change": conflict["human_change"],
            "agent_preference": conflict["agent_preference"],
            "timestamp": conflict["timestamp"],
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "instructions": (
                "Решите конфликт:\n"
                "  - 'human_wins': Применить изменения разработчика\n"
                "  - 'agent_wins': Применить предпочтения агента\n"
                "  - 'compromise': Найти компромиссное решение"
            ),
        }

        # Сохранить proposal в файл
        with open(proposal_file, "w", encoding="utf-8") as f:
            json.dump(proposal_data, f, indent=2, ensure_ascii=False)

        logger.info(
            "Proposal created",
            proposal_id=conflict["id"],
            proposal_file=str(proposal_file),
        )

        return conflict["id"]

    def resolve_conflict(self, conflict_id: str, decision: str) -> dict[str, Any]:
        """
        Ручное разрешение конфликта.

        Args:
            conflict_id: ID конфликта (proposal_id)
            decision: Решение ("human_wins" / "agent_wins" / "compromise")

        Returns:
            Обновлённая информация о конфликте

        Raises:
            ValueError: Если конфликт не найден или решение невалидно
        """
        # Найти конфликт
        conflict = None
        for c in self.conflicts:
            if c["id"] == conflict_id:
                conflict = c
                break

        if not conflict:
            raise ValueError(f"Conflict not found: {conflict_id}")

        # Валидация решения
        valid_decisions = ["human_wins", "agent_wins", "compromise"]
        if decision not in valid_decisions:
            raise ValueError(f"Invalid decision: {decision}. " f"Must be one of: {valid_decisions}")

        # Обновить статус
        conflict["status"] = "resolved"
        conflict["resolved_decision"] = decision
        conflict["resolved_at"] = datetime.now().isoformat()

        # Обновить локальный словарь
        if conflict_id in self._resolutions:
            self._resolutions[conflict_id] = {
                "status": "resolved",
                "resolution": decision,
                "resolved_at": conflict["resolved_at"],
            }

        # Обновить файл proposal
        proposal_file = self.proposals_dir / f"proposal_{conflict_id}.json"
        if proposal_file.exists():
            proposal_data = {
                "conflict_id": conflict_id,
                "config": conflict["config"],
                "human_change": conflict["human_change"],
                "agent_preference": conflict["agent_preference"],
                "timestamp": conflict["timestamp"],
                "status": "resolved",
                "decision": decision,
                "resolved_at": conflict["resolved_at"],
                "created_at": conflict.get("created_at"),
            }
            with open(proposal_file, "w", encoding="utf-8") as f:
                json.dump(proposal_data, f, indent=2, ensure_ascii=False)

        # Логирование через TransparencyLogger
        if self.transparency_logger:
            self.transparency_logger.log_action(
                {
                    "planned": f"Resolve conflict {conflict_id}",
                    "executed": f"Conflict resolved with decision: {decision}",
                    "status": "success",
                    "confidence": 1.0,
                    "user_approval": True,
                }
            )

        logger.info(
            "Conflict resolved",
            conflict_id=conflict_id,
            decision=decision,
        )

        return conflict

    def get_conflict(self, conflict_id: str) -> Optional[dict[str, Any]]:
        """
        Получить информацию о конфликте по ID.

        Args:
            conflict_id: ID конфликта

        Returns:
            Словарь с информацией о конфликте или None если не найден
        """
        for conflict in self.conflicts:
            if conflict["id"] == conflict_id:
                return conflict
        return None

    def get_all_conflicts(self) -> list[dict[str, Any]]:
        """
        Получить все конфликты.

        Returns:
            Список всех конфликтов
        """
        return self.conflicts.copy()

    def get_pending_conflicts(self) -> list[dict[str, Any]]:
        """
        Получить все неразрешённые конфликты.

        Returns:
            Список неразрешённых конфликтов
        """
        return [c for c in self.conflicts if c["status"] == "pending"]

    def get_proposals_dir(self) -> Path:
        """
        Получить путь к директории proposal-файлов.

        Returns:
            Path к директории proposals
        """
        return self.proposals_dir

    def clear_history(self) -> None:
        """Очистить историю конфликтов."""
        self.conflicts = []
        self._resolutions = {}
        logger.info("Conflict history cleared")
