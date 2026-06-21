#!/usr/bin/env python3
"""
Улучшенная система логирования для когнитивного агента
"""

import json
import logging
from datetime import datetime
from pathlib import Path

import structlog

# Добавляем корень проекта в PATH
REPO_ROOT = Path(__file__).parent.parent.parent


# Настройка логирования
def setup_logging():
    """Настройка системы логирования"""

    # Создаем директории для логов
    log_dir = REPO_ROOT / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    # Настройка стандартного логирования
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_dir / "cognitive_agent.log"),
            logging.StreamHandler(),
        ],
    )

    # Настройка structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.WriteLoggerFactory(),
        cache_logger_on_first_use=False,
    )

    return logging.getLogger(__name__)


# ⭐ [МОНИТОРИНГ] Structured Logger (JSON)
class StructuredLogger:
    """Структурированный логгер для JSON-вывода (ELK/Grafana compatible)"""

    def __init__(self, name: str, log_file: str = None):
        self.logger = structlog.get_logger(name)

        # JSON-логгер для файлов (ELK/Grafana)
        if log_file:
            self._json_log_file = Path(log_file)
            self._json_log_file.parent.mkdir(parents=True, exist_ok=True)
        else:
            self._json_log_file = REPO_ROOT / "logs" / "cognitive_agent.json"

    def _write_json(self, level: str, message: str, **kwargs):
        """Записать запись в JSON-файл"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message,
            **kwargs,
        }
        with open(self._json_log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def info(self, message: str, **kwargs):
        self.logger.info(message, **kwargs)
        self._write_json("info", message, **kwargs)

    def error(self, message: str, **kwargs):
        self.logger.error(message, **kwargs)
        self._write_json("error", message, **kwargs)

    def warning(self, message: str, **kwargs):
        self.logger.warning(message, **kwargs)
        self._write_json("warning", message, **kwargs)

    def debug(self, message: str, **kwargs):
        self.logger.debug(message, **kwargs)
        self._write_json("debug", message, **kwargs)


# ⭐ [МОНИТОРИНГ] Audit Logger для трассировки действий
class AuditLogger:
    """Логгер аудита для трассировки всех действий агента"""

    def __init__(self, agent_id: str, log_file: str = None):
        self.agent_id = agent_id
        self.log_file = Path(log_file) if log_file else REPO_ROOT / "logs" / "agent_audit.jsonl"
        self._ensure_log_file()

    def _ensure_log_file(self):
        """Убедиться, что файл аудита существует"""
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.log_file.exists():
            self.log_file.touch()

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
        structured_logger = StructuredLogger(
            "cognitive_agent",
            log_file=str(REPO_ROOT / "logs" / "cognitive_agent.json"),
        )
        structured_logger.info(
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
        structured_logger = StructuredLogger(
            "cognitive_agent",
            log_file=str(REPO_ROOT / "logs" / "cognitive_agent.json"),
        )
        structured_logger.warning(
            f"Security event: {event_type}",
            severity=severity,
            **details,
        )


# Инициализация глобальных логгеров
logger = setup_logging()
structured_logger = StructuredLogger(
    "cognitive_agent",
    log_file=str(REPO_ROOT / "logs" / "cognitive_agent.json"),
)
