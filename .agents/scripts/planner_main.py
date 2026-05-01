#!/usr/bin/env python3
"""
Основной скрипт планировщика задач для Cognitive Automation Agent.
Выполняет планирование, приоритизацию и оптимизацию задач.
"""

import json
import logging
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List

import yaml

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(".agents/logs/planner.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class TaskPlanner:
    """Планировщик задач для оптимизации и приоритизации"""

    def __init__(self, config_path: str = ".agents/config/planner.yaml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.tasks = []
        self.schedule = {}

    def _load_config(self) -> Dict[str, Any]:
        """Загрузка конфигурации планировщика"""
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            logger.error(f"Ошибка загрузки конфигурации: {e}")
            return {}

    def load_tasks(self, tasks_file: str = ".agents/data/tasks.json") -> List[Dict[str, Any]]:
        """Загрузка задач из файла"""
        try:
            tasks_path = Path(tasks_file)
            if tasks_path.exists():
                with open(tasks_path, "r", encoding="utf-8") as f:
                    self.tasks = json.load(f)
                logger.info(f"Загружено {len(self.tasks)} задач")
            else:
                logger.warning(f"Файл задач не найден: {tasks_file}")
                self.tasks = self._generate_sample_tasks()
        except Exception as e:
            logger.error(f"Ошибка загрузки задач: {e}")
            self.tasks = self._generate_sample_tasks()

        return self.tasks

    def _generate_sample_tasks(self) -> List[Dict[str, Any]]:
        """Генерация примерных задач для демонстрации"""
        sample_tasks = [
            {
                "id": "task_001",
                "title": "Настройка CI/CD пайплайна",
                "description": "Настройка автоматической сборки и деплоя",
                "priority": 0.9,
                "urgency": 0.8,
                "complexity": 0.7,
                "estimated_duration": 120,  # минуты
                "dependencies": [],
                "resources": ["ci_cd", "docker"],
                "category": "devops",
            },
            {
                "id": "task_002",
                "title": "Рефакторинг модуля аутентификации",
                "description": "Улучшение безопасности и производительности",
                "priority": 0.8,
                "urgency": 0.6,
                "complexity": 0.8,
                "estimated_duration": 180,
                "dependencies": [],
                "resources": ["backend", "security"],
                "category": "development",
            },
            {
                "id": "task_003",
                "title": "Добавление тестового покрытия",
                "description": "Увеличение покрытия тестами до 80%",
                "priority": 0.7,
                "urgency": 0.5,
                "complexity": 0.6,
                "estimated_duration": 240,
                "dependencies": ["task_002"],
                "resources": ["testing", "qa"],
                "category": "testing",
            },
            {
                "id": "task_004",
                "title": "Оптимизация производительности базы данных",
                "description": "Настройка индексов и запросов",
                "priority": 0.6,
                "urgency": 0.4,
                "complexity": 0.9,
                "estimated_duration": 150,
                "dependencies": [],
                "resources": ["database", "backend"],
                "category": "optimization",
            },
            {
                "id": "task_005",
                "title": "Обновление документации",
                "description": "Актуализация README и API документации",
                "priority": 0.5,
                "urgency": 0.3,
                "complexity": 0.3,
                "estimated_duration": 90,
                "dependencies": ["task_001", "task_002"],
                "resources": ["documentation"],
                "category": "documentation",
            },
        ]

        logger.info(f"Сгенерировано {len(sample_tasks)} примерных задач")
        return sample_tasks

    def prioritize_tasks(self) -> List[Dict[str, Any]]:
        """Приоритизация задач на основе конфигурации"""
        logger.info("Приоритизация задач...")

        if not self.tasks:
            logger.warning("Нет задач для приоритизации")
            return []

        # Весовые коэффициенты из конфигурации
        weights = self.config.get("prioritization", {}).get(
            "weights",
            {"urgency": 0.3, "importance": 0.4, "complexity": 0.1, "dependencies": 0.2},
        )

        # Расчет итогового приоритета для каждой задачи
        for task in self.tasks:
            # Базовый приоритет (важность)
            importance = task.get("priority", 0.5)

            # Срочность
            urgency = task.get("urgency", 0.5)

            # Сложность (инвертированная - сложные задачи имеют меньший приоритет)
            complexity = 1.0 - task.get("complexity", 0.5)

            # Влияние зависимостей
            dependencies_factor = 1.0
            if task.get("dependencies"):
                # Задачи с зависимостями имеют более низкий приоритет
                dependencies_factor = 0.7

            # Расчет итогового приоритета
            final_priority = (
                weights.get("urgency", 0.3) * urgency
                + weights.get("importance", 0.4) * importance
                + weights.get("complexity", 0.1) * complexity
            ) * dependencies_factor

            task["final_priority"] = final_priority
            task["calculated_at"] = datetime.now().isoformat()

        # Сортировка по приоритету (по убыванию)
        self.tasks.sort(key=lambda x: x.get("final_priority", 0), reverse=True)

        logger.info("Задачи приоритизированы. Топ-3:")
        for i, task in enumerate(self.tasks[:3]):
            logger.info(f"  {i+1}. {task['title']} (приоритет: {task['final_priority']:.2f})")

        return self.tasks

    def optimize_schedule(self) -> Dict[str, Any]:
        """Оптимизация расписания выполнения задач"""
        logger.info("Оптимизация расписания...")

        if not self.tasks:
            logger.warning("Нет задач для оптимизации")
            return {}

        # Настройки из конфигурации
        max_concurrent = self.config.get("planning", {}).get("max_concurrent_tasks", 5)
        planning_horizon = self.config.get("planning", {}).get("planning_horizon", 24)  # часы

        # Группировка задач по категориям
        tasks_by_category = {}
        for task in self.tasks:
            category = task.get("category", "uncategorized")
            if category not in tasks_by_category:
                tasks_by_category[category] = []
            tasks_by_category[category].append(task)

        # Создание начального расписания
        schedule = {
            "generated_at": datetime.now().isoformat(),
            "planning_horizon_hours": planning_horizon,
            "max_concurrent_tasks": max_concurrent,
            "tasks_scheduled": 0,
            "total_duration_minutes": 0,
            "schedule": [],
        }

        # Простой алгоритм планирования (FCFS с приоритетами)
        current_time = datetime.now()
        time_slots = {}

        for task in self.tasks:
            # Проверка зависимостей
            dependencies = task.get("dependencies", [])
            if dependencies:
                # Проверяем, выполнены ли зависимости
                for dep_id in dependencies:
                    # В реальной реализации здесь была бы проверка выполнения
                    pass

            # Расчет времени начала
            duration = task.get("estimated_duration", 60)
            start_time = current_time

            # Поиск свободного слота
            slot_found = False
            for hour_offset in range(0, planning_horizon * 60, 30):  # Проверка каждые 30 минут
                check_time = current_time + timedelta(minutes=hour_offset)
                time_key = check_time.strftime("%Y-%m-%d %H:%M")

                if time_key not in time_slots:
                    time_slots[time_key] = 0

                if time_slots[time_key] < max_concurrent:
                    # Найден свободный слот
                    start_time = check_time
                    time_slots[time_key] += 1
                    slot_found = True
                    break

            if not slot_found:
                # Если не нашли слот, используем первое доступное время
                start_time = current_time + timedelta(hours=planning_horizon)

            # Расчет времени окончания
            end_time = start_time + timedelta(minutes=duration)

            # Добавление в расписание
            schedule_entry = {
                "task_id": task["id"],
                "title": task["title"],
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_minutes": duration,
                "priority": task.get("final_priority", 0.5),
                "category": task.get("category", "uncategorized"),
                "resources": task.get("resources", []),
            }

            schedule["schedule"].append(schedule_entry)
            schedule["tasks_scheduled"] += 1
            schedule["total_duration_minutes"] += duration

        self.schedule = schedule
        logger.info(
            f"Запланировано {schedule['tasks_scheduled']} задач на {schedule['total_duration_minutes']} минут"
        )

        return schedule

    def identify_dependencies(self) -> Dict[str, List[str]]:
        """Выявление зависимостей между задачами"""
        logger.info("Анализ зависимостей между задачами...")

        dependencies = {}

        for task in self.tasks:
            task_id = task.get("id")
            deps = task.get("dependencies", [])

            if deps:
                dependencies[task_id] = deps

                # Проверка существования зависимых задач
                for dep_id in deps:
                    dep_exists = any(t.get("id") == dep_id for t in self.tasks)
                    if not dep_exists:
                        logger.warning(f"Зависимость {dep_id} для задачи {task_id} не найдена")

        # Построение графа зависимостей
        dependency_graph = self._build_dependency_graph(dependencies)

        # Проверка циклических зависимостей
        cycles = self._detect_cycles(dependency_graph)
        if cycles:
            logger.warning(f"Обнаружены циклические зависимости: {cycles}")

        return {
            "dependencies": dependencies,
            "dependency_graph": dependency_graph,
            "has_cycles": len(cycles) > 0,
            "cycles": cycles,
        }

    def _build_dependency_graph(self, dependencies: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """Построение графа зависимостей"""
        graph = {}

        for task_id, deps in dependencies.items():
            if task_id not in graph:
                graph[task_id] = []
            graph[task_id].extend(deps)

        return graph

    def _detect_cycles(self, graph: Dict[str, List[str]]) -> List[List[str]]:
        """Обнаружение циклических зависимостей"""
        # Упрощенная реализация для демонстрации
        cycles = []
        visited = set()

        def dfs(node, path):
            if node in path:
                # Найден цикл
                cycle_start = path.index(node)
                cycles.append(path[cycle_start:] + [node])
                return

            if node in visited:
                return

            visited.add(node)
            path.append(node)

            for neighbor in graph.get(node, []):
                dfs(neighbor, path.copy())

        for node in graph:
            dfs(node, [])

        return cycles

    def group_parallel_tasks(self) -> Dict[str, List[Dict[str, Any]]]:
        """Группировка задач для параллельного выполнения"""
        logger.info("Группировка задач для параллельного выполнения...")

        if not self.tasks:
            return {}

        # Группировка по категориям
        groups = {}

        for task in self.tasks:
            category = task.get("category", "uncategorized")

            if category not in groups:
                groups[category] = {
                    "category": category,
                    "tasks": [],
                    "total_duration": 0,
                    "avg_priority": 0,
                }

            groups[category]["tasks"].append(task)
            groups[category]["total_duration"] += task.get("estimated_duration", 0)

        # Расчет среднего приоритета для каждой группы
        for category, group_data in groups.items():
            tasks = group_data["tasks"]
            if tasks:
                avg_priority = sum(t.get("final_priority", 0) for t in tasks) / len(tasks)
                group_data["avg_priority"] = avg_priority

        # Сортировка групп по среднему приоритету (по убыванию)
        sorted_groups = dict(
            sorted(groups.items(), key=lambda x: x[1]["avg_priority"], reverse=True)
        )

        logger.info(f"Создано {len(sorted_groups)} групп задач")
        for category, data in list(sorted_groups.items())[:3]:
            logger.info(
                f"  Группа '{category}': {len(data['tasks'])} задач, приоритет: {data['avg_priority']:.2f}"
            )

        return sorted_groups

    def save_results(self):
        """Сохранение результатов планирования"""
        reports_dir = Path(".agents/reports/plans")
        reports_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Сохранение приоритизированных задач
        tasks_file = reports_dir / f"prioritized_tasks_{timestamp}.json"
        with open(tasks_file, "w", encoding="utf-8") as f:
            json.dump(self.tasks, f, indent=2, ensure_ascii=False)

        # Сохранение расписания
        if self.schedule:
            schedule_file = reports_dir / f"schedule_{timestamp}.json"
            with open(schedule_file, "w", encoding="utf-8") as f:
                json.dump(self.schedule, f, indent=2, ensure_ascii=False)

        # Сохранение сводного отчета
        summary = {
            "timestamp": datetime.now().isoformat(),
            "total_tasks": len(self.tasks),
            "tasks_prioritized": len([t for t in self.tasks if "final_priority" in t]),
            "schedule_generated": bool(self.schedule),
            "schedule_tasks": self.schedule.get("tasks_scheduled", 0) if self.schedule else 0,
            "total_duration_hours": (
                self.schedule.get("total_duration_minutes", 0) / 60 if self.schedule else 0
            ),
            "report_files": {
                "tasks": str(tasks_file),
                "schedule": str(schedule_file) if self.schedule else None,
            },
        }

        summary_file = reports_dir / f"planning_summary_{timestamp}.json"
        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        logger.info(f"Результаты планирования сохранены в {reports_dir}")


def main():
    """Основная функция запуска планировщика"""
    try:
        logger.info("Запуск планировщика задач...")

        planner = TaskPlanner()

        # Загрузка задач
        tasks = planner.load_tasks()
        logger.info(f"Загружено {len(tasks)} задач")

        # Приоритизация
        prioritized = planner.prioritize_tasks()

        # Анализ зависимостей
        dependencies = planner.identify_dependencies()

        # Группировка для параллельного выполнения
        groups = planner.group_parallel_tasks()

        # Оптимизация расписания
        schedule = planner.optimize_schedule()

        # Сохранение результатов
        planner.save_results()

        # Вывод краткой информации
        print("\n" + "=" * 60)
        print("РЕЗУЛЬТАТЫ ПЛАНИРОВАНИЯ ЗАДАЧ")
        print("=" * 60)

        print(f"Всего задач: {len(tasks)}")
        print(f"Приоритизировано: {len(prioritized)}")

        if schedule:
            print(f"Запланировано: {schedule.get('tasks_scheduled', 0)}")
            print(f"Общая длительность: {schedule.get('total_duration_minutes', 0) / 60:.1f} часов")

        if dependencies.get("has_cycles"):
            print("⚠️  Обнаружены циклические зависимости!")

        print("\nТоп-5 задач по приоритету:")
        for i, task in enumerate(prioritized[:5]):
            print(f"  {i+1}. {task['title']} (приоритет: {task.get('final_priority', 0):.2f})")

        print("=" * 60)

        # Сохранение статуса для мониторинга
        status_file = Path(".agents/plans/last_plan_status.json")
        status_file.parent.mkdir(exist_ok=True)

        with open(status_file, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "status": "success",
                    "timestamp": time.time(),
                    "tasks_processed": len(tasks),
                    "plan_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
                },
                f,
                indent=2,
            )

        return 0

    except Exception as e:
        logger.error(f"Ошибка при планировании: {e}")

        # Сохранение статуса ошибки
        status_file = Path(".agents/plans/last_plan_status.json")
        status_file.parent.mkdir(exist_ok=True)

        with open(status_file, "w", encoding="utf-8") as f:
            json.dump(
                {"status": "error", "timestamp": time.time(), "error": str(e)},
                f,
                indent=2,
            )

        return 1


if __name__ == "__main__":
    sys.exit(main())
