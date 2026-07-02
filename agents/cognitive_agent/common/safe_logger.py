"""Безопасный логгер с фильтрацией чувствительных данных"""

import logging
import re
from typing import Any


class SafeLogger:
    """Безопасный логгер с фильтрацией чувствительных данных

    Предназначен для логирования, которое может содержать:
    - Токены API
    - Пароли
    - Секретные ключи
    - Любые другие чувствительные данные

    Все чувствительные данные автоматически заменяются на [REDACTED]
    """

    def __init__(self, name: str, level: int = logging.INFO):
        """Инициализация безопасного логгера

        Args:
            name: Имя логгера (обычно имя модуля)
            level: Уровень логирования (по умолчанию INFO)
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # Паттерны для фильтрации чувствительных данных
        # Каждый кортеж: (pattern, replacement)
        self.sensitive_patterns: list[tuple[str, str]] = [
            # Токены API
            (r'(token["\s:=]+)["\'][^"\']+["\']', r"\1[REDACTED]"),
            (r'(api_key["\s:=]+)["\'][^"\']+["\']', r"\1[REDACTED]"),
            (r'(apikey["\s:=]+)["\'][^"\']+["\']', r"\1[REDACTED]"),
            # Пароли
            (r'(password["\s:=]+)["\'][^"\']+["\']', r"\1[REDACTED]"),
            (r'(passwd["\s:=]+)["\'][^"\']+["\']', r"\1[REDACTED]"),
            # Секретные ключи
            (r'(secret["\s:=]+)["\'][^"\']+["\']', r"\1[REDACTED]"),
            (r'(private_key["\s:=]+)["\'][^"\']+["\']', r"\1[REDACTED]"),
            # Bearer токены
            (r"(bearer\s+)[^\s]+", r"\1[REDACTED]"),
            (r"(authorization\s*:\s*)[^\s]+", r"\1[REDACTED]"),
            # AWS/Cloud ключи
            (r'(aws_secret_access_key["\s:=]+)["\'][^"\']+["\']', r"\1[REDACTED]"),
            (r'(access_key_id["\s:=]+)["\'][^"\']+["\']', r"\1[REDACTED]"),
            # GitHub/GitLab токены
            (r'(github_token["\s:=]+)["\'][^"\']+["\']', r"\1[REDACTED]"),
            (r'(gitlab_token["\s:=]+)["\'][^"\']+["\']', r"\1[REDACTED]"),
            # 一般敏感数据 (long random strings that might be secrets)
            (r'(["\'])([a-zA-Z0-9]{32,64})["\']', r"\1[REDACTED]\1"),
        ]

    def _sanitize(self, message: str) -> str:
        """Фильтрация чувствительных данных из строки

        Args:
            message: Исходное сообщение

        Returns:
            str: Сообщение с заменёнными чувствительными данными
        """
        sanitized = message
        for pattern, replacement in self.sensitive_patterns:
            sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)
        return sanitized

    def info(self, message: str, **kwargs: Any) -> None:
        """Информационное сообщение

        Args:
            message: Сообщение для логирования
            **kwargs: Дополнительные параметры (передаются в logging.info)
        """
        self.logger.info(self._sanitize(message), **kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        """Предупреждение

        Args:
            message: Сообщение для логирования
            **kwargs: Дополнительные параметры (передаются в logging.warning)
        """
        self.logger.warning(self._sanitize(message), **kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        """Ошибка

        Args:
            message: Сообщение для логирования
            **kwargs: Дополнительные параметры (передаются в logging.error)
        """
        self.logger.error(self._sanitize(message), **kwargs)

    def debug(self, message: str, **kwargs: Any) -> None:
        """Отладочное сообщение

        Args:
            message: Сообщение для логирования
            **kwargs: Дополнительные параметры (передаются в logging.debug)
        """
        self.logger.debug(self._sanitize(message), **kwargs)

    def critical(self, message: str, **kwargs: Any) -> None:
        """Критическая ошибка

        Args:
            message: Сообщение для логирования
            **kwargs: Дополнительные параметры (передаются в logging.critical)
        """
        self.logger.critical(self._sanitize(message), **kwargs)

    def set_level(self, level: int) -> None:
        """Установка уровня логирования

        Args:
            level: Новый уровень логирования
        """
        self.logger.setLevel(level)
