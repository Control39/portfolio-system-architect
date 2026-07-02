"""Тесты для безопасного логгера (common/safe_logger.py)

# pragma: allowlist secret

Service Tier: COMMON
Purpose: Unit testing for SafeLogger class with sensitive data filtering
"""

import logging

import pytest

from agents.cognitive_agent.common.safe_logger import SafeLogger


class TestSafeLoggerInitialization:
    """Тесты инициализации SafeLogger"""

    def test_initialization_with_default_level(self):
        """Тест инициализации с уровнем по умолчанию"""
        logger = SafeLogger("test_logger")

        assert logger is not None
        assert logger.logger.name == "test_logger"
        # Проверяем, что паттерны инициализированы
        assert len(logger.sensitive_patterns) > 0

    def test_initialization_with_custom_level(self):
        """Тест инициализации с кастомным уровнем"""
        logger = SafeLogger("test_logger", level=10)  # DEBUG level

        assert logger is not None
        assert logger.logger.level == 10

    def test_has_sanitize_method(self):
        """Тест наличия метода _sanitize"""
        logger = SafeLogger("test_logger")

        assert hasattr(logger, "_sanitize")
        assert callable(logger._sanitize)


class TestSafeLoggerSanitization:
    """Тесты фильтрации чувствительных данных"""

    def test_api_token_filtering(self):
        """Тест фильтрации API токена"""
        logger = SafeLogger("test_logger")

        message = 'token="secret-token-12345"'
        sanitized = logger._sanitize(message)

        # pragma: allowlist secret
        assert "secret-token-12345" not in sanitized
        assert "[REDACTED]" in sanitized

    def test_api_key_filtering(self):
        """Тест фильтрации API ключа"""
        logger = SafeLogger("test_logger")

        message = 'api_key="my-api-key-12345"'
        sanitized = logger._sanitize(message)

        # pragma: allowlist secret
        assert "my-api-key-12345" not in sanitized
        assert "[REDACTED]" in sanitized

    def test_password_filtering(self):
        """Тест фильтрации пароля"""
        logger = SafeLogger("test_logger")

        message = 'password="super_secret_password"'
        sanitized = logger._sanitize(message)

        # pragma: allowlist secret
        assert "super_secret_password" not in sanitized
        assert "[REDACTED]" in sanitized

    def test_secret_filtering(self):
        """Тест фильтрации секрета"""
        logger = SafeLogger("test_logger")

        message = 'secret="my-secret-key"'
        sanitized = logger._sanitize(message)

        # pragma: allowlist secret
        assert "my-secret-key" not in sanitized
        assert "[REDACTED]" in sanitized

    def test_bearer_token_filtering(self):
        """Тест фильтрации Bearer токена"""
        logger = SafeLogger("test_logger")

        message = "Bearer secret-bearer-token-12345"
        sanitized = logger._sanitize(message)

        # pragma: allowlist secret
        assert "secret-bearer-token-12345" not in sanitized
        assert "[REDACTED]" in sanitized

    def test_multiple_secrets_filtering(self):
        """Тест фильтрации нескольких секретов в одной строке"""
        logger = SafeLogger("test_logger")

        message = 'token="secret1" and api_key="secret2" and password="secret3"'
        sanitized = logger._sanitize(message)

        assert "secret1" not in sanitized
        assert "secret2" not in sanitized
        assert "secret3" not in sanitized
        assert sanitized.count("[REDACTED]") >= 3

    def test_normal_message_not_filtered(self):
        """Тест, что обычное сообщение не фильтруется"""
        logger = SafeLogger("test_logger")

        message = "This is a normal message without secrets"
        sanitized = logger._sanitize(message)

        assert sanitized == message

    def test_case_insensitive_filtering(self):
        """Тест, что фильтрация нечувствительна к регистру"""
        logger = SafeLogger("test_logger")

        message = 'TOKEN="secret-token"'
        sanitized = logger._sanitize(message)

        assert "secret-token" not in sanitized
        assert "[REDACTED]" in sanitized


