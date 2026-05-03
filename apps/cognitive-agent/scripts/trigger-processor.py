#!/usr/bin/env python3
"""
Обработчик автоматических триггеров Cognitive Automation Agent.
Мониторит события и запускает соответствующие действия.
"""

import json
import logging
import os
import signal
import subprocess
import sys
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("apps/cognitive-agent/logs/triggers.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class TriggerPriority(Enum):
    """Приоритеты триггеров"""

    CRITICAL = 100
    HIGH = 75
    MEDIUM = 50
    LOW = 25


class TriggerStatus(Enum):
    """Статусы триггеров"""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"


@dataclass
class TriggerEvent:
    """Событие триггера"""

    name: str
    source: str
    data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    priority: TriggerPriority = TriggerPriority.MEDIUM

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return {
            "name": self.name,
            "source": self.source,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "priority": self.priority.value,
        }


@dataclass
class TriggerAction:
    """Действие триггера"""

    name: str
    command: str
    timeout: int
    allowed_failures: int = 0
    retry_count: int = 0

    def execute(self) -> Dict[str, Any]:
        """Выполнение действия"""
        logger.info(f"Выполнение действия: {self.name}")

        try:
            # Разделяем команду на части
            cmd_parts = self.command.split()

            # Если команда начинается с python, добавляем путь к скриптам
            if cmd_parts[0] == "python" and len(cmd_parts) > 1:
                script_name = cmd_parts[1]
                if not script_name.startswith(".") and not script_name.startswith("/"):
                    # Ищем скрипт в директориях агента
                    script_path = self._find_script(script_name)
                    if script_path:
                        cmd_parts[1] = str(script_path)

            # Выполняем команду
            start_time = time.time()
            result = subprocess.run(
                cmd_parts,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=Path.cwd(),
            )
            execution_time = time.time() - start_time

            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "execution_time": execution_time,
            }

        except subprocess.TimeoutExpired:
            logger.error(f"Таймаут выполнения действия: {self.name}")
            return {
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": f"Timeout after {self.timeout} seconds",
                "execution_time": self.timeout,
            }
        except Exception as e:
            logger.error(f"Ошибка выполнения действия {self.name}: {e}")
            return {
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": str(e),
                "execution_time": 0,
            }

    def _find_script(self, script_name: str) -> Optional[Path]:
        """Поиск скрипта в директориях агента"""
        search_paths = [
            Path(".agents") / "scripts",
            Path(".agents") / "tests",
            Path(".agents"),
            Path("."),
        ]

        for path in search_paths:
            script_path = path / script_name
            if script_path.exists():
                return script_path

        return None


