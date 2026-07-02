#!/usr/bin/env python3
"""
Proposal System module for cognitive agent

Система предложений (агент предлагает, разработчик применяет).

Ключевые принципы:
- Агент создаёт proposal с описанием изменений
- Разработчик просматривает и применяет вручную
- Никаких автоматических изменений без одобрения
- Интеграция с TransparencyLogger для прозрачности
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import structlog

logger = structlog.get_logger(__name__)


class ProposalSystem:
    """
    Система предложений (агент предлагает, разработчик применяет)

    Статусы предложений:
    - pending: Новое предложение, ожидает рассмотрения
    - approved: Предложение одобрено (готово к применению)
    - rejected: Предложение отклонено
    - applied: Предложение успешно применено

    Использование:
        system = ProposalSystem(transparency_logger=logger)
        proposal_id = system.create_proposal(
            title="Update config",
            description="Change timeout from 30 to 60",
            changes={"file": "config.yaml", "timeout": 60}
        )
        # Разработчик просматривает и применяет
        system.apply_proposal(proposal_id)
    """

    STATUSES = {"pending", "approved", "rejected", "applied"}
    DEFAULT_TIMEOUT = 300  # 5 минут

    def __init__(self, transparency_logger: Any = None):
        """
        Инициализация ProposalSystem.

        Args:
            transparency_logger: Экземпляр TransparencyLogger для логирования (опционально)
        """
        self.proposals: dict[str, dict[str, Any]] = {}
        self.proposals_dir = Path(".agent_data/proposals")
        self.proposals_dir.mkdir(parents=True, exist_ok=True)
        self.transparency_logger = transparency_logger

        logger.info(
            "ProposalSystem initialized",
            proposals_dir=str(self.proposals_dir),
        )

    def create_proposal(
        self,
        title: str,
        description: str,
        changes: dict[str, Any],
        risk_level: str = "medium",
    ) -> str:
        """
        Создать новое предложение.

        Args:
            title: Заголовок предложения
            description: Описание изменений
            changes: Словарь с изменениями
                - file: Путь к файлу
                - action: Действие (create/modify/delete)
                - changes: Конкретные изменения
            risk_level: Уровень риска (low/medium/high/critical)

        Returns:
            ID созданного предложения
        """
        proposal_id = str(uuid.uuid4())
        proposal = {
            "id": proposal_id,
            "title": title,
            "description": description,
            "changes": changes,
            "risk_level": risk_level,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "applied_at": None,
            "applied_by": None,
            "rejected_at": None,
            "rejected_by": None,
        }

        self.proposals[proposal_id] = proposal
        self._save_proposal(proposal)

        # Логирование через TransparencyLogger
        if self.transparency_logger:
            self.transparency_logger.log_action(
                {
                    "planned": title,
                    "executed": f"Proposal {proposal_id} created",
                    "status": "pending",
                    "confidence": 0.9,
                    "user_approval": False,
                }
            )

        logger.info(
            "Proposal created",
            proposal_id=proposal_id,
            title=title,
            risk_level=risk_level,
        )

        return proposal_id

    def get_proposal(self, proposal_id: str) -> Optional[dict[str, Any]]:
        """
        Получить предложение по ID.

        Args:
            proposal_id: ID предложения

        Returns:
            Данные предложения или None если не найдено
        """
        return self.proposals.get(proposal_id)

    def list_proposals(self, status: str = "pending") -> list[dict[str, Any]]:
        """
        Список предложений с фильтрацией по статусу.

        Args:
            status: Статус для фильтрации (pending/approved/rejected/applied/all)

        Returns:
            Список предложений
        """
        if status == "all":
            return list(self.proposals.values())

        return [proposal for proposal in self.proposals.values() if proposal["status"] == status]

    def apply_proposal(self, proposal_id: str) -> bool:
        """
        Применить предложение (заглушка, меняет только статус).

        КРИТИЧЕСКОЕ ПРАВИЛО: Этот метод НЕ применяет изменения автоматически.
        Он только меняет статус на 'applied' для аудита.

        Args:
            proposal_id: ID предложения

        Returns:
            True если применено успешно, False если не найдено
        """
        if proposal_id not in self.proposals:
            logger.warning("Proposal not found", proposal_id=proposal_id)
            return False

        proposal = self.proposals[proposal_id]
        proposal["status"] = "applied"
        proposal["applied_at"] = datetime.now().isoformat()
        proposal["applied_by"] = "human"

        self._save_proposal(proposal)

        logger.info(
            "Proposal applied",
            proposal_id=proposal_id,
            title=proposal["title"],
        )

        return True

    def reject_proposal(self, proposal_id: str) -> bool:
        """
        Отклонить предложение.

        Args:
            proposal_id: ID предложения

        Returns:
            True если отклонено успешно, False если не найдено
        """
        if proposal_id not in self.proposals:
            logger.warning("Proposal not found", proposal_id=proposal_id)
            return False

        proposal = self.proposals[proposal_id]
        proposal["status"] = "rejected"
        proposal["rejected_at"] = datetime.now().isoformat()
        proposal["rejected_by"] = "human"

        self._save_proposal(proposal)

        logger.info(
            "Proposal rejected",
            proposal_id=proposal_id,
            title=proposal["title"],
        )

        return True

    def _save_proposal(self, proposal: dict[str, Any]) -> None:
        """
        Сохранить предложение в файл.

        Args:
            proposal: Данные предложения
        """
        file_path = self.proposals_dir / f"proposal_{proposal['id']}.json"

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(proposal, f, indent=2, ensure_ascii=False)

        logger.debug(
            "Proposal saved",
            proposal_id=proposal["id"],
            file_path=str(file_path),
        )

    def get_proposal_file(self, proposal_id: str) -> Optional[Path]:
        """
        Получить путь к файлу предложения.

        Args:
            proposal_id: ID предложения

        Returns:
            Path к файлу или None если не найдено
        """
        proposal = self.get_proposal(proposal_id)
        if not proposal:
            return None

        return self.proposals_dir / f"proposal_{proposal_id}.json"

    def update_proposal_status(self, proposal_id: str, status: str) -> bool:
        """
        Обновить статус предложения.

        Args:
            proposal_id: ID предложения
            status: Новый статус

        Returns:
            True если успешно, False если не найдено
        """
        if proposal_id not in self.proposals:
            return False

        if status not in self.STATUSES:
            logger.warning(
                "Invalid status",
                status=status,
                valid_statuses=list(self.STATUSES),
            )
            return False

        proposal = self.proposals[proposal_id]
        proposal["status"] = status
        self._save_proposal(proposal)

        return True

    def get_pending_count(self) -> int:
        """
        Получить количество ожидающих предложений.

        Returns:
            Количество pending предложений
        """
        return len(self.list_proposals(status="pending"))

    def get_stats(self) -> dict[str, Any]:
        """
        Получить статистику предложений.

        Returns:
            Словарь со статистикой
        """
        total = len(self.proposals)
        pending = len(self.list_proposals(status="pending"))
        approved = len(self.list_proposals(status="approved"))
        rejected = len(self.list_proposals(status="rejected"))
        applied = len(self.list_proposals(status="applied"))

        return {
            "total": total,
            "pending": pending,
            "approved": approved,
            "rejected": rejected,
            "applied": applied,
            "proposals_dir": str(self.proposals_dir),
        }
