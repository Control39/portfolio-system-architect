#!/usr/bin/env python3
"""
Обработчик автоматических триггеров Cognitive Automation Agent.
Мониторит события и запускает соответствующие действия.
"""

import json
import logging
import os
import platform
import shutil  # Для поиска исполняемых файлов в PATH
import signal
import subprocess
import sys
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

import yaml

# ============================================
# 🔒 SAFE MODE CHECK - БЛОКИРОВКА ТРИГГЕРОВ
# ============================================
# Проверяем safe_mode.yaml перед выполнением триггерных действий
SAFE_MODE_CONFIG = Path("agents/cognitive_agent/config/safe_mode.yaml")


class SafeMode(str, Enum):
    """Режимы безопасного выполнения."""

    NORMAL = "NORMAL"
    SAFE_READ_ONLY = "SAFE_READ_ONLY"
    LOCKDOWN = "LOCKDOWN"


def load_safe_mode() -> SafeMode:
    """Загружает safe_mode.yaml и возвращает режим.

    По умолчанию — NORMAL (т.е. разрешить работу), чтобы обеспечить обратную совместимость.
    """

    if not SAFE_MODE_CONFIG.exists():
        return SafeMode.NORMAL

    try:
        with open(SAFE_MODE_CONFIG, encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}

        raw_mode = str(config.get("mode", SafeMode.NORMAL.value)).strip()
        try:
            return SafeMode(raw_mode)
        except ValueError:
            logging.getLogger(__name__).warning(
                "Unknown safe_mode mode='%s', fallback to NORMAL", raw_mode
            )
            return SafeMode.NORMAL
    except Exception as exc:
        logging.getLogger(__name__).warning(
            "Failed to load safe_mode.yaml: %s; fallback to NORMAL", exc
        )
        return SafeMode.NORMAL



def is_trigger_execution_allowed() -> bool:
    """Определяет, можно ли выполнять триггерные действия в текущем безопасном режиме."""

    mode = load_safe_mode()
    # SAFE_READ_ONLY и LOCKDOWN запрещают выполнение действий
    return mode == SafeMode.NORMAL

# ============================================


# Создание директории для логов
AGENT_ROOT = Path(__file__).resolve().parents[1]
AGENT_DATA_DIR = AGENT_ROOT / ".agent_data"
LOG_DIR = AGENT_DATA_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True, parents=True)


# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(LOG_DIR / "triggers.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Аудит логирование для безопасности
audit_logger = logging.getLogger("audit")
audit_logger.setLevel(logging.INFO)
audit_handler = logging.FileHandler(LOG_DIR / "audit.log")
audit_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
audit_logger.addHandler(audit_handler)

