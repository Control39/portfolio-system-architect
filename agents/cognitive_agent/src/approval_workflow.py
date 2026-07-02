#!/usr/bin/env python3
"""
Approval Workflow module for cognitive agent

Human-in-the-loop подтверждение критических действий.

Ключевые принципы:
- Low/Medium риск: автоподтверждение (если safe_mode != LOCKDOWN)
- High/Critical риск: требуют явного подтверждения
- Интеграция с TransparencyLogger для прозрачности
- Сохранение в .agent_data/approvals/ для аудита
"""

import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional

import structlog
import yaml

logger = structlog.get_logger(__name__)


class ApprovalWorkflow:
    """
    Human-in-the-loop подтверждение критических действий

    Уровни риска:
    - low: Стандартные операции (сканирование, чтение)
    - medium: Изменения без последствий (документация, комментарии)
    - high: Важные изменения (конфиги, тесты)
    - critical: Критические изменения (основной код, продакшн)
    """

    RISK_LEVELS = {"low", "medium", "high", "critical"}
    AUTO_APPROVE_LEVELS = {"low", "medium"}
    DEFAULT_TIMEOUT = 300  # 5 минут по умолчанию

    def __init__(self, transparency_logger: Any = None, safe_mode_config: dict = None):
        """
        Инициализация ApprovalWorkflow.

        Args:
            transparency_logger: Экземпляр TransparencyLogger для логирования (опционально)
            safe_mode_config: Конфигурация safe_mode (опционально)
        """
        self.pending_approvals: dict[str, dict[str, Any]] = {}
        self.approvals_dir = Path(".agent_data/approvals")
        self.approvals_dir.mkdir(parents=True, exist_ok=True)
        self.transparency_logger = transparency_logger
        self.safe_mode_config = safe_mode_config or {}
        self._timeout = timedelta(seconds=self.DEFAULT_TIMEOUT)

        logger.info(
            "ApprovalWorkflow initialized",
            approvals_dir=str(self.approvals_dir),
            default_timeout_seconds=self.DEFAULT_TIMEOUT,
        )

    def request_approval(self, action: dict[str, Any]) -> dict[str, Any]:
        """
        Создать запрос на подтверждение действия.

        Args:
            action: Словарь с данными действия
                - action: Описание действия
                - risk_level: Уровень риска (low/medium/high/critical)
                - description: Описание (опционально)
                - path: Путь к файлу (опционально)
                - context: Контекст (опционально)

        Returns:
            Словарь с результатом:
                - status: auto_approved / pending
                - approval_id: ID подтверждения (если pending)
                - action: Данные действия
        """
        risk_level = action.get("risk_level", "medium")

        # Валидация уровня риска
        if risk_level not in self.RISK_LEVELS:
            logger.warning(
                "Invalid risk level, defaulting to medium",
                risk_level=risk_level,
            )
            risk_level = "medium"

        # Автоподтверждение для низких/средних рисков
        if risk_level in self.AUTO_APPROVE_LEVELS:
            # Проверить safe_mode LOCKDOWN
            mode = self.safe_mode_config.get("mode", "")
            if mode == "LOCKDOWN":
                # В LOCKDOWN режиме даже низкий риск требует подтверждения
                return self._create_approval_request(action, risk_level)

            # Автоподтверждение
            logger.info(
                "Auto-approved action",
                action=action.get("action", "Unknown"),
                risk_level=risk_level,
            )

            if self.transparency_logger:
                self.transparency_logger.log_action(
                    {
                        "planned": action.get("description", action.get("action", "Unknown")),
                        "executed": "Auto-approved",
                        "status": "success",
                        "confidence": 1.0,
                        "user_approval": False,
                    }
                )

            return {"status": "auto_approved", "action": action}

        # Высокий/Критический риск требует подтверждения
        return self._create_approval_request(action, risk_level)

    def _create_approval_request(self, action: dict[str, Any], risk_level: str) -> dict[str, Any]:
        """
        Создать запрос на подтверждение (для high/critical риска).

        Args:
            action: Данные действия
            risk_level: Уровень риска

        Returns:
            Словарь с ID подтверждения
        """
        approval_id = str(uuid.uuid4())
        approval = {
            "id": approval_id,
            "action": action,
            "risk_level": risk_level,
            "timestamp": datetime.now().isoformat(),
            "expires_at": (datetime.now() + self._timeout).isoformat(),
            "status": "pending",
            "approved_by": None,
            "approved_at": None,
        }

        self.pending_approvals[approval_id] = approval
        self._save_approval(approval)

        # Логирование через TransparencyLogger
        if self.transparency_logger:
            self.transparency_logger.log_action(
                {
                    "planned": action.get("description", action.get("action", "Unknown")),
                    "executed": f"Awaiting human approval (ID: {approval_id})",
                    "status": "pending",
                    "confidence": 0.9,
                    "user_approval": False,
                }
            )

        logger.info(
            "Approval request created",
            approval_id=approval_id,
            risk_level=risk_level,
            action=action.get("action", "Unknown"),
        )

        return {"status": "pending", "approval_id": approval_id, "action": action}

    def approve(self, approval_id: str) -> bool:
        """
        Подтвердить действие.

        Args:
            approval_id: ID подтверждения

        Returns:
            True если подтверждено успешно, False если не найдено
        """
        if approval_id not in self.pending_approvals:
            logger.warning("Approval not found", approval_id=approval_id)
            return False

        approval = self.pending_approvals[approval_id]
        approval["status"] = "approved"
        approval["approved_by"] = "human"
        approval["approved_at"] = datetime.now().isoformat()

        self._save_approval(approval)
        del self.pending_approvals[approval_id]

        logger.info(
            "Approval granted",
            approval_id=approval_id,
            risk_level=approval["risk_level"],
        )

        return True

    def deny(self, approval_id: str) -> bool:
        """
        Отклонить действие.

        Args:
            approval_id: ID подтверждения

        Returns:
            True если отклонено успешно, False если не найдено
        """
        if approval_id not in self.pending_approvals:
            logger.warning("Approval not found", approval_id=approval_id)
            return False

        approval = self.pending_approvals[approval_id]
        approval["status"] = "denied"
        approval["approved_by"] = "human"
        approval["approved_at"] = datetime.now().isoformat()

        self._save_approval(approval)
        del self.pending_approvals[approval_id]

        logger.info(
            "Approval denied",
            approval_id=approval_id,
            risk_level=approval["risk_level"],
        )

        return True

    def check_pending(self) -> list[dict[str, Any]]:
        """
        Получить список ожидающих подтверждений.

        Returns:
            Список ожидающих подтверждений
        """
        return list(self.pending_approvals.values())

    def is_expired(self, approval_id: str) -> bool:
        """
        Проверить таймаут подтверждения.

        Args:
            approval_id: ID подтверждения

        Returns:
            True если истёк таймаут, False если ещё актуально
        """
        if approval_id not in self.pending_approvals:
            return True

        approval = self.pending_approvals[approval_id]
        expires_at = datetime.fromisoformat(approval["expires_at"])
        is_expired = datetime.now() > expires_at

        if is_expired:
            logger.warning(
                "Approval expired",
                approval_id=approval_id,
                expires_at=approval["expires_at"],
            )
            # Удалить истёкший approval
            del self.pending_approvals[approval_id]
            approval["status"] = "expired"
            self._save_approval(approval)

        return is_expired

    def _save_approval(self, approval: dict[str, Any]) -> None:
        """
        Сохранить подтверждение в файл.

        Args:
            approval: Данные подтверждения
        """
        file_path = self.approvals_dir / f"approval_{approval['id']}.json"

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(approval, f, indent=2, ensure_ascii=False)

        logger.debug(
            "Approval saved",
            approval_id=approval["id"],
            file_path=str(file_path),
        )

    def get_approval(self, approval_id: str) -> Optional[dict[str, Any]]:
        """
        Получить информацию о подтверждении по ID.

        Args:
            approval_id: ID подтверждения

        Returns:
            Данные подтверждения или None если не найдено
        """
        return self.pending_approvals.get(approval_id)

    def clear_pending(self) -> int:
        """
        Очистить все ожидающие подтверждения (например, при перезапуске).

        Returns:
            Количество очищенных подтверждений
        """
        count = len(self.pending_approvals)
        self.pending_approvals.clear()
        logger.info("Cleared pending approvals", count=count)
        return count

    def get_stats(self) -> dict[str, Any]:
        """
        Получить статистику подтверждений.

        Returns:
            Словарь со статистикой
        """
        total = len(self.pending_approvals)
        high_risk = sum(1 for a in self.pending_approvals.values() if a["risk_level"] == "high")
        critical_risk = sum(1 for a in self.pending_approvals.values() if a["risk_level"] == "critical")

        return {
            "total_pending": total,
            "high_risk_pending": high_risk,
            "critical_risk_pending": critical_risk,
            "approvals_dir": str(self.approvals_dir),
        }
