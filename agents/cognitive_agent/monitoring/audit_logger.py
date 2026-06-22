"""Audit logging module for cognitive agent."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import structlog


class AuditLogger:
    """Логгер аудита для трассировки всех действий агента"""

    def __init__(self, agent_id: str, log_file: str = None, structured_logger=None):
        self.agent_id = agent_id
        self.log_file = log_file or str(
            Path.home() / ".agent_data" / "logs" / "agent_audit.jsonl"
        )
        self.structured_logger = structured_logger
        self._ensure_log_file()

    def _ensure_log_file(self):
        """Убедиться, что файл аудита существует"""
        Path(self.log_file).parent.mkdir(parents=True, exist_ok=True)
        if not Path(self.log_file).exists():
            Path(self.log_file).touch()

    def log_action(self, action: str, details: dict, status: str = "success"):
        """
        Записать действие в аудит-лог.

        Args:
            action: Название действия (scan, plan, execute, etc.)
            details: Детали действия
            status: Статус выполнения (success, failed, blocked)
        """
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent_id": self.agent_id,
            "action": action,
            "details": details,
            "status": status,
        }

        # Запись в JSONL-файл (для ELK/Fluentd)
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(audit_entry, ensure_ascii=False) + "\n")

        # Логирование в структурированный логгер
        if self.structured_logger:
            self.structured_logger.info(
                "Audit log entry",
                action=action,
                agent_id=self.agent_id,
                status=status,
            )

    def log_security_event(self, event_type: str, details: dict, severity: str = "warning"):
        """Записать событие безопасности в аудит"""
        self.log_action(
            action=f"security:{event_type}",
            details=details,
            status="blocked" if severity == "critical" else "warning",
        )
        if self.structured_logger:
            self.structured_logger.warning(
                f"Security event: {event_type}",
                severity=severity,
                **details,
            )
