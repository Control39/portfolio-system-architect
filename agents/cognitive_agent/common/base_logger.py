"""
Базовый логгер для Cognitive Agent
"""

import logging

import structlog

from .exceptions import AuditLogError


class BaseLogger:
    """
    Базовый класс логгера для Cognitive Agent
    Использует structlog для структурированного логирования
    """

    def __init__(self, name: str, log_level: str = "INFO", log_format: str = "json"):
        """
        Инициализировать базовый логгер

        Args:
            name: Имя логгера
            log_level: Уровень логирования
            log_format: Формат логов ("json" или "text")
        """
        self.name = name
        self.log_level = getattr(logging, log_level.upper())

        # Настройка structlog
        if log_format.lower() == "json":
            structlog.configure(
                processors=[
                    structlog.stdlib.filter_by_level,
                    structlog.stdlib.add_logger_name,
                    structlog.stdlib.add_log_level,
                    structlog.stdlib.PositionalArgumentsFormatter(),
                    structlog.processors.TimeStamper(fmt="iso"),
                    structlog.processors.StackInfoRenderer(),
                    structlog.processors.format_exc_info,
                    structlog.processors.UnicodeDecoder(),
                    structlog.processors.JSONRenderer(),
                ],
                context_class=dict,
                logger_factory=structlog.stdlib.LoggerFactory(),
                wrapper_class=structlog.stdlib.BoundLogger,
                cache_logger_on_first_use=True,
            )
        else:
            structlog.configure(
                processors=[
                    structlog.stdlib.filter_by_level,
                    structlog.stdlib.add_logger_name,
                    structlog.stdlib.add_log_level,
                    structlog.stdlib.PositionalArgumentsFormatter(),
                    structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
                    structlog.processors.StackInfoRenderer(),
                    structlog.processors.format_exc_info,
                    structlog.processors.UnicodeDecoder(),
                    structlog.processors.KeyValueRenderer(key_order=["timestamp", "level", "logger", "event"]),
                ],
                context_class=dict,
                logger_factory=structlog.stdlib.LoggerFactory(),
                wrapper_class=structlog.stdlib.BoundLogger,
                cache_logger_on_first_use=True,
            )

        self.logger = structlog.get_logger(name)
        self.logger.setLevel(self.log_level)

    def info(self, message: str, **kwargs):
        """Логировать информационное сообщение"""
        self.logger.info(message, **kwargs)

    def debug(self, message: str, **kwargs):
        """Логировать отладочное сообщение"""
        self.logger.debug(message, **kwargs)

    def warning(self, message: str, **kwargs):
        """Логировать предупреждение"""
        self.logger.warning(message, **kwargs)

    def error(self, message: str, **kwargs):
        """Логировать ошибку"""
        self.logger.error(message, **kwargs)

    def critical(self, message: str, **kwargs):
        """Логировать критическую ошибку"""
        self.logger.critical(message, **kwargs)

    def bind(self, **kwargs):
        """Привязать контекст к логгеру"""
        self.logger = self.logger.bind(**kwargs)

    def unbind(self, *keys):
        """Отвязать контекст от логгера"""
        self.logger = self.logger.unbind(*keys)


def setup_logging(log_level: str = "INFO", log_format: str = "json", log_file: str | None = None):
    """
    Настроить глобальное логирование для приложения

    Args:
        log_level: Уровень логирования
        log_format: Формат логов ("json" или "text")
        log_file: Путь к файлу логов (опционально)
    """
    try:
        if log_file:
            # Настройка логирования в файл
            logging.basicConfig(
                level=getattr(logging, log_level.upper()),
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                handlers=[logging.FileHandler(log_file, encoding="utf-8"), logging.StreamHandler()],
            )
        else:
            # Настройка логирования в stdout
            logging.basicConfig(
                level=getattr(logging, log_level.upper()), format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
    except Exception as e:
        # Если возникла ошибка при настройке логирования, выбросить специальное исключение
        raise AuditLogError(
            f"Не удалось настроить логирование: {str(e)}",
            details={"log_level": log_level, "log_format": log_format, "log_file": log_file},
        )
