"""
Улучшенный планировщик задач для Cognitive Agent
Поддерживает сложные зависимости, условные ветвления и параллельное выполнение задач
"""

import threading
import uuid
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

import networkx as nx

from ..common.base_logger import BaseLogger
from ..common.base_security import BaseSecurityChecker
from ..common.exceptions import ValidationError


class TaskStatus(Enum):
    """Статус задачи"""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"


@dataclass
class Task:
    """Представление задачи"""

    id: str
    name: str
    function: Callable
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    dependencies: list[str] = field(default_factory=list)  # ID задач, от которых зависит
    condition: Callable | None = None  # Условие выполнения
    priority: int = 0  # Приоритет (0 - самый высокий)
    timeout: int | None = None  # Таймаут в секундах
    max_retries: int = 0  # Максимальное количество повторных попыток
    rollback_function: Callable | None = None  # Функция отката изменений
    rollback_args: tuple = field(default_factory=tuple)
    rollback_kwargs: dict = field(default_factory=dict)

    status: TaskStatus = TaskStatus.PENDING
    result: Any | None = None
    error: Exception | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    retry_count: int = 0


class EnhancedTaskPlanner:
    """
    Улучшенный планировщик задач с поддержкой сложных зависимостей
    """

    def __init__(
        self,
        max_workers: int = 5,
        logger: BaseLogger | None = None,
        security_checker: BaseSecurityChecker | None = None,
    ):
        """
        Инициализировать улучшенный планировщик задач

        Args:
            max_workers: Максимальное количество параллельных рабочих
            logger: Логгер для записи событий
            security_checker: Проверяльщик безопасности
        """
        self.max_workers = max_workers
        self.logger = logger or BaseLogger("EnhancedTaskPlanner")
        self.security_checker = security_checker or BaseSecurityChecker()
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

        # Граф зависимостей задач
        self.dependency_graph = nx.DiGraph()

        # Словарь задач
        self.tasks: dict[str, Task] = {}

        # Результаты выполнения
        self.results: dict[str, Any] = {}

        # Блокировка для потокобезопасности
        self._lock = threading.RLock()

        self.logger.info("Улучшенный планировщик задач инициализирован", max_workers=max_workers)

    def add_task(
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
        Добавить задачу в планировщик

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
        task_id = str(uuid.uuid4())

        task = Task(
            id=task_id,
            name=name,
            function=function,
            args=args,
            kwargs=kwargs,
            dependencies=dependencies or [],
            condition=condition,
            priority=priority,
            timeout=timeout,
            max_retries=max_retries,
            rollback_function=rollback_function,
        )

        with self._lock:
            self.tasks[task_id] = task
            self.dependency_graph.add_node(task_id, task=task)

            # Добавить ребра зависимостей
            for dep_id in task.dependencies:
                if dep_id in self.tasks:
                    self.dependency_graph.add_edge(dep_id, task_id)
                else:
                    self.logger.warning(f"Зависимость {dep_id} не найдена для задачи {task_id}")

        self.logger.debug(
            f"Добавлена задача: {name} (ID: {task_id})", dependencies=task.dependencies, priority=priority
        )

        return task_id

    def remove_task(self, task_id: str) -> bool:
        """
        Удалить задачу из планировщика

        Args:
            task_id: ID задачи для удаления

        Returns:
            Успешно ли удалена
        """
        with self._lock:
            if task_id not in self.tasks:
                return False

            # Удалить задачу из графа
            self.dependency_graph.remove_node(task_id)

            # Удалить все зависимости от этой задачи
            for node in list(self.dependency_graph.nodes):
                if task_id in [edge[0] for edge in self.dependency_graph.in_edges(node)]:
                    self.dependency_graph.remove_edge(task_id, node)

            # Удалить из словаря задач
            del self.tasks[task_id]

            self.logger.debug(f"Удалена задача: {task_id}")
            return True

    def _validate_dependency_graph(self) -> bool:
        """
        Проверить граф зависимостей на наличие циклов

        Returns:
            Валиден ли граф
        """
        try:
            # Проверить, есть ли циклы в графе
            cycles = list(nx.simple_cycles(self.dependency_graph))
            if cycles:
                self.logger.error("Обнаружены циклы в графе зависимостей", cycles=cycles)
                return False

            # Проверить, все ли зависимости существуют
            for task_id, task in self.tasks.items():
                for dep_id in task.dependencies:
                    if dep_id not in self.tasks:
                        self.logger.error(f"Зависимость {dep_id} не найдена для задачи {task_id}")
                        return False

            return True
        except Exception as e:
            self.logger.error(f"Ошибка при проверке графа зависимостей: {str(e)}")
            return False

    def _get_ready_tasks(self) -> list[Task]:
        """
        Получить список задач, готовых к выполнению

        Returns:
            Список готовых к выполнению задач
        """
        ready_tasks = []

        for task_id, task in self.tasks.items():
            if task.status != TaskStatus.PENDING:
                continue

            # Проверить, выполнены ли все зависимости
            all_deps_satisfied = True
            for dep_id in task.dependencies:
                dep_task = self.tasks.get(dep_id)
                if not dep_task or dep_task.status != TaskStatus.SUCCESS:
                    all_deps_satisfied = False
                    break

            # Проверить условие выполнения
            condition_met = True
            if task.condition:
                try:
                    condition_met = task.condition(self.results)
                except Exception as e:
                    self.logger.error(f"Ошибка при проверке условия для задачи {task_id}: {str(e)}")
                    condition_met = False

            if all_deps_satisfied and condition_met:
                ready_tasks.append(task)

        # Сортировать по приоритету (меньше число - выше приоритет)
        ready_tasks.sort(key=lambda t: t.priority)

        return ready_tasks

    def _execute_task(self, task: Task) -> bool:
        """
        Выполнить одну задачу

        Args:
            task: Задача для выполнения

        Returns:
            Успешно ли выполнена
        """
        task.start_time = datetime.now()
        task.status = TaskStatus.RUNNING

        self.logger.info(f"Начало выполнения задачи: {task.name} (ID: {task.id})")

        try:
            # Выполнить задачу
            if task.timeout:
                # Для задач с таймаутом использовать asyncio
                future = self.executor.submit(task.function, *task.args, **task.kwargs)
                result = future.result(timeout=task.timeout)
            else:
                result = task.function(*task.args, **task.kwargs)

            task.result = result
            task.status = TaskStatus.SUCCESS

            # Сохранить результат
            self.results[task.id] = result

            self.logger.info(f"Задача выполнена успешно: {task.name} (ID: {task.id})")
            return True

        except Exception as e:
            task.error = e
            task.status = TaskStatus.FAILED

            self.logger.error(f"Ошибка выполнения задачи {task.name} (ID: {task.id}): {str(e)}")

            # Попробовать выполнить повторную попытку, если доступна
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                task.status = TaskStatus.PENDING  # Сбросить статус для повторной попытки
                self.logger.info(
                    f"Планируется повторная попытка для задачи {task.name} (попытка {task.retry_count}/{task.max_retries})"
                )
                return False
            else:
                return False
        finally:
            task.end_time = datetime.now()

    def execute_plan(self, max_iterations: int = 100) -> dict[str, Any]:
        """
        Выполнить план задач

        Args:
            max_iterations: Максимальное количество итераций

        Returns:
            Результат выполнения плана
        """
        # Проверить валидность графа зависимостей
        if not self._validate_dependency_graph():
            raise ValidationError(
                "Граф зависимостей невалиден",
                details={"tasks_count": len(self.tasks), "graph_nodes": len(self.dependency_graph.nodes)},
            )

        iteration = 0
        completed_tasks = 0
        total_tasks = len(self.tasks)

        self.logger.info(f"Начало выполнения плана из {total_tasks} задач")

        while completed_tasks < total_tasks and iteration < max_iterations:
            iteration += 1

            # Получить готовые к выполнению задачи
            ready_tasks = self._get_ready_tasks()

            if not ready_tasks:
                # Если нет готовых задач, но не все выполнены - возможно, есть цикл или нерешаемые зависимости
                pending_tasks = [t for t in self.tasks.values() if t.status == TaskStatus.PENDING]
                if pending_tasks:
                    self.logger.warning(f"Нет готовых задач, но остались ожидающие: {[t.name for t in pending_tasks]}")
                    break
                else:
                    break

            # Выполнить готовые задачи (параллельно)
            futures = []
            for task in ready_tasks:
                future = self.executor.submit(self._execute_task, task)
                futures.append((task, future))

            # Дождаться завершения задач
            for task, future in futures:
                try:
                    success = future.result()
                    if success:
                        completed_tasks += 1
                except Exception as e:
                    self.logger.error(f"Ошибка при выполнении задачи {task.name}: {str(e)}")
                    task.status = TaskStatus.FAILED
                    task.error = e

            self.logger.debug(f"Итерация {iteration}: выполнено {completed_tasks}/{total_tasks} задач")

        # Подготовить результат
        successful_tasks = [t for t in self.tasks.values() if t.status == TaskStatus.SUCCESS]
        failed_tasks = [t for t in self.tasks.values() if t.status == TaskStatus.FAILED]
        cancelled_tasks = [t for t in self.tasks.values() if t.status in [TaskStatus.CANCELLED, TaskStatus.SKIPPED]]

        result = {
            "completed": completed_tasks,
            "total": total_tasks,
            "successful_tasks": len(successful_tasks),
            "failed_tasks": len(failed_tasks),
            "cancelled_tasks": len(cancelled_tasks),
            "results": self.results.copy(),
            "execution_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "iterations_used": iteration,
        }

        if failed_tasks:
            result["failed_task_details"] = [{"id": t.id, "name": t.name, "error": str(t.error)} for t in failed_tasks]

        self.logger.info(f"План выполнен: {completed_tasks}/{total_tasks} задач", **result)
        return result

    def rollback_failed_tasks(self) -> bool:
        """
        Выполнить откат изменений для неудачных задач

        Returns:
            Успешно ли выполнен откат
        """
        failed_tasks = [t for t in self.tasks.values() if t.status == TaskStatus.FAILED and t.rollback_function]

        if not failed_tasks:
            self.logger.info("Нет неудачных задач с функцией отката")
            return True

        self.logger.info(f"Выполнение отката для {len(failed_tasks)} задач")

        rollback_success = True
        for task in failed_tasks:
            try:
                task.rollback_function(*task.rollback_args, **task.rollback_kwargs)
                self.logger.info(f"Откат выполнен для задачи: {task.name}")
            except Exception as e:
                self.logger.error(f"Ошибка при откате задачи {task.name}: {str(e)}")
                rollback_success = False

        return rollback_success

    def get_task_status(self, task_id: str) -> TaskStatus | None:
        """
        Получить статус задачи

        Args:
            task_id: ID задачи

        Returns:
            Статус задачи или None, если задача не найдена
        """
        task = self.tasks.get(task_id)
        return task.status if task else None

    def get_plan_status(self) -> dict[str, Any]:
        """
        Получить статус плана в целом

        Returns:
            Статус плана
        """
        total_tasks = len(self.tasks)
        successful_tasks = len([t for t in self.tasks.values() if t.status == TaskStatus.SUCCESS])
        failed_tasks = len([t for t in self.tasks.values() if t.status == TaskStatus.FAILED])
        pending_tasks = len([t for t in self.tasks.values() if t.status == TaskStatus.PENDING])
        running_tasks = len([t for t in self.tasks.values() if t.status == TaskStatus.RUNNING])

        return {
            "total_tasks": total_tasks,
            "successful_tasks": successful_tasks,
            "failed_tasks": failed_tasks,
            "pending_tasks": pending_tasks,
            "running_tasks": running_tasks,
            "completion_percentage": successful_tasks / total_tasks * 100 if total_tasks > 0 else 0,
            "status": "completed" if pending_tasks == 0 and running_tasks == 0 else "in_progress",
        }

    def cancel_plan(self):
        """
        Отменить выполнение плана
        """
        with self._lock:
            for task in self.tasks.values():
                if task.status in [TaskStatus.PENDING, TaskStatus.RUNNING]:
                    task.status = TaskStatus.CANCELLED
                    self.logger.info(f"Задача отменена: {task.name} (ID: {task.id})")

        self.logger.info("План отменен")

    def clear_plan(self):
        """
        Очистить план и сбросить все задачи
        """
        with self._lock:
            self.tasks.clear()
            self.results.clear()
            self.dependency_graph.clear()

        self.logger.info("План очищен")
