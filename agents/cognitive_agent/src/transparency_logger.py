"""Transparency logger module for cognitive agent."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import structlog

logger = structlog.get_logger(__name__)


class TransparencyLogger:
    """
    Логгер прозрачности для отслеживания различий между планируемыми и выполненными действиями.

    Интегрируется с audit_logger для создания полной картины действий агента.
    Позволяет пользователю видеть, что агент ПЛАНИРОВАЛ сделать vs ЧТО ФАКТИЧЕСКИ ВЫПОЛНИЛОСЬ.

    Ключевые возможности:
    - Отслеживание расхождений между планом и реальностью
    - Автоматическое обнаружение "обмана" (planned != executed)
    - Поддержка многоуровневой прозрачности (info/warning/error)
    """

    def __init__(
        self,
        agent_id: str = "transparency-agent",
        log_file: Optional[str] = None,
        audit_logger: Any = None,
        structured_logger=None,
    ):
        """
        Инициализация TransparencyLogger.

        Args:
            agent_id: Идентификатор агента
            log_file: Путь к файлу лога (опционально)
            audit_logger: Экземпляр AuditLogger для интеграции (опционально)
            structured_logger: Структурированный логгер (опционально)
        """
        self.agent_id = agent_id
        self.log_file = log_file or str(Path.home() / ".agent_data" / "logs" / "transparency_log.jsonl")
        self.audit_logger = audit_logger
        self.structured_logger = structured_logger or logger
        self._ensure_log_file()
        self._action_history: list[dict[str, Any]] = []
        self._transparency_level = "full"  # full, partial, minimal

    def _ensure_log_file(self):
        """Убедиться, что файл прозрачности существует."""
        Path(self.log_file).parent.mkdir(parents=True, exist_ok=True)
        if not Path(self.log_file).exists():
            Path(self.log_file).touch()

    def set_transparency_level(self, level: str):
        """
        Установить уровень прозрачности.

        Args:
            level: Уровень ("full", "partial", "minimal")
        """
        valid_levels = ["full", "partial", "minimal"]
        if level not in valid_levels:
            raise ValueError(f"Invalid transparency level: {level}. " f"Must be one of: {valid_levels}")

        self._transparency_level = level
        self.structured_logger.info(
            "Transparency level changed",
            level=level,
            agent_id=self.agent_id,
        )

    def log_action(self, action_data: dict[str, Any]) -> bool:
        """
        Записать действие с прозрачностью.

        Args:
            action_data: Словарь с данными действия
                - planned: Что планировалось сделать
                - executed: Что было фактически выполнено
                - status: Статус ("executed", "modified", "blocked", "skipped")
                - confidence: Уверенность в выполнении (0.0-1.0)
                - user_approval: Было ли действие одобрено пользователем

        Returns:
            True если действие записано успешно, False если заблокировано
        """
        # Проверка обязательных полей
        required_fields = ["planned", "executed", "status"]
        missing_fields = [field for field in required_fields if field not in action_data]
        if missing_fields:
            self.structured_logger.error(
                "Missing required fields in action data",
                missing_fields=missing_fields,
                agent_id=self.agent_id,
            )
            return False

        # Проверка на расхождение (обман)
        planned = action_data["planned"]
        executed = action_data["executed"]
        is_discrepancy = planned != executed

        # Формирование записи
        transparency_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent_id": self.agent_id,
            "planned": planned,
            "executed": executed,
            "status": action_data["status"],
            "confidence": action_data.get("confidence", 1.0),
            "user_approval": action_data.get("user_approval", False),
            "is_discrepancy": is_discrepancy,
            "transparency_level": self._transparency_level,
        }

        # Запись в файл
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(transparency_entry, ensure_ascii=False) + "\n")

        # Хранение в памяти
        self._action_history.append(transparency_entry)

        # Интеграция с audit_logger
        if self.audit_logger:
            self.audit_logger.log_action(
                action="transparency",
                details={
                    "planned": str(planned)[:100],  # Truncate for readability
                    "executed": str(executed)[:100],
                    "is_discrepancy": is_discrepancy,
                },
                status="warning" if is_discrepancy else "success",
            )

        # Логирование в структурированный логгер
        log_level = "warning" if is_discrepancy else "info"
        getattr(self.structured_logger, log_level)(
            "Action logged with transparency",
            planned=planned,
            executed=executed,
            status=action_data["status"],
            is_discrepancy=is_discrepancy,
            agent_id=self.agent_id,
        )

        return True

    def get_status(self) -> dict[str, Any]:
        """
        Получить текущий статус прозрачности.

        Returns:
            Словарь с информацией о прозрачности
        """
        total_actions = len(self._action_history)
        discrepancies = sum(1 for action in self._action_history if action["is_discrepancy"])
        approved_actions = sum(1 for action in self._action_history if action["user_approval"])

        return {
            "agent_id": self.agent_id,
            "transparency_level": self._transparency_level,
            "total_actions": total_actions,
            "discrepancies": discrepancies,
            "approved_actions": approved_actions,
            "discrepancy_rate": (discrepancies / total_actions if total_actions > 0 else 0.0),
            "history_preview": self._action_history[-5:],  # Last 5 actions
        }

    def get_discrepancies(self) -> list[dict[str, Any]]:
        """
        Получить все действия с расхождениями.

        Returns:
            Список действий, где planned != executed
        """
        return [action for action in self._action_history if action["is_discrepancy"]]

    def clear_history(self):
        """Очистить историю действий."""
        self._action_history = []
        self.structured_logger.info(
            "Transparency history cleared",
            agent_id=self.agent_id,
        )

    def export_to_audit(self, audit_logger: Any):
        """
        Экспортировать историю в AuditLogger.

        Args:
            audit_logger: Экземпляр AuditLogger для экспорта
        """
        for action in self._action_history:
            audit_logger.log_action(
                action="transparency_export",
                details={
                    "planned": str(action["planned"]),
                    "executed": str(action["executed"]),
                    "status": action["status"],
                    "is_discrepancy": action["is_discrepancy"],
                },
                status="warning" if action["is_discrepancy"] else "success",
            )
