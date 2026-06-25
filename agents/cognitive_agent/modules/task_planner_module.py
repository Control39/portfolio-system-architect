"""
Модуль планировщика задач для Cognitive Agent
Часть модульного рефакторинга autonomous_agent.py
"""

import asyncio
import json
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any


class TaskPlanner:
    """
    Планировщик задач для управления асинхронными операциями
    """

    def __init__(self):
        self.tasks = {}  # id -> task definition
        self.task_queue = asyncio.Queue()
        self.completed_tasks = {}
        self.failed_tasks = {}
        self.running_tasks = set()
        self.task_counter = 0
        self.dependencies = {}  # task_id -> [dependency_ids]
        self.task_graph = {}  # task_id -> {definition}
        self.lock = threading.Lock()
        self._queue_file = ".agent_data/task_queue.json"
        Path(self._queue_file).parent.mkdir(parents=True, exist_ok=True)

    async def add_task(self, task_id: str, task_details: dict, dependencies: list[str] = None) -> dict[str, Any]:
        """
        Добавить новую задачу в планировщик

        Args:
            task_id: Уникальный идентификатор задачи
            task_details: Детали задачи (тип, параметры и т.д.)
            dependencies: Список ID задач, от которых зависит эта задача

        Returns:
            Словарь с информацией о добавленной задаче
        """
        with self.lock:
            # Проверяем уникальность ID
            if task_id in self.tasks:
                raise ValueError(f"Task with ID {task_id} already exists")

            task_definition = {
                "id": task_id,
                "type": task_details.get("type", "generic"),
                "status": "pending",
                "created_at": datetime.now().isoformat(),
                "params": task_details.get("params", {}),
                "attempts": 0,
                "max_attempts": task_details.get("max_attempts", 3),
                "priority": task_details.get("priority", 5),
                "dependencies": dependencies or [],
            }

            # Добавляем задачу в очередь, если нет зависимостей или все зависимости выполнены
            await self._enqueue_task_if_ready(task_definition)

            # Сохраняем определение задачи
            self.task_graph[task_id] = task_definition
            self.tasks[task_id] = task_definition

            # Устанавливаем зависимости
            if dependencies:
                self.dependencies[task_id] = dependencies

            # Сохраняем очередь задач
            await self._save_queue()

            return {
                "id": task_id,
                "status": "added",
                "type": task_definition["type"],
                "dependencies": dependencies or [],
            }

    async def create_task(self, task_type: str, priority: int = 5, **kwargs) -> dict[str, Any]:
        """
        Создать новую задачу с автоматическим ID

        Args:
            task_type: Тип задачи (например, "scan", "analyze", "process")
            priority: Приоритет задачи (1-10)
            **kwargs: Дополнительные параметры задачи

        Returns:
            Словарь с информацией о созданной задаче
        """
        task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{self.task_counter}"
        self.task_counter += 1

        task_details = {"type": task_type, "params": kwargs, "priority": priority}

        return await self.add_task(task_id, task_details)

    async def _enqueue_task_if_ready(self, task_def: dict[str, Any]):
        """Поместить задачу в очередь, если она готова к выполнению"""
        task_id = task_def["id"]

        # Проверяем зависимости
        deps = self.dependencies.get(task_id, [])
        all_deps_completed = all(dep_id in self.completed_tasks for dep_id in deps)

        # Если нет незавершенных зависимостей, помещаем в очередь
        if not deps or all_deps_completed:
            await self.task_queue.put((task_def["priority"], task_id, task_def))
            task_def["status"] = "queued"

    async def execute_task_queue(self, max_concurrent: int = 3):
        """
        Выполнить очередь задач с ограничением на одновременное выполнение

        Args:
            max_concurrent: Максимальное количество одновременно выполняемых задач
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def execute_single_task(priority, task_id, task_def):
            async with semaphore:
                return await self._execute_task(task_id, task_def)

        tasks = []
        while not self.task_queue.empty():
            try:
                priority, task_id, task_def = self.task_queue.get_nowait()
                task_coro = execute_single_task(priority, task_id, task_def)
                tasks.append(asyncio.create_task(task_coro))
            except asyncio.QueueEmpty:
                break

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _execute_task(self, task_id: str, task_definition: dict[str, Any]) -> bool:
        """
        Выполнить одну задачу

        Args:
            task_id: Идентификатор задачи
            task_definition: Определение задачи

        Returns:
            Успешность выполнения
        """
        if task_id in self.running_tasks:
            return False

        try:
            self.running_tasks.add(task_id)
            self.tasks[task_id]["status"] = "running"
            self.tasks[task_id]["started_at"] = datetime.now().isoformat()

            # Выполняем задачу в зависимости от типа
            success = await self._run_task_by_type(task_id, task_definition)

            if success:
                self.tasks[task_id]["status"] = "completed"
                self.tasks[task_id]["completed_at"] = datetime.now().isoformat()
                self.completed_tasks[task_id] = self.tasks[task_id]
            else:
                self.tasks[task_id]["status"] = "failed"
                self.tasks[task_id]["failed_at"] = datetime.now().isoformat()
                self.failed_tasks[task_id] = self.tasks[task_id]

            return success

        except Exception as e:
            self.tasks[task_id]["status"] = "failed"
            self.tasks[task_id]["error"] = str(e)
            self.tasks[task_id]["failed_at"] = datetime.now().isoformat()
            self.failed_tasks[task_id] = self.tasks[task_id]
            return False

        finally:
            self.running_tasks.discard(task_id)
            await self._save_queue()

    async def _run_task_by_type(self, task_id: str, task_definition: dict[str, Any]) -> bool:
        """
        Выполнить задачу в зависимости от её типа

        Args:
            task_id: Идентификатор задачи
            task_definition: Определение задачи

        Returns:
            Успешность выполнения
        """
        task_type = task_definition["type"]
        params = task_definition["params"]

        try:
            if task_type == "scan":
                return await self._run_scan_task(params)
            elif task_type == "analyze":
                return await self._run_analysis_task(params)
            elif task_type == "process":
                return await self._run_process_task(params)
            elif task_type == "maintenance":
                return await self._run_maintenance_task(params)
            else:
                # Обработка произвольной задачи
                return await self._run_generic_task(task_type, params)

        except Exception as e:
            print(f"Error executing task {task_id}: {e}")
            return False

    async def _run_scan_task(self, params: dict[str, Any]) -> bool:
        """Выполнить задачу сканирования"""
        from .project_scanner_module import ProjectScanner

        path = params.get("path", ".")
        depth = params.get("depth", 3)
        scan_mode = params.get("mode", "auto")
        task_id = params.get("task_id", "unknown")

        scanner = ProjectScanner(scan_depth=depth)
        result = await scanner.scan_project(path, scan_mode=scan_mode)

        # Сохраняем результат сканирования
        scan_result_file = f".agent_data/scan_results/{task_id}_result.json"
        Path(scan_result_file).parent.mkdir(parents=True, exist_ok=True)

        with open(scan_result_file, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        return True

    async def _run_analysis_task(self, params: dict[str, Any]) -> bool:
        """Выполнить задачу анализа"""
        # Здесь будет логика анализа в зависимости от параметров
        analysis_type = params.get("analysis_type", "general")

        # Заглушка для анализа
        print(f"Running {analysis_type} analysis with params: {params}")
        await asyncio.sleep(1)  # Имитация работы

        return True

    async def _run_process_task(self, params: dict[str, Any]) -> bool:
        """Выполнить задачу обработки"""
        # Здесь будет логика обработки
        process_type = params.get("process_type", "general")

        print(f"Running {process_type} process with params: {params}")
        await asyncio.sleep(1)  # Имитация работы

        return True

    async def _run_maintenance_task(self, params: dict[str, Any]) -> bool:
        """Выполнить задачу обслуживания"""
        # Очистка старых файлов, логов и т.д.
        cleanup_dirs = params.get("directories", [])
        days_old = params.get("days_old", 7)

        cutoff_time = time.time() - (days_old * 24 * 60 * 60)

        for dir_path in cleanup_dirs:
            if Path(dir_path).exists():
                for file_path in Path(dir_path).rglob("*"):
                    if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                        try:
                            file_path.unlink()
                            print(f"Cleaned up old file: {file_path}")
                        except Exception as e:
                            print(f"Could not clean file {file_path}: {e}")

        return True

    async def _run_generic_task(self, task_type: str, params: dict[str, Any]) -> bool:
        """Выполнить общую задачу"""
        print(f"Running generic task {task_type} with params: {params}")
        await asyncio.sleep(1)  # Имитация работы
        return True

    async def _save_queue(self):
        """Сохранить состояние очереди задач"""
        queue_state = {
            "tasks": self.tasks,
            "completed_tasks": self.completed_tasks,
            "failed_tasks": self.failed_tasks,
            "running_tasks": list(self.running_tasks),
            "task_counter": self.task_counter,
            "dependencies": self.dependencies,
            "task_graph": self.task_graph,
        }

        with open(self._queue_file, "w", encoding="utf-8") as f:
            json.dump(queue_state, f, ensure_ascii=False, indent=2)

    async def load_queue(self):
        """Загрузить состояние очереди задач"""
        try:
            if Path(self._queue_file).exists():
                with open(self._queue_file, encoding="utf-8") as f:
                    queue_state = json.load(f)

                self.tasks = queue_state.get("tasks", {})
                self.completed_tasks = queue_state.get("completed_tasks", {})
                self.failed_tasks = queue_state.get("failed_tasks", {})
                self.running_tasks = set(queue_state.get("running_tasks", []))
                self.task_counter = queue_state.get("task_counter", 0)
                self.dependencies = queue_state.get("dependencies", {})
                self.task_graph = queue_state.get("task_graph", {})

                # Восстанавливаем очередь задач из сохраненного состояния
                for task_id, task_def in self.tasks.items():
                    if task_def["status"] in ["pending", "queued"]:
                        priority = task_def.get("priority", 5)
                        await self.task_queue.put((priority, task_id, task_def))
        except Exception as e:
            print(f"Error loading queue: {e}")

    def get_task_status(self, task_id: str) -> dict[str, Any]:
        """Получить статус задачи"""
        if task_id in self.tasks:
            return self.tasks[task_id]
        elif task_id in self.completed_tasks:
            return self.completed_tasks[task_id]
        elif task_id in self.failed_tasks:
            return self.failed_tasks[task_id]
        else:
            return {"error": "Task not found"}

    def get_queue_stats(self) -> dict[str, int]:
        """Получить статистику очереди задач"""
        return {
            "total_tasks": len(self.tasks),
            "completed_tasks": len(self.completed_tasks),
            "failed_tasks": len(self.failed_tasks),
            "running_tasks": len(self.running_tasks),
            "queued_tasks": self.task_queue.qsize(),
        }

    def get_pending_tasks(self) -> list[str]:
        """Получить список ожидающих задач"""
        return [task_id for task_id, task_def in self.tasks.items() if task_def["status"] in ["pending", "queued"]]

    def cancel_task(self, task_id: str) -> bool:
        """Отменить задачу"""
        if task_id in self.tasks:
            if task_id in self.running_tasks:
                # Нельзя отменить уже запущенную задачу
                return False

            self.tasks[task_id]["status"] = "cancelled"
            self.tasks[task_id]["cancelled_at"] = datetime.now().isoformat()

            # Удаляем из очереди, если там есть
            # Это требует специальной логики, т.к. нельзя удалить из asyncio.Queue
            # Пока просто помечаем как отменённые

            return True
        return False