# Whitelist разрешенных команд
ALLOWED_COMMANDS = [
    "python",
    "pytest",
    "mypy",
    "black",
    "ruff",
    "flake8",
    "pip",
    "git",
    "echo",
    "ls",
    "cat",
    "wc",
    "grep",
    "find",
    "sed",
    "awk",
    "sh",
    "bash",
    "make",
    "node",
    "npm",
    "yarn",
    "docker",
    "kubectl",
    "terraform",
    "aws",
    "gcloud",
]


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
    data: dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    priority: TriggerPriority = TriggerPriority.MEDIUM

    def to_dict(self) -> dict[str, Any]:
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

    def _find_script(self, script_name: str) -> Path | None:
        """Поиск скрипта в директориях агента"""
        script_paths = [
            Path("scripts") / script_name,
            Path("agents") / script_name,
            Path("agents/cognitive_agent") / script_name,
        ]
        for path in script_paths:
            if path.exists():
                return path.resolve()
        return None

    def execute(self) -> dict[str, Any]:
        """Выполнение действия"""
        logger.info(f"Выполнение действия: {self.name}")

        try:
            # Разделяем команду на части
            cmd_parts = self.command.split()

            # Валидация команды для предотвления B603 и B607
            if not self._validate_command(cmd_parts):
                return {
                    "success": False,
                    "returncode": -1,
                    "stdout": "",
                    "stderr": "Command validation failed",
                    "execution_time": 0,
                }

            # Преобразование частичного пути к исполняемому файлу в абсолютный
            cmd_parts = self._resolve_executable_path(cmd_parts)

            # Если команда начинается с python, добавляем путь к скриптам
            if cmd_parts[0] == "python" and len(cmd_parts) > 1:
                script_name = cmd_parts[1]
                if not script_name.startswith(".") and not script_name.startswith("/"):
                    # Ищем скрипт в директориях агента
                    script_path = self._find_script(script_name)
                    if script_path:
                        cmd_parts[1] = str(script_path)

            # Выполняем команду с shell=False для безопасности
            start_time = time.time()
            result = subprocess.run(
                cmd_parts,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=Path.cwd(),
                shell=False  # Явно указываем shell=False для предотвращения B602
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

    def _validate_command(self, cmd_parts: list[str]) -> bool:
        """Валидация команды для предотвращения внедрения команд"""
        # Whitelist-подход: проверяем, что команда разрешена
        if cmd_parts:
            command_name = cmd_parts[0].replace('.exe', '').replace('.bat', '').replace('.cmd', '').replace('.ps1', '')
            if command_name not in ALLOWED_COMMANDS:
                audit_logger.warning(f"Команда не разрешена whitelist: {command_name}")
                logger.error(f"Команда не разрешена: {command_name}. Разрешенные команды: {ALLOWED_COMMANDS}")
                return False
            else:
                audit_logger.info(f"Команда разрешена whitelist: {command_name}")

        # Проверяем, что команда не содержит потенциально опасных символов
        dangerous_patterns = [";", "&", "|", "$", "`", ">", "<", "(", ")", "[", "]"]

        for part in cmd_parts:
            for pattern in dangerous_patterns:
                if pattern in part:
                    audit_logger.warning(f"Найден потенциально опасный символ в команде: {pattern} в {part}")
                    logger.warning(f"Найден потенциально опасный символ в команде: {pattern} в {part}")
                    return False

        return True

    def _resolve_executable_path(self, cmd_parts: list[str]) -> list[str]:
        """Преобразование частичного пути к исполняемому файлу в абсолютный"""
        if not cmd_parts:
            return cmd_parts

        executable = cmd_parts[0]

        # Для Windows и Unix систем используем shutil.which для поиска исполняемых файлов
        if platform.system() == "Windows":
            # Для Windows добавляем .exe, если не указано
            if not executable.endswith(('.exe', '.bat', '.cmd', '.ps1')):
                executable += '.exe'

        # Используем shutil.which для поиска исполняемого файла в PATH
        resolved_path = shutil.which(executable)
        if resolved_path:
            cmd_parts[0] = resolved_path
        else:
            logger.warning(f"Исполняемый файл не найден в PATH: {executable}")
            # Если не найден, возвращаем исходную команду (для случаев, когда это локальный скрипт)
            pass

        return cmd_parts


class TriggerProcessor:
    """Обработчик триггеров"""

    def __init__(self, config_path: str = ".agents/config/triggers.yaml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.triggers = self._parse_triggers()
        self.actions = self._parse_actions()
        self.event_queue = []
        self.queue_lock = threading.Lock()
        self.running = False
        self.workers = []

        # Статистика
        self.stats = {"processed": 0, "succeeded": 0, "failed": 0, "retried": 0, "queue_size": 0}

        # Очередь с приоритетами
        self.priority_queue = []

    def _load_config(self) -> dict[str, Any]:
        """Загрузка конфигурации"""
        if not self.config_path.exists():
            logger.warning(f"Конфигурационный файл не найден: {self.config_path}")
            return {}

        try:
            with open(self.config_path, encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            logger.error(f"Ошибка загрузки конфигурации: {e}")
            return {}

    def _parse_triggers(self) -> dict[str, dict[str, Any]]:
        """Парсинг триггеров из конфигурации"""
        triggers = self.config.get("triggers", {})
        logger.info(f"Загружено триггеров: {len(triggers)}")
        return triggers

    def _parse_actions(self) -> dict[str, TriggerAction]:
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
        # SafeMode: запрет выполнения триггерных действий
        if not is_trigger_execution_allowed():
            logger.warning("🔒 SAFE MODE active: Trigger execution is blocked")
            return False

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

    def _check_conditions(self, conditions: list[Any], event: TriggerEvent) -> bool:
        """Проверка условий триггера.

        Формат YAML: список элементов, где каждый элемент — словарь с одним ключом типа условия.

        Если условие не распознано — логируется warning и возвращается True
        (обратная совместимость).
        """

        if not conditions:
            return True

        def _parse_hhmm(value: str) -> tuple[int, int]:
            hh_s, mm_s = value.split(":", 1)
            return int(hh_s), int(mm_s)

        now = datetime.now().time()
        for raw_condition in conditions:
            if not isinstance(raw_condition, dict) or not raw_condition:
                logger.warning("Unknown condition format: %r; fallback to True", raw_condition)
                continue

            condition_type = next(iter(raw_condition.keys()))
            condition_value = raw_condition.get(condition_type)

            # 1) file_exists
            if condition_type == "file_exists":
                if not isinstance(condition_value, str):
                    logger.warning("file_exists expects string path; fallback to True")
                    continue
                if not Path(condition_value).exists():
                    return False
                continue

            # 2) git_operation
            if condition_type == "git_operation":
                expected = str(condition_value)
                actual = str(event.data.get("git_operation", ""))
                if actual != expected:
                    return False
                continue

            # 3) time_of_day
            if condition_type == "time_of_day":
                if not isinstance(condition_value, str) or "-" not in condition_value:
                    logger.warning("time_of_day expects 'HH:MM-HH:MM'; fallback to True")
                    continue
                start_s, end_s = condition_value.split("-", 1)
                sh, sm = _parse_hhmm(start_s.strip())
                eh, em = _parse_hhmm(end_s.strip())
                start_t = datetime.now().replace(
                    hour=sh, minute=sm, second=0, microsecond=0
                ).time()
                end_t = datetime.now().replace(
                    hour=eh, minute=em, second=0, microsecond=0
                ).time()

                # wrap-around window (e.g. 22:00-02:00)
                if start_t <= end_t:
                    if not (start_t <= now <= end_t):
                        return False
                else:
                    if not (now >= start_t or now <= end_t):
                        return False
                continue

            # 4) log_contains
            if condition_type == "log_contains":
                if not isinstance(condition_value, str):
                    logger.warning("log_contains expects string; fallback to True")
                    continue

                log_path = event.data.get("log_path")
                if not isinstance(log_path, str):
                    log_path = str(Path("logs") / "triggers.log")

                try:
                    log_file = Path(log_path)
                    if not log_file.exists():
                        return False
                    content = log_file.read_text(encoding="utf-8", errors="ignore")
                except Exception:
                    logger.warning("Failed reading log file '%s'", log_path)
                    return False

                if condition_value not in content:
                    return False
                continue

            # 5) response_time_gt
            if condition_type == "response_time_gt":
                try:
                    threshold_ms = float(condition_value)
                except (TypeError, ValueError):
                    logger.warning("response_time_gt expects number; fallback to True")
                    continue

                actual_ms_raw = event.data.get("response_time_ms")
                if actual_ms_raw is None:
                    return False
                try:
                    actual_ms_f = float(actual_ms_raw)
                except (TypeError, ValueError):
                    return False

                if not (actual_ms_f > threshold_ms):
                    return False
                continue

            # Unknown condition: обратная совместимость
            logger.warning(
                "Unknown condition '%s'=%r; fallback to True",
                condition_type,
                condition_value,
            )
            # Unknown condition => обратная совместимость: условие не блокирует триггер
            continue

        return True





    def _log_results(self, event: TriggerEvent, results: list[dict[str, Any]], success: bool):
        """Логирование результатов"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event": event.to_dict(),
            "results": results,
            "success": success,
        }

        # Сохраняем в файл
        log_dir = LOG_DIR / "triggers"
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

    def get_stats(self) -> dict[str, Any]:
        """Получение статистики"""
        with self.queue_lock:
            stats = self.stats.copy()
            stats["queue_size"] = len(self.priority_queue)

        return stats

    def simulate_event(self, event_name: str, data: dict[str, Any] = None):
        """Симуляция события (для тестирования)"""
        event = TriggerEvent(name=event_name, source="simulation", data=data or {}, priority=TriggerPriority.MEDIUM)

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
            data={"error_message": error_message, "component": component, "severity": "error"},
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
    parser.add_argument("--config", default=".agents/config/triggers.yaml", help="Путь к конфигурации")
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