class TestSafeLoggerMethods:
    """Тесты методов логирования"""

    def test_info_method_exists(self):
        """Тест наличия метода info"""
        logger = SafeLogger("test_logger")

        assert hasattr(logger, "info")
        assert callable(logger.info)

    def test_warning_method_exists(self):
        """Тест наличия метода warning"""
        logger = SafeLogger("test_logger")

        assert hasattr(logger, "warning")
        assert callable(logger.warning)

    def test_error_method_exists(self):
        """Тест наличия метода error"""
        logger = SafeLogger("test_logger")

        assert hasattr(logger, "error")
        assert callable(logger.error)

    def test_debug_method_exists(self):
        """Тест наличия метода debug"""
        logger = SafeLogger("test_logger")

        assert hasattr(logger, "debug")
        assert callable(logger.debug)

    def test_critical_method_exists(self):
        """Тест наличия метода critical"""
        logger = SafeLogger("test_logger")

        assert hasattr(logger, "critical")
        assert callable(logger.critical)

    def test_set_level_method_exists(self):
        """Тест наличия метода set_level"""
        logger = SafeLogger("test_logger")

        assert hasattr(logger, "set_level")
        assert callable(logger.set_level)


class TestSafeLoggerIntegration:
    """Интеграционные тесты SafeLogger"""

    def test_logging_with_sensitive_data(self, caplog):
        """Тест логирования с чувствительными данными"""
        logger = SafeLogger("test_logger", level=logging.DEBUG)

        # Тестируем, что сообщение логируется с фильтрацией
        logger.info('token="secret-token"')

        # Проверяем, что в логе нет оригинального токена
        assert "secret-token" not in caplog.text
        assert "[REDACTED]" in caplog.text

    def test_logging_normal_message(self, caplog):
        """Тест логирования обычного сообщения"""
        logger = SafeLogger("test_logger", level=logging.INFO)

        logger.info("Normal message without secrets")

        assert "Normal message without secrets" in caplog.text

    def test_logging_warning_with_api_key(self, caplog):
        """Тест предупреждения с API ключом"""
        logger = SafeLogger("test_logger", level=logging.WARNING)

        logger.warning('api_key="my-secret-key"')

        assert "my-secret-key" not in caplog.text
        assert "[REDACTED]" in caplog.text


class TestSafeLoggerEdgeCases:
    """Тесты граничных случаев SafeLogger"""

    def test_empty_message(self):
        """Тест пустого сообщения"""
        logger = SafeLogger("test_logger")

        message = ""
        sanitized = logger._sanitize(message)

        assert sanitized == ""

    def test_message_without_secrets(self):
        """Тест сообщения без секретов"""
        logger = SafeLogger("test_logger")

        message = "This is a public message"
        sanitized = logger._sanitize(message)

        assert sanitized == message

    def test_message_with_partial_patterns(self):
        """Тест сообщения с частичными паттернами"""
        logger = SafeLogger("test_logger")

        message = 'token is not valid"'
        sanitized = logger._sanitize(message)

        # Не должно фильтроваться, так как нет значения
        assert 'token is not valid"' in sanitized

    def test_long_secret_value(self):
        """Тест фильтрации очень длинного секрета"""
        logger = SafeLogger("test_logger")

        long_secret = "a" * 1000
        message = f'token="{long_secret}"'
        sanitized = logger._sanitize(message)

        assert long_secret not in sanitized
        assert "[REDACTED]" in sanitized

    def test_unicode_in_secrets(self):
        """Тест фильтрации секретов с unicode"""
        logger = SafeLogger("test_logger")

        message = 'token="секретный-токен-123"'
        sanitized = logger._sanitize(message)

        assert "секретный-токен-123" not in sanitized
        assert "[REDACTED]" in sanitized
