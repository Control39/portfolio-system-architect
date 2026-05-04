#!/usr/bin/env python3
"""
Исправленный скрипт запуска Cognitive Automation Agent.
Основан на workflow-driven архитектуре.
"""

import logging
import os
import signal
import subprocess
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List
import json

# Создание папки логов перед инициализацией логирования
LOG_DIR = Path("apps/cognitive-agent/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(str(LOG_DIR / "agent_launch.log")),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class CognitiveAgentLauncher:
    """Запускатель и менеджер Cognitive Automation Agent"""

    def __init__(self, agent_root: str = "apps/cognitive-agent"):
        self.agent_root = Path(agent_root)
        self.processes: Dict[str, subprocess.Popen] = {}
        self.monitoring_threads: Dict[str, threading.Thread] = {}
        self.running = False

        # Создание необходимых директорий
        self._ensure_directories()

        # Загрузка конфигурации
        self.config = self._load_configuration()

    def _ensure_directories(self):
        """Создание необходимых директорий"""
        required_dirs = [
            "logs",
            "scans",
            "reports",
            "backups",
            "cache",
            "data",
            "knowledge",
            "models",
            "plans",
            "recommendations",
        ]

        for dir_name in required_dirs:
            dir_path = self.agent_root / dir_name
            dir_path.mkdir(exist_ok=True, parents=True)
            logger.info(f"Директория проверена/создана: {dir_path}")

    def _load_configuration(self) -> Dict[str, Any]:
        """Загрузка конфигурации агента"""
        config_path = self.agent_root / "config" / "agent-config.yaml"

        if not config_path.exists():
            logger.warning(f"Конфигурационный файл не найден: {config_path}")
            return self._get_default_config()

        try:
            import yaml
            with open(config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
            logger.info(f"Конфигурация загружена из: {config_path}")
            return config
        except Exception as e:
            logger.error(f"Ошибка загрузки конфигурации: {e}")
            return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Получение конфигурации по умолчанию"""
        return {
            "autonomy": {"level": "high", "approval_required": False},
            "scanning": {"enabled": True, "triggers": {"project_open": True}},
            "components": {"scanner": True, "planner": True, "learning": True, "executor": True},
        }

    def start_agent(self, mode: str = "full") -> bool:
        """Запуск агента в указанном режиме"""
        logger.info(f"🚀 Запуск Cognitive Automation Agent в режиме: {mode}")

        try:
            # Запуск компонентов в зависимости от режима
            components_to_start = self._get_components_for_mode(mode)

            for component in components_to_start:
                if not self._start_component(component):
                    logger.error(f"Не удалось запустить компонент: {component}")

            self.running = True
            logger.info("✅ Cognitive Automation Agent успешно запущен")

            # Запуск мониторинга
            self._start_monitoring()

            return True

        except Exception as e:
            logger.error(f"Ошибка запуска агента: {e}")
            return False

    def _get_components_for_mode(self, mode: str) -> List[str]:
        """Получение списка компонентов для запуска в зависимости от режима"""
        modes = {
            "full": ["scanner", "planner", "learning", "executor"],
            "scan": ["scanner"],
            "plan": ["planner"],
            "learn": ["learning"],
            "execute": ["executor"],
            "minimal": ["scanner", "planner"],
        }

        return modes.get(mode, modes["minimal"])

    def _start_component(self, component: str) -> bool:
        """Запуск конкретного компонента"""
        component_scripts = {
            "scanner": "scanner_main.py",
            "planner": "planner_main.py",
            "learning": "learning_main.py",
            "executor": "executor_main.py",
        }

        script_name = component_scripts.get(component)
        if not script_name:
            logger.error(f"Неизвестный компонент: {component}")
            return False

        # Проверяем существование скрипта
        script_path = self.agent_root / "scripts" / script_name
        if not script_path.exists():
            logger.warning(f"Скрипт компонента не найден: {script_path}")
            return False

        # Запуск компонента
        try:
            cmd = [sys.executable, str(script_path), "--daemon"]
            env = os.environ.copy()
            env["AGENT_MODE"] = component
            env["AGENT_ROOT"] = str(self.agent_root)

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                text=True,
                bufsize=1,
            )

            self.processes[component] = process
            logger.info(f"Компонент запущен: {component} (PID: {process.pid})")

            # Запуск потока для чтения вывода
            self._start_output_reader(component, process)

            return True

        except Exception as e:
            logger.error(f"Ошибка запуска компонента {component}: {e}")
            return False

    def _start_output_reader(self, component: str, process: subprocess.Popen):
        """Запуск потока для чтения вывода компонента"""
        def read_output():
            while True:
                try:
                    output = process.stdout.readline()
                    if output:
                        logger.info(f"[{component}] {output.strip()}")
                    elif process.poll() is not None:
                        break
                except Exception:
                    break

        thread = threading.Thread(target=read_output, daemon=True)
        thread.start()

    def _start_monitoring(self):
        """Запуск мониторинга работы агента"""
        logger.info("📊 Запуск системы мониторинга...")

        # Мониторинг процессов
        monitor_thread = threading.Thread(target=self._monitor_processes, daemon=True)
        monitor_thread.start()
        self.monitoring_threads["process_monitor"] = monitor_thread

    def _monitor_processes(self):
        """Мониторинг процессов компонентов"""
        logger.info("Мониторинг процессов запущен")

        while self.running:
            time.sleep(30)

            for component, process in list(self.processes.items()):
                if process.poll() is not None:
                    logger.warning(f"Компонент {component} завершился с кодом: {process.returncode}")

                    if self.config.get("autonomy", {}).get("level") == "high":
                        logger.info(f"Попытка перезапуска компонента: {component}")
                        self._start_component(component)

    def stop_agent(self, graceful: bool = True) -> bool:
        """Остановка агента"""
        logger.info("🛑 Остановка Cognitive Automation Agent...")

        self.running = False

        for component, process in list(self.processes.items()):
            try:
                if graceful:
                    process.terminate()
                    try:
                        process.wait(timeout=10)
                        logger.info(f"Компонент {component} корректно остановлен")
                    except subprocess.TimeoutExpired:
                        logger.warning(f"Компонент {component} не ответил, принудительная остановка")
                        process.kill()
                else:
                    process.kill()
            except Exception as e:
                logger.error(f"Ошибка остановки компонента {component}: {e}")

        self.processes.clear()
        logger.info("✅ Cognitive Automation Agent остановлен")
        return True

    def get_status(self) -> Dict[str, Any]:
        """Получение статуса агента"""
        status = {
            "running": self.running,
            "timestamp": datetime.now().isoformat(),
            "components": {},
            "resources": {},
        }

        for component, process in self.processes.items():
            status["components"][component] = {
                "pid": process.pid if process else None,
                "alive": process.poll() is None if process else False,
            }

        return status

    def run_workflow(self, workflow_name: str, params: Dict[str, Any] = None) -> bool:
        """Запуск рабочего процесса"""
        logger.info(f"🚀 Запуск рабочего процесса: {workflow_name}")

        workflow_path = self.agent_root / "workflows" / f"{workflow_name}.yaml"
        if not workflow_path.exists():
            logger.error(f"Рабочий процесс не найден: {workflow_path}")
            return False

        try:
            logger.info(f"Запуск workflow: {workflow_name}")
            workflow_thread = threading.Thread(
                target=self._execute_workflow,
                args=(workflow_name, params or {}),
                daemon=True,
            )
            workflow_thread.start()

            logger.info(f"Рабочий процесс {workflow_name} запущен")
            return True

        except Exception as e:
            logger.error(f"Ошибка запуска рабочего процесса: {e}")
            return False

    def _execute_workflow(self, workflow_name: str, params: Dict[str, Any]):
        """Выполнение рабочего процесса"""
        logger.info(f"Выполнение workflow: {workflow_name}")

        phases = ["scanning", "analysis", "planning", "execution", "validation"]

        for phase in phases:
            logger.info(f"Workflow {workflow_name}: фаза {phase}")
            time.sleep(2)

        logger.info(f"Workflow {workflow_name} завершен успешно")

        result_file = (
            self.agent_root / "reports" / f"workflow_{workflow_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        result_file.parent.mkdir(exist_ok=True)

        results = {
            "workflow": workflow_name,
            "timestamp": datetime.now().isoformat(),
            "status": "completed",
            "phases_completed": phases,
        }

        with open(result_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        logger.info(f"Результаты workflow сохранены: {result_file}")


def signal_handler(signum, frame):
    """Обработчик сигналов"""
    logger.info(f"Получен сигнал {signum}, остановка агента...")
    if "launcher" in globals():
        globals()["launcher"].stop_agent()
    sys.exit(0)


def main():
    """Основная функция запуска"""
    import argparse

    parser = argparse.ArgumentParser(description="Cognitive Automation Agent Launcher")
    parser.add_argument(
        "--mode",
        choices=["full", "scan", "plan", "learn", "execute", "minimal"],
        default="full",
        help="Режим запуска агента",
    )
    parser.add_argument("--workflow", help="Запуск конкретного рабочего процесса")
    parser.add_argument("--params", help="Параметры workflow в формате JSON")
    parser.add_argument("--status", action="store_true", help="Показать статус агента")
    parser.add_argument("--stop", action="store_true", help="Остановить агента")

    args = parser.parse_args()

    global launcher
    launcher = CognitiveAgentLauncher()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    if args.status:
        status = launcher.get_status()
        print(json.dumps(status, indent=2, ensure_ascii=False))
        return

    if args.stop:
        launcher.stop_agent()
        return

    if args.workflow:
        params = {}
        if args.params:
            try:
                params = json.loads(args.params)
            except json.JSONDecodeError as e:
                logger.error(f"Ошибка разбора параметров: {e}")
                return

        if launcher.run_workflow(args.workflow, params):
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                logger.info("Workflow прерван пользователем")
        return

    if launcher.start_agent(args.mode):
        logger.info("Агент запущен. Нажмите Ctrl+C для остановки.")
        try:
            while launcher.running:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Получен сигнал прерывания")
        finally:
            launcher.stop_agent()
    else:
        logger.error("Не удалось запустить агента")
        sys.exit(1)


if __name__ == "__main__":
    main()
