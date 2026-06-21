"""
Модуль планировщика задач для Cognitive Agent
"""

from collections.abc import Callable
from typing import Any

# Абсолютные импорты для совместимости с тестами
try:
    from agents.cognitive_agent.common.base_logger import BaseLogger
    from agents.cognitive_agent.common.base_security import BaseSecurityChecker
    from agents.cognitive_agent.common.exceptions import TaskExecutionError, ValidationError
except ImportError:
    # Fallback для прямого запуска
    from ..common.base_logger import BaseLogger
    from ..common.base_security import BaseSecurityChecker
    from ..common.exceptions import TaskExecutionError

from .task_planner_enhanced import EnhancedTaskPlanner, TaskStatus


class TaskPlanner:
    """
    Планировщик задач для Cognitive Agent
    Поддерживает планирование и выполнение задач с учетом зависимостей
    """

    def __init__(self, logger: BaseLogger | None = None, security_checker: BaseSecurityChecker | None = None):
        """
        Инициализировать планировщик задач

        Args:
            logger: Логгер для записи событий
            security_checker: Проверяльщик безопасности
        """
        self.logger = logger or BaseLogger("TaskPlanner")
        self.security_checker = security_checker or BaseSecurityChecker()

        # Использовать улучшенный планировщик как основной движок
        self.enhanced_planner = EnhancedTaskPlanner(
            max_workers=5, logger=self.logger, security_checker=self.security_checker
        )

        self.logger.info("Планировщик задач инициализирован")

    def schedule_task(
        self,
        name: str,
        function: Callable,
        dependencies: list[str] | None = None,
        condition: Callable | None = None,
        priority: int = 0,
        timeout: int | None = None,
        max_retries: int = 0,
        rollback_function: Callable | None = None,
        *args,
        **kwargs,
    ) -> str:
        """
        Запланировать задачу

        Args:
            name: Имя задачи
            function: Функция для выполнения
            dependencies: Зависимости (ID задач, которые должны быть выполнены до этой)
            condition: Условие выполнения задачи
            priority: Приоритет задачи
            timeout: Таймаут выполнения
            max_retries: Максимальное количество повторных попыток
            rollback_function: Функция отката изменений
            *args: Аргументы для функции
            **kwargs: Ключевые аргументы для функции

        Returns:
            ID добавленной задачи
        """
        task_id = self.enhanced_planner.add_task(
            name=name,
            function=function,
            dependencies=dependencies,
            condition=condition,
            priority=priority,
            timeout=timeout,
            max_retries=max_retries,
            rollback_function=rollback_function,
            *args,
            **kwargs,
        )

        self.logger.debug(f"Задача запланирована: {name} (ID: {task_id})")
        return task_id

    def execute_plan(self, max_iterations: int = 100) -> dict[str, Any]:
        """
        Выполнить план задач

        Args:
            max_iterations: Максимальное количество итераций

        Returns:
            Результат выполнения плана
        """
        self.logger.info("Начало выполнения плана задач")

        try:
            result = self.enhanced_planner.execute_plan(max_iterations=max_iterations)

            # Выполнить откат для неудачных задач
            rollback_success = self.enhanced_planner.rollback_failed_tasks()
            result["rollback_success"] = rollback_success

            self.logger.info("План задач выполнен", **result)
            return result
        except Exception as e:
            self.logger.error(f"Ошибка при выполнении плана задач: {str(e)}")
            raise TaskExecutionError(
                f"Ошибка выполнения плана задач: {str(e)}", details={"max_iterations": max_iterations}
            )

    def get_task_status(self, task_id: str) -> str | None:
        """
        Получить статус задачи

        Args:
            task_id: ID задачи

        Returns:
            Статус задачи или None, если задача не найдена
        """
        status = self.enhanced_planner.get_task_status(task_id)
        return status.value if status else None

    def get_plan_status(self) -> dict[str, Any]:
        """
        Получить статус плана в целом

        Returns:
            Статус плана
        """
        return self.enhanced_planner.get_plan_status()

    def cancel_plan(self):
        """
        Отменить выполнение плана
        """
        self.enhanced_planner.cancel_plan()
        self.logger.info("План задач отменен")

    def clear_plan(self):
        """
        Очистить план и сбросить все задачи
        """
        self.enhanced_planner.clear_plan()
        self.logger.info("План задач очищен")

    def add_conditional_task(
        self,
        name: str,
        function: Callable,
        condition_func: Callable,
        dependencies: list[str] | None = None,
        *args,
        **kwargs,
    ) -> str:
        """
        Добавить задачу с условным выполнением

        Args:
            name: Имя задачи
            function: Функция для выполнения
            condition_func: Функция условия выполнения
            dependencies: Зависимости
            *args: Аргументы для функции
            **kwargs: Ключевые аргументы для функции

        Returns:
            ID добавленной задачи
        """
        return self.schedule_task(
            name=name, function=function, dependencies=dependencies, condition=condition_func, *args, **kwargs
        )

    def add_parallel_tasks(self, tasks_config: list[dict[str, Any]]) -> list[str]:
        """
        Добавить несколько задач для параллельного выполнения

        Args:
            tasks_config: Список конфигураций задач

        Returns:
            Список ID добавленных задач
        """
        task_ids = []
        for config in tasks_config:
            task_id = self.schedule_task(**config)
            task_ids.append(task_id)

        self.logger.debug(f"Добавлено {len(task_ids)} задач для параллельного выполнения")
        return task_ids

    def create_dependency_chain(self, tasks: list[dict[str, Any]]) -> list[str]:
        """
        Создать цепочку задач с последовательными зависимостями

        Args:
            tasks: Список конфигураций задач (каждая зависит от предыдущей)

        Returns:
            Список ID добавленных задач
        """
        task_ids = []
        prev_task_id = None

        for config in tasks:
            dependencies = [prev_task_id] if prev_task_id else []
            config_copy = config.copy()
            config_copy["dependencies"] = dependencies

            task_id = self.schedule_task(**config_copy)
            task_ids.append(task_id)
            prev_task_id = task_id

        self.logger.debug(f"Создана цепочка из {len(task_ids)} задач с зависимостями")
        return task_ids


# Экспортируем EnhancedTaskPlanner для прямого использования
__all__ = ["TaskPlanner", "EnhancedTaskPlanner", "TaskStatus"]
