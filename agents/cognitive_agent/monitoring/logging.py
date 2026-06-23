"""Structured logging module for cognitive agent."""

import json
from datetime import datetime
from pathlib import Path

import structlog


class StructuredLogger:
    """Структурированный логгер для JSON-вывода (ELK/Grafana compatible)"""

    def __init__(self, name: str, log_file: str = None):
        self.logger = structlog.get_logger(name)

        # JSON-логгер для файлов (ELK/Grafana)
        if log_file:
            self._json_log_file = log_file
            Path(self._json_log_file).parent.mkdir(parents=True, exist_ok=True)
        else:
            self._json_log_file = None

    def _write_json(self, level: str, message: str, **kwargs):
        """Записать запись в JSON-файл"""
        if self._json_log_file:
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
