"""
Базовые расширения для BaseCognitiveAgent
"""

import threading
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any

from .base_logger import BaseLogger
from .base_scanner import BaseProjectScanner
from .base_security import BaseSecurityChecker
from .cache_manager import get_cache_manager
from .exceptions import CacheError, ConfigurationError, DataProcessingError, ErrorHandler, ValidationError
from .memory_manager import get_memory_manager, with_memory_limit
from .pattern_analyzer import AdaptiveLearningSystem


class BaseAgentExtensions:
    """
    Базовые расширения для BaseCognitiveAgent
    Содержит общие компоненты, которые могут использоваться как в Standard, так и в Enterprise версиях
    """

    def __init__(
        self, project_path: str, logger: BaseLogger | None = None, security_checker: BaseSecurityChecker | None = None
    ):
        """
        Инициализировать базовые расширения агента

        Args:
            project_path: Путь к проекту
            logger: Логгер (опционально)
            security_checker: Проверяльщик безопасности (опционально)
        """
        try:
            self.project_path = Path(project_path).resolve()
            if not self.project_path.exists():
                raise ConfigurationError(
                    f"Путь проекта не существует: {project_path}", details={"project_path": project_path}
                )
        except Exception as e:
            raise ConfigurationError(
                f"Ошибка инициализации расширений агента: {str(e)}", details={"project_path": project_path}
            )

        self.logger = logger or BaseLogger("BaseAgentExtensions")
        self.security_checker = security_checker or BaseSecurityChecker()

        # Инициализировать сканер проекта
        try:
            self.project_scanner = BaseProjectScanner(project_path=project_path, security_checker=self.security_checker)
        except Exception as e:
            raise ConfigurationError(
                f"Ошибка инициализации сканера проекта: {str(e)}", details={"project_path": project_path}
            )

        # История решений
        self.decision_history = []

        # Кэш для оптимизации - теперь используем улучшенный кэш
        self.cache_manager = get_cache_manager()
        self.project_cache = self.cache_manager.get_project_cache()
        self.file_cache = self.cache_manager.get_file_cache()
        self.ai_response_cache = self.cache_manager.get_ai_response_cache()

        # Менеджер памяти
        self.memory_manager = get_memory_manager()

        # Система адаптивного обучения
        self.adaptive_learning_system = AdaptiveLearningSystem(logger=self.logger)

        # Зарегистрировать callback для очистки кэша при необходимости
        self.memory_manager.register_cleanup_callback(self._perform_cache_cleanup)

        # Флаги состояния
        self.initialized = False

        # Обработчик ошибок
        self.error_handler = ErrorHandler(logger=self.logger)

    def _perform_cache_cleanup(self):
        """
        Выполнить очистку кэша как часть очистки памяти
        """
        self.logger.debug("Выполнение очистки кэша в рамках очистки памяти")

        # Очистить устаревшие элементы из кэшей
        self.project_cache._cleanup_expired()
        self.file_cache._cleanup_expired()
        self.ai_response_cache._cleanup_expired()

    def initialize(self):
        """
        Инициализировать компоненты расширений
        """
        if self.initialized:
            return

        self.logger.info("Инициализация базовых расширений агента", project_path=str(self.project_path))

        # Здесь можно добавить дополнительную инициализацию
        self.initialized = True

    @with_memory_limit(max_memory_mb=50)  # Ограничение 50MB для этой операции
    def get_project_context(self, scan_mode: str = "auto") -> dict[str, Any]:
        """
        Получить контекст проекта через сканирование

        Args:
            scan_mode: Режим сканирования

        Returns:
            Контекст проекта
        """
        try:
            # Попробовать получить из кэша
            cache_key = f"project_context_{self.project_path}_{scan_mode}"
            cached_result = self.project_cache.get(cache_key)

            if cached_result is not None:
                self.logger.debug("Контекст проекта получен из кэша", cache_key=cache_key)
                return cached_result

            self.logger.info("Получение контекста проекта", scan_mode=scan_mode)

            # Выполнить сканирование проекта
            scan_results = self.project_scanner.scan(mode=scan_mode)

            # Добавить дополнительную информацию в контекст
            context = {
                "scan_results": scan_results,
                "timestamp": datetime.now().isoformat(),
                "project_hash": self.project_scanner.calculate_project_hash(),
                "context_type": "project_analysis",
            }

            # Сохранить в кэш
            success = self.project_cache.set(cache_key, context)
            if success:
                self.logger.debug("Контекст проекта сохранен в кэш", cache_key=cache_key)
            else:
                self.logger.warning("Не удалось сохранить контекст проекта в кэш", cache_key=cache_key)

            return context
        except Exception as e:
            raise DataProcessingError(
                f"Ошибка получения контекста проекта: {str(e)}",
                details={"scan_mode": scan_mode, "project_path": str(self.project_path)},
            )

    def remember_decision(self, context: dict[str, Any], decision: str, outcome: str):
        """
        Запомнить решение и его результат для будущего обучения

        Args:
            context: Контекст принятия решения
            decision: Принятое решение
            outcome: Результат (success, failed, cancelled)
        """
        try:
            decision_record = {
                "context": context,
                "decision": decision,
                "outcome": outcome,
                "timestamp": datetime.now().isoformat(),
            }

            self.decision_history.append(decision_record)

            # Ограничиваем историю 100 записями
            if len(self.decision_history) > 100:
                self.decision_history = self.decision_history[-100:]

            # Обновляем success rate
            success_count = sum(1 for d in self.decision_history if d["outcome"] == "success")
            success_rate = success_count / len(self.decision_history) if self.decision_history else 0.0

            self.logger.info(
                "Решение запомнено",
                decision=decision,
                outcome=outcome,
                success_rate=success_rate,
                history_length=len(self.decision_history),
            )

            # Обучить систему на этом решении
            self.adaptive_learning_system.learn_from_decision(context, decision, outcome)

        except Exception as e:
            raise DataProcessingError(
                f"Ошибка запоминания решения: {str(e)}", details={"decision": decision, "outcome": outcome}
            )

    def get_success_rate(self) -> float:
        """
        Получить текущий success rate

        Returns:
            Success rate в диапазоне [0, 1]
        """
        try:
            if not self.decision_history:
                return 0.0

            success_count = sum(1 for d in self.decision_history if d["outcome"] == "success")
            return success_count / len(self.decision_history)
        except ZeroDivisionError:
            # Обработка случая, когда denominator равен нулю
            return 0.0
        except Exception as e:
            raise DataProcessingError(
                f"Ошибка вычисления success rate: {str(e)}", details={"history_length": len(self.decision_history)}
            )

    def validate_task_context(self, task_context: dict[str, Any]) -> tuple[bool, str]:
        """
        Проверить контекст задачи на безопасность и корректность

        Args:
            task_context: Контекст задачи

        Returns:
            Кортеж (валидно ли, сообщение)
        """
        try:
            # Проверить на наличие критических полей
            required_fields = ["task_description", "project_path"]
            for field in required_fields:
                if field not in task_context:
                    return False, f"Отсутствует обязательное поле: {field}"

            # Проверить путь проекта
            project_path = Path(task_context["project_path"])
            is_safe, message = self.security_checker.validate_path(str(project_path))
            if not is_safe:
                return False, message

            # Проверить описание задачи на опасные паттерны
            task_desc = task_context.get("task_description", "")
            is_safe, message = self.security_checker.validate_code(task_desc)
            if not is_safe:
                return False, message

            return True, "Контекст задачи валиден"
        except Exception as e:
            raise ValidationError(
                f"Ошибка валидации контекста задачи: {str(e)}",
                details={
                    "task_context_keys": list(task_context.keys())
                    if isinstance(task_context, dict)
                    else type(task_context)
                },
            )

    def get_cached_result(self, key: str) -> Any | None:
        """
        Получить результат из кэша

        Args:
            key: Ключ кэша

        Returns:
            Закэшированный результат или None
        """
        try:
            # Попробовать получить из кэша ответов ИИ
            cached_item = self.ai_response_cache.get(key)
            if cached_item is not None:
                self.logger.debug("Результат получен из кэша", cache_key=key)
                return cached_item

            # Попробовать получить из общего кэша файлов
            cached_item = self.file_cache.get(key)
            if cached_item is not None:
                self.logger.debug("Результат получен из кэша файлов", cache_key=key)
                return cached_item

            # Попробовать получить из кэша проекта
            cached_item = self.project_cache.get(key)
            if cached_item is not None:
                self.logger.debug("Результат получен из кэша проекта", cache_key=key)
                return cached_item

            self.logger.debug("Результат не найден в кэше", cache_key=key)
            return None
        except Exception as e:
            raise CacheError(f"Ошибка получения результата из кэша: {str(e)}", details={"cache_key": key})

    def cache_result(self, key: str, result: Any, ttl: int = 3600):
        """
        Закэшировать результат

        Args:
            key: Ключ кэша
            result: Результат для кэширования
            ttl: Время жизни в секундах (по умолчанию 1 час)
        """
        try:
            # Попробовать закэшировать в кэш ответов ИИ
            success = self.ai_response_cache.set(key, result)
            if success:
                self.logger.debug("Результат сохранен в кэш ИИ", cache_key=key)
            else:
                # Если не удалось в основной кэш, попробовать кэш файлов
                success = self.file_cache.set(key, result)
                if success:
                    self.logger.debug("Результат сохранен в кэш файлов", cache_key=key)
                else:
                    # Если не удалось нигде сохранить, просто логировать
                    self.logger.warning("Не удалось сохранить результат в кэш", cache_key=key)
        except Exception as e:
            raise CacheError(f"Ошибка кэширования результата: {str(e)}", details={"cache_key": key})

    def _cleanup_expired_cache(self):
        """
        Удалить устаревшие записи из кэша
        """
        # Устаревшие записи автоматически удаляются в MemoryAwareCache
        # при обращении к ним или при принудительной очистке
        pass

    def run_with_timeout(self, func: Callable, timeout: int = 30, *args, **kwargs) -> Any:
        """
        Выполнить функцию с таймаутом

        Args:
            func: Функция для выполнения
            timeout: Таймаут в секундах
            *args: Аргументы для функции
            **kwargs: Ключевые аргументы для функции

        Returns:
            Результат выполнения функции
        """

        def target(result_container, error_container):
            try:
                result_container[0] = func(*args, **kwargs)
            except Exception as e:
                error_container[0] = e

        result_container = [None]
        error_container = [None]

        thread = threading.Thread(target=target, args=(result_container, error_container))
        thread.daemon = True
        thread.start()
        thread.join(timeout)

        if thread.is_alive():
            raise TimeoutError(f"Функция не завершилась за {timeout} секунд")

        if error_container[0]:
            raise error_container[0]

        return result_container[0]

    def prepare_agent_state(self, initial_context: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        Подготовить начальное состояние агента

        Args:
            initial_context: Начальный контекст (опционально)

        Returns:
            Подготовленное состояние агента
        """
        try:
            state = {
                "initialized_at": datetime.now().isoformat(),
                "decision_history": self.decision_history,
                "project_context": self.get_project_context(),
                "success_rate": self.get_success_rate(),
                "extensions_version": "1.0.0",
            }

            if initial_context:
                state.update(initial_context)

            self.logger.info("Состояние агента подготовлено", state_size=len(state))
            return state
        except Exception as e:
            raise DataProcessingError(
                f"Ошибка подготовки состояния агента: {str(e)}",
                details={"has_initial_context": initial_context is not None},
            )

    def execute_with_error_handling(
        self, func: Callable, *args, error_context: dict[str, Any] | None = None, **kwargs
    ) -> Any:
        """
        Выполнить функцию с обработкой ошибок

        Args:
            func: Функция для выполнения
            *args: Аргументы для функции
            error_context: Контекст ошибки
            **kwargs: Ключевые аргументы для функции

        Returns:
            Результат выполнения функции
        """
        return self.error_handler.safe_execute(func, *args, error_context=error_context, **kwargs)

    def get_memory_usage(self) -> dict[str, Any]:
        """
        Получить информацию об использовании памяти кэшами

        Returns:
            Словарь с информацией об использовании памяти
        """
        cache_memory_info = self.cache_manager.monitor_memory_usage()
        memory_manager_info = self.memory_manager.get_memory_status()

        return {"cache_memory": cache_memory_info, "memory_manager": memory_manager_info}

    def check_and_manage_memory(self) -> bool:
        """
        Проверить использование памяти и выполнить управление при необходимости

        Returns:
            Требовалось ли управление памятью
        """
        return self.memory_manager.check_memory_usage()

    def get_learning_advice(self, context: dict[str, Any], decision: str) -> dict[str, Any]:
        """
        Получить совет по принятию решения на основе исторических данных

        Args:
            context: Контекст принятия решения
            decision: Решение для оценки

        Returns:
            Совет по решению
        """
        return self.adaptive_learning_system.get_advice_for_decision(context, decision)

    def get_learning_metrics(self) -> dict[str, Any]:
        """
        Получить метрики обучения

        Returns:
            Метрики обучения системы
        """
        return self.adaptive_learning_system.get_learning_metrics()
