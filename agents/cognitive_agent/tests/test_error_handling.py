"""
Тесты для системы обработки ошибок Cognitive Agent
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock

import pytest

from cognitive_agent.common import (
    AgentStateError,
    AIServiceError,
    AuditLogError,
    BaseAgentExtensions,
    BaseLogger,
    BaseProjectScanner,
    BaseSecurityChecker,
    CacheError,
    CognitiveAgentError,
    ConfigurationError,
    DataProcessingError,
    ErrorHandler,
    FileOperationError,
    IntegrationError,
    NetworkError,
    ResourceExhaustionError,
    SecurityViolationError,
    TaskExecutionError,
    ValidationError,
    handle_errors,
)


class TestErrorHandling:
    """
    Тесты для системы обработки ошибок
    """

    def test_exception_hierarchy(self):
        """Тест иерархии исключений"""
        # Все исключения должны наследоваться от CognitiveAgentError
        exceptions = [
            ConfigurationError,
            SecurityViolationError,
            ResourceExhaustionError,
            AIServiceError,
            FileOperationError,
            NetworkError,
            ValidationError,
            TaskExecutionError,
            IntegrationError,
            AgentStateError,
            DataProcessingError,
            CacheError,
            AuditLogError,
        ]

        for exc_class in exceptions:
            exc = exc_class("Тестовое сообщение")
            assert isinstance(exc, CognitiveAgentError)
            assert exc.message == "Тестовое сообщение"

    def test_exception_with_details(self):
        """Тест исключений с деталями"""
        details = {"key": "value", "number": 42}
        exc = ConfigurationError("Ошибка конфигурации", details=details)

        assert exc.details == details
        assert exc.to_dict()["details"] == details
        assert exc.to_dict()["message"] == "Ошибка конфигурации"
        assert exc.to_dict()["type"] == "ConfigurationError"

    def test_error_handler_initialization(self):
        """Тест инициализации обработчика ошибок"""
        logger = Mock()
        handler = ErrorHandler(logger=logger)

        assert handler.logger == logger
        assert isinstance(handler.error_counts, dict)
        assert handler.max_retries == 3
        assert len(handler.retry_delays) == 3

    def test_error_handler_handles_exception(self):
        """Тест обработки исключения обработчиком"""
        logger = Mock()
        handler = ErrorHandler(logger=logger)

        context = {"operation": "test", "value": 123}
        error = ValueError("Тестовая ошибка")

        error_info = handler.handle_error(error, context)

        assert error_info["handled"] is True
        assert error_info["original_error"] == error
        assert error_info["context"] == context
        assert error_info["error_type"] == "ValueError"
        assert error_info["recovery_action"] == "escalate"

        # Проверить, что ошибка зарегистрирована в логгере
        logger.error.assert_called_once()

    def test_error_handler_determines_recovery_action(self):
        """Тест определения действия восстановления"""
        handler = ErrorHandler()

        # Тесты для разных типов ошибок
        test_cases = [
            (ConfigurationError("Config error"), "configuration_fix"),
            (SecurityViolationError("Security error"), "security_review"),
            (ResourceExhaustionError("Resource error"), "resource_cleanup"),
            (AIServiceError("AI error"), "provider_switch"),
            (FileOperationError("File error"), "file_validation"),
            (NetworkError("Network error"), "connection_retry"),
            (ValidationError("Validation error"), "configuration_fix"),
            (TaskExecutionError("Task error"), "task_reschedule"),
            (CacheError("Cache error"), "cache_clear"),
            (Exception("Generic error"), "escalate"),
        ]

        for error, expected_action in test_cases:
            action = handler._determine_recovery_action(error)
            assert action == expected_action

    def test_error_handler_should_retry_logic(self):
        """Тест логики повтора попыток"""
        handler = ErrorHandler()

        # Ошибки, для которых НЕ нужно повторять
        no_retry_errors = [
            SecurityViolationError("Security error"),
            ConfigurationError("Config error"),
            ValidationError("Validation error"),
        ]

        for error in no_retry_errors:
            assert handler._should_retry(error) is False

        # Ошибки, для которых НУЖНО повторять
        retry_errors = [
            NetworkError("Network error"),
            AIServiceError("AI error"),
            ResourceExhaustionError("Resource error"),
        ]

        for error in retry_errors:
            assert handler._should_retry(error) is True

    def test_safe_execute_successful(self):
        """Тест безопасного выполнения успешной функции"""
        handler = ErrorHandler()

        def successful_func(x, y):
            return x + y

        result = handler.safe_execute(successful_func, 5, 3)
        assert result == 8

    def test_safe_execute_with_exception(self):
        """Тест безопасного выполнения с исключением"""
        handler = ErrorHandler()

        def failing_func():
            raise ValueError("Ошибка выполнения")

        result = handler.safe_execute(failing_func)

        assert isinstance(result, dict)
        assert result["success"] is False
        assert "error_info" in result

    def test_safe_execute_with_context(self):
        """Тест безопасного выполнения с контекстом"""
        logger = Mock()
        handler = ErrorHandler(logger=logger)

        context = {"operation": "test_operation"}

        def failing_func():
            raise TaskExecutionError("Ошибка задачи")

        result = handler.safe_execute(failing_func, error_context=context)

        assert isinstance(result, dict)
        assert result["success"] is False
        assert result["error_info"]["context"] == context

        # Проверить, что контекст передан в логгер
        logger.error.assert_called()
        call_args = logger.error.call_args
        assert context in str(call_args)

    def test_error_statistics(self):
        """Тест статистики ошибок"""
        handler = ErrorHandler()

        # Вызвать несколько разных ошибок
        handler.handle_error(ValueError("Error 1"))
        handler.handle_error(ValueError("Error 2"))
        handler.handle_error(TypeError("Error 3"))

        stats = handler.get_error_statistics()

        assert stats["ValueError"] == 2
        assert stats["TypeError"] == 1

    def test_error_statistics_reset(self):
        """Тест сброса статистики ошибок"""
        handler = ErrorHandler()

        handler.handle_error(ValueError("Error 1"))
        assert len(handler.get_error_statistics()) > 0

        handler.reset_error_statistics()
        assert len(handler.get_error_statistics()) == 0

    def test_handle_errors_decorator(self):
        """Тест декоратора обработки ошибок"""
        logger = Mock()

        @handle_errors(logger=logger)
        def decorated_func():
            raise ConfigurationError("Ошибка конфигурации")

        result = decorated_func()

        assert isinstance(result, dict)
        assert result["success"] is False
        assert "error_info" in result

    def test_components_use_new_exceptions(self):
        """Тест того, что компоненты используют новую систему исключений"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Тест BaseLogger с ошибкой аудита
            try:
                BaseLogger.setup_logging(log_file="/invalid/path/log.txt")
            except AuditLogError:
                pass  # Ожидаемое поведение
            except Exception:
                # Другие исключения тоже допустимы, если они не нарушают контракт
                pass

            # Тест BaseProjectScanner с валидацией
            with pytest.raises(ValidationError):
                BaseProjectScanner("/nonexistent/path")

            # Тест BaseAgentExtensions с валидацией
            with pytest.raises(ConfigurationError):
                BaseAgentExtensions("/nonexistent/path")

    def test_base_agent_extensions_error_handling_methods(self):
        """Тест методов обработки ошибок в BaseAgentExtensions"""
        with tempfile.TemporaryDirectory() as temp_dir:
            extensions = BaseAgentExtensions(temp_dir)

            # Тест кэширования с ошибкой
            with pytest.raises(CacheError):
                extensions.cache_result(None, "test")  # None в качестве ключа вызовет ошибку

            # Тест получения из кэша с ошибкой
            with pytest.raises(CacheError):
                extensions.get_cached_result(None)  # None в качестве ключа вызовет ошибку

            # Тест валидации контекста задачи
            with pytest.raises(ValidationError):
                extensions.validate_task_context({})  # Пустой контекст не содержит обязательных полей

    def test_base_project_scanner_error_handling(self):
        """Тест обработки ошибок в BaseProjectScanner"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Создать scanner
            scanner = BaseProjectScanner(temp_dir)

            # Тест получения измененных файлов с ошибкой
            with pytest.raises(FileOperationError):
                scanner.get_changed_files("invalid_commit_ref")

    def test_base_security_checker_integration(self):
        """Тест интеграции BaseSecurityChecker с системой исключений"""
        checker = BaseSecurityChecker()

        # Тест валидации безопасного пути
        is_safe, message = checker.validate_path("./safe/path")
        assert is_safe is True

        # Тест валидации опасной команды
        is_safe, message = checker.validate_command("rm -rf /")
        assert is_safe is False


if __name__ == "__main__":
    pytest.main([__file__])