class TriggerProcessor:
    """Обработчик триггеров"""

    def __init__(self, config_path: str = "apps/cognitive-agent/config/triggers.yaml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.triggers = self._parse_triggers()
        self.actions = self._parse_actions()
        self.event_queue = []
        self.queue_lock = threading.Lock()
        self.running = False
        self.workers = []

        # Статистика
        self.stats = {
            "processed": 0,
            "succeeded": 0,
            "failed": 0,
            "retried": 0,
            "queue_size": 0,
        }

        # Очередь с приоритетами
        self.priority_queue = []

    def _load_config(self) -> Dict[str, Any]:
        """Загрузка конфигурации"""
        if not self.config_path.exists():
            logger.warning(f"Конфигурационный файл не найден: {self.config_path}")
            return {}

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            logger.error(f"Ошибка загрузки конфигурации: {e}")
            return {}

    def _parse_triggers(self) -> Dict[str, Dict[str, Any]]:
        """Парсинг триггеров из конфигурации"""
        triggers = self.config.get("triggers", {})
        logger.info(f"Загружено триггеров: {len(triggers)}")
        return triggers

    def _parse_actions(self) -> Dict[str, TriggerAction]:
        """Парсинг действий из конфигурации"""
        actions_config = self.config.get("actions", {})
        actions = {}

        for name, config in actions_config.items():
            action = TriggerAction(
                name=name,
                command=config.get("command", ""),
                timeout=config.get("timeout", 60),
                allowed_failures=config.get("allowed_failures", 0),
            )
            actions[name] = action

        logger.info(f"Загружено действий: {len(actions)}")
        return actions

    def add_event(self, event: TriggerEvent):
        """Добавление события в очередь"""
        with self.queue_lock:
            # Добавляем в очередь с учетом приоритета
            self.priority_queue.append(event)
            # Сортируем по приоритету (по убыванию)
            self.priority_queue.sort(key=lambda e: e.priority.value, reverse=True)
            self.stats["queue_size"] = len(self.priority_queue)

        logger.info(f"Добавлено событие: {event.name} (приоритет: {event.priority})")

    def process_event(self, event: TriggerEvent) -> bool:
        """Обработка одного события"""
        logger.info(f"Обработка события: {event.name}")

        # Получаем конфигурацию триггера
        trigger_config = self.triggers.get(event.name)
        if not trigger_config:
            logger.warning(f"Конфигурация триггера не найдена: {event.name}")
            return False

        # Проверяем условия
        if not self._check_conditions(trigger_config.get("conditions", []), event):
            logger.info(f"Условия триггера не выполнены: {event.name}")
            return False

        # Получаем действия
        action_names = trigger_config.get("actions", [])
        trigger_config.get("autonomy_level", "medium")

        # Выполняем действия
        success = True
        results = []

        for action_name in action_names:
            action = self.actions.get(action_name)
            if not action:
                logger.warning(f"Действие не найдено: {action_name}")
                continue

            # Выполняем действие
            result = action.execute()
            results.append(
                {
                    "action": action_name,
                    "success": result["success"],
                    "execution_time": result["execution_time"],
                }
            )

            if not result["success"]:
                success = False
                logger.error(f"Действие завершилось с ошибкой: {action_name}")

                # Проверяем, разрешены ли ошибки
                if action.allowed_failures > 0 and action.retry_count < action.allowed_failures:
                    action.retry_count += 1
                    logger.info(f"Повторная попытка {action.retry_count}/{action.allowed_failures}")
                    # Повторяем действие
                    result = action.execute()
                    if result["success"]:
                        success = True
                        logger.info(f"Повторная попытка успешна: {action_name}")

        # Логируем результаты
        self._log_results(event, results, success)

        # Обновляем статистику
        with self.queue_lock:
            self.stats["processed"] += 1
            if success:
                self.stats["succeeded"] += 1
            else:
                self.stats["failed"] += 1

        return success

    def _check_conditions(self, conditions: List[Any], event: TriggerEvent) -> bool:
        """Проверка условий триггера"""
        if not conditions:
            return True

        # Простая реализация проверки условий
        for _condition in conditions:
            # TODO: Реализовать полноценную проверку условий
            # Сейчас просто возвращаем True для всех условий
            pass

        return True

    def _log_results(self, event: TriggerEvent, results: List[Dict[str, Any]], success: bool):
        """Логирование результатов"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event": event.to_dict(),
            "results": results,
            "success": success,
        }

        # Сохраняем в файл
        log_dir = Path("apps/cognitive-agent/logs/triggers")
        log_dir.mkdir(exist_ok=True, parents=True)

        log_file = log_dir / f"trigger_{event.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(log_entry, f, indent=2, ensure_ascii=False)

        logger.info(f"Результаты сохранены: {log_file}")

    def worker_loop(self):
        """Цикл обработки событий воркером"""
        while self.running:
            event = None

            # Получаем событие из очереди
            with self.queue_lock:
                if self.priority_queue:
                    event = self.priority_queue.pop(0)
                    self.stats["queue_size"] = len(self.priority_queue)

            if event:
                self.process_event(event)
            else:
                # Нет событий, ждем
                time.sleep(1)

    def start(self, num_workers: int = 3):
        """Запуск обработчика триггеров"""
        if self.running:
            logger.warning("Обработчик уже запущен")
            return

        logger.info(f"Запуск обработчика триггеров с {num_workers} воркерами")
        self.running = True

        # Запускаем воркеры
        for i in range(num_workers):
            worker = threading.Thread(target=self.worker_loop, name=f"TriggerWorker-{i}")
            worker.daemon = True
            worker.start()
            self.workers.append(worker)

        logger.info("Обработчик триггеров запущен")

    def stop(self):
        """Остановка обработчика триггеров"""
        logger.info("Остановка обработчика триггеров")
        self.running = False

        # Ждем завершения воркеров
        for worker in self.workers:
            worker.join(timeout=5)

        logger.info("Обработчик триггеров остановлен")

    def get_stats(self) -> Dict[str, Any]:
        """Получение статистики"""
        with self.queue_lock:
            stats = self.stats.copy()
            stats["queue_size"] = len(self.priority_queue)

        return stats

    def simulate_event(self, event_name: str, data: Dict[str, Any] = None):
        """Симуляция события (для тестирования)"""
        event = TriggerEvent(
            name=event_name,
            source="simulation",
            data=data or {},
            priority=TriggerPriority.MEDIUM,
        )

        self.add_event(event)
        logger.info(f"Симулировано событие: {event_name}")


# Готовые триггеры для распространенных сценариев
class CommonTriggers:
    """Готовые триггеры для распространенных сценариев"""

    @staticmethod
    def create_project_open_trigger() -> TriggerEvent:
        """Триггер при открытии проекта"""
        return TriggerEvent(
            name="project_open",
            source="vscode",
            data={"project_path": str(Path.cwd())},
            priority=TriggerPriority.HIGH,
        )

    @staticmethod
    def create_file_change_trigger(file_path: str) -> TriggerEvent:
        """Триггер при изменении файла"""
        return TriggerEvent(
            name="file_change",
            source="filesystem",
            data={
                "file_path": file_path,
                "event_type": "modified",
                "timestamp": datetime.now().isoformat(),
            },
            priority=TriggerPriority.MEDIUM,
        )

    @staticmethod
    def create_git_commit_trigger(commit_hash: str, message: str) -> TriggerEvent:
        """Триггер при коммите в Git"""
        return TriggerEvent(
            name="git_commit",
            source="git",
            data={
                "commit_hash": commit_hash,
                "message": message,
                "branch": "main",
                "author": os.environ.get("USER", "unknown"),
            },
            priority=TriggerPriority.HIGH,
        )

    @staticmethod
    def create_error_trigger(error_message: str, component: str) -> TriggerEvent:
        """Триггер при ошибке"""
        return TriggerEvent(
            name="error_detected",
            source=component,
            data={
                "error_message": error_message,
                "component": component,
                "severity": "error",
            },
            priority=TriggerPriority.CRITICAL,
        )

    @staticmethod
    def create_schedule_trigger(schedule_name: str) -> TriggerEvent:
        """Триггер по расписанию"""
        return TriggerEvent(
            name=schedule_name,
            source="scheduler",
            data={"schedule": schedule_name, "timestamp": datetime.now().isoformat()},
            priority=TriggerPriority.LOW,
        )


def main():
    """Основная функция"""
    import argparse

    parser = argparse.ArgumentParser(description="Обработчик триггеров Cognitive Automation Agent")
    parser.add_argument(
        "--config", default="apps/cognitive-agent/config/triggers.yaml", help="Путь к конфигурации"
    )
    parser.add_argument("--workers", type=int, default=3, help="Количество воркеров")
    parser.add_argument("--simulate", help="Симулировать событие")
    parser.add_argument("--simulate-data", help="Данные для симуляции (JSON)")
    parser.add_argument("--stats", action="store_true", help="Показать статистику")
    parser.add_argument("--daemon", action="store_true", help="Запуск в режиме демона")

    args = parser.parse_args()

    # Создаем обработчик
    processor = TriggerProcessor(args.config)

    if args.simulate:
        # Симуляция события
        data = {}
        if args.simulate_data:
            try:
                data = json.loads(args.simulate_data)
            except:
                logger.error("Ошибка парсинга JSON данных")

        processor.simulate_event(args.simulate, data)

        # Обрабатываем событие
        processor.start(1)
        time.sleep(5)
        processor.stop()

    elif args.stats:
        # Показываем статистику
        stats = processor.get_stats()
        print(json.dumps(stats, indent=2, ensure_ascii=False))

    elif args.daemon:
        # Запуск в режиме демона
        print("🚀 Запуск обработчика триггеров в режиме демона...")
        print(f"Конфигурация: {args.config}")
        print(f"Воркеры: {args.workers}")
        print("Нажмите Ctrl+C для остановки")

        # Обработка сигналов
        def signal_handler(sig, frame):
            print("\n🛑 Остановка обработчика...")
            processor.stop()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Запускаем обработчик
        processor.start(args.workers)

        # Бесконечный цикл
        try:
            while True:
                time.sleep(1)
                # Периодически логируем статистику
                stats = processor.get_stats()
                if stats["processed"] % 10 == 0:
                    logger.info(f"Статистика: {stats}")
        except KeyboardInterrupt:
            signal_handler(None, None)

    else:
        # Интерактивный режим
        print("🔧 Обработчик триггеров Cognitive Automation Agent")
        print("Используйте --help для просмотра доступных опций")


if __name__ == "__main__":
    main()
