"""
Иерархия исключений для Cognitive Agent
"""

import traceback
from typing import Any


class CognitiveAgentError(Exception):
    """
    Базовое исключение для агента
    """

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}
        self.timestamp = None
        self.traceback_info = traceback.format_exc() if self.__cause__ else None

    def to_dict(self) -> dict[str, Any]:
        """
        Преобразовать исключение в словарь для логирования
        """
        return {
            "type": self.__class__.__name__,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "traceback": self.traceback_info,
        }


class ConfigurationError(CognitiveAgentError):
    """
    Ошибка конфигурации агента
    """

    pass


class SecurityViolationError(CognitiveAgentError):
    """
    Нарушение безопасности
    """

    pass


class ResourceExhaustionError(CognitiveAgentError):
    """
    Исчерпание ресурсов (память, диск, CPU)
    """

    pass


class AIServiceError(CognitiveAgentError):
    """
    Ошибка сервиса ИИ
    """

    pass


class FileOperationError(CognitiveAgentError):
    """
    Ошибка операции с файлами
    """

    pass


class NetworkError(CognitiveAgentError):
    """
    Ошибка сети
    """

    pass


class ValidationError(CognitiveAgentError):
    """
    Ошибка валидации данных
    """

    pass


class TaskExecutionError(CognitiveAgentError):
    """
    Ошибка выполнения задачи
    """

    pass


class IntegrationError(CognitiveAgentError):
    """
    Ошибка интеграции с внешними системами
    """

    pass


class AgentStateError(CognitiveAgentError):
    """
    Ошибка состояния агента
    """

    pass


class DataProcessingError(CognitiveAgentError):
    """
    Ошибка обработки данных
    """

    pass


class CacheError(CognitiveAgentError):
    """
    Ошибка кэширования
    """

    pass


class AuditLogError(CognitiveAgentError):
    """
    Ошибка аудит-логирования
    """

    pass


class ErrorHandler:
    """
    Централизованный обработчик ошибок для Cognitive Agent
    """

    def __init__(self, logger=None):
        """
        Инициализировать обработчик ошибок

        Args:
            logger: Логгер для записи ошибок
        """
        self.logger = logger
        self.error_counts = {}  # Счетчик ошибок по типам
        self.max_retries = 3  # Максимальное количество повторных попыток
        self.retry_delays = [1, 2, 4]  # Задержки между попытками (в секундах)

    def handle_error(self, error: Exception, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        Обработать ошибку и вернуть информацию о ней

        Args:
            error: Объект ошибки
            context: Контекст, в котором произошла ошибка

        Returns:
            Словарь с информацией об ошибке
        """
        error_info = {
            "handled": True,
            "original_error": error,
            "timestamp": None,
            "context": context or {},
            "recovery_action": "none",
            "should_retry": False,
            "retry_count": 0,
        }

        # Определить тип ошибки
        error_type = type(error).__name__
        error_info["error_type"] = error_type

        # Увеличить счетчик ошибок
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1

        # Зарегистрировать ошибку в логгере
        if self.logger:
            self.logger.error(
                f"Обработана ошибка: {error_type}",
                error_type=error_type,
                message=str(error),
                context=context,
                error_count=self.error_counts[error_type],
            )

        # Определить действие восстановления на основе типа ошибки
        recovery_action = self._determine_recovery_action(error)
        error_info["recovery_action"] = recovery_action

        # Определить, нужно ли повторить попытку
        error_info["should_retry"] = self._should_retry(error)

        return error_info

    def _determine_recovery_action(self, error: Exception) -> str:
        """
        Определить действие восстановления на основе типа ошибки

        Args:
            error: Объект ошибки

        Returns:
            Действие восстановления
        """
        type(error).__name__

        if isinstance(error, (ConfigurationError, ValidationError)):
            return "configuration_fix"  # Требуется исправление конфигурации
        elif isinstance(error, SecurityViolationError):
            return "security_review"  # Требуется проверка безопасности
        elif isinstance(error, ResourceExhaustionError):
            return "resource_cleanup"  # Требуется очистка ресурсов
        elif isinstance(error, AIServiceError):
            return "provider_switch"  # Требуется переключение провайдера ИИ
        elif isinstance(error, FileOperationError):
            return "file_validation"  # Требуется проверка файловой операции
        elif isinstance(error, NetworkError):
            return "connection_retry"  # Требуется повторное подключение
        elif isinstance(error, TaskExecutionError):
            return "task_reschedule"  # Требуется перепланирование задачи
        elif isinstance(error, CacheError):
            return "cache_clear"  # Требуется очистка кэша
        else:
            return "escalate"  # Передать выше

    def _should_retry(self, error: Exception) -> bool:
        """
        Определить, нужно ли повторить попытку

        Args:
            error: Объект ошибки

        Returns:
            Нужно ли повторить попытку
        """
        # Не повторять для ошибок безопасности и конфигурации
        if isinstance(error, (SecurityViolationError, ConfigurationError, ValidationError)):
            return False

        # Повторять для сетевых ошибок и ошибок ИИ
        if isinstance(error, (NetworkError, AIServiceError)):
            return True

        # Повторять для ошибок ресурсов (могут быть временные перегрузки)
        if isinstance(error, ResourceExhaustionError):
            return True

        # Повторять для других ошибок в зависимости от ситуации
        return False

    def safe_execute(self, func, *args, error_context: dict[str, Any] | None = None, **kwargs):
        """
        Безопасно выполнить функцию с обработкой ошибок

        Args:
            func: Функция для выполнения
            *args: Аргументы функции
            error_context: Контекст ошибки
            **kwargs: Ключевые аргументы функции

        Returns:
            Результат выполнения функции или информация об ошибке
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_info = self.handle_error(e, error_context)

            # Если нужно повторить попытку
            if error_info["should_retry"] and error_info.get("retry_count", 0) < self.max_retries:
                import time

                delay = self.retry_delays[min(error_info.get("retry_count", 0), len(self.retry_delays) - 1)]
                time.sleep(delay)

                # Увеличить счетчик повторов
                error_info["retry_count"] = error_info.get("retry_count", 0) + 1

                # Повторить выполнение
                return self.safe_execute(func, *args, error_context=error_context, **kwargs)

            # Если не удалось выполнить после повторов или повтор не нужен
            return {"success": False, "error_info": error_info}

    def get_error_statistics(self) -> dict[str, int]:
        """
        Получить статистику ошибок

        Returns:
            Словарь с количеством ошибок по типам
        """
        return self.error_counts.copy()

    def reset_error_statistics(self):
        """
        Сбросить статистику ошибок
        """
        self.error_counts.clear()


# Глобальный обработчик ошибок
global_error_handler = ErrorHandler()


def handle_errors(logger=None):
    """
    Декоратор для обработки ошибок в функциях

    Args:
        logger: Логгер для записи ошибок
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            handler = ErrorHandler(logger=logger)
            return handler.safe_execute(func, *args, **kwargs)

        return wrapper

    return decorator


def register_error_handler(handler: ErrorHandler):
    """
    Зарегистрировать глобальный обработчик ошибок

    Args:
        handler: Обработчик ошибок
    """
    global global_error_handler
    global_error_handler = handler
