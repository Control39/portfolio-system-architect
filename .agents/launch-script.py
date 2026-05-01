#!/usr/bin/env python3
"""
Скрипт запуска Cognitive Automation Agent.
Обеспечивает автоматический запуск, мониторинг и управление агентом.
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

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(".agents/logs/agent_launch.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class CognitiveAgentLauncher:
    """Запускатель и менеджер Cognitive Automation Agent"""

    def __init__(self, agent_root: str = ".agents"):
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
            "autonomy": {"level": "medium", "approval_required": True},
            "scanning": {"enabled": True, "triggers": {"project_open": True}},
            "components": {"scanner": True, "planner": True, "learning": True},
        }

    def start_agent(self, mode: str = "full") -> bool:
        """Запуск агента в указанном режиме"""
        logger.info(f"🚀 Запуск Cognitive Automation Agent в режиме: {mode}")

        try:
            # Проверка предварительных условий
            if not self._check_prerequisites():
                logger.error("Не выполнены предварительные условия")
                return False

            # Запуск компонентов в зависимости от режима
            components_to_start = self._get_components_for_mode(mode)

            for component in components_to_start:
                if not self._start_component(component):
                    logger.error(f"Не удалось запустить компонент: {component}")
                    return False

            self.running = True
            logger.info("✅ Cognitive Automation Agent успешно запущен")

            # Запуск мониторинга
            self._start_monitoring()

            return True

        except Exception as e:
            logger.error(f"Ошибка запуска агента: {e}")
            return False

    def _check_prerequisites(self) -> bool:
        """Проверка предварительных условий"""
        logger.info("🔍 Проверка предварительных условий...")

        checks = [
            ("Python 3.9+", self._check_python_version),
            ("Директория агента", lambda: self.agent_root.exists()),
            ("Конфигурация", lambda: (self.agent_root / "config").exists()),
            ("Скиллы", lambda: (self.agent_root / "skills").exists()),
        ]

        all_passed = True
        for check_name, check_func in checks:
            try:
                if check_func():
                    logger.info(f"  ✅ {check_name}")
                else:
                    logger.warning(f"  ⚠️  {check_name}")
                    all_passed = False
            except Exception as e:
                logger.error(f"  ❌ {check_name}: {e}")
                all_passed = False

        return all_passed

    def _check_python_version(self) -> bool:
        """Проверка версии Python"""
        return sys.version_info >= (3, 9)

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
            # Создаем заглушку для тестирования
            return self._create_component_stub(component)

        # Запуск компонента
        try:
            cmd = [sys.executable, str(script_path), "--daemon"]
            env = os.environ.copy()
            env["AGENT_MODE"] = component

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                text=True,
                bufsize=1,
                universal_newlines=True,
            )

            self.processes[component] = process
            logger.info(f"Компонент запущен: {component} (PID: {process.pid})")

            # Запуск потока для чтения вывода
            self._start_output_reader(component, process)

            return True

        except Exception as e:
            logger.error(f"Ошибка запуска компонента {component}: {e}")
            return False

    def _create_component_stub(self, component: str) -> bool:
        """Создание заглушки компонента для тестирования"""
        logger.info(f"Создание заглушки для компонента: {component}")

        # Создаем простой скрипт-заглушку
        stub_content = f'''#!/usr/bin/env python3
"""
Заглушка компонента {component} Cognitive Automation Agent.
В реальной реализации здесь будет логика компонента.
"""

import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Основная функция компонента"""
    logger.info(f"Компонент {{component}} запущен")

    # Имитация работы компонента
    while True:
        logger.info(f"Компонент {{component}} работает...")
        time.sleep(10)

if __name__ == "__main__":
    main()
'''

        scripts_dir = self.agent_root / "scripts"
        scripts_dir.mkdir(exist_ok=True)

        stub_path = scripts_dir / f"{component}_stub.py"
        with open(stub_path, "w", encoding="utf-8") as f:
            f.write(stub_content)

        # Делаем файл исполняемым
        stub_path.chmod(0o755)

        # Запускаем заглушку
        cmd = [sys.executable, str(stub_path)]
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        self.processes[component] = process
        logger.info(f"Заглушка компонента запущена: {component}")

        return True

    def _start_output_reader(self, component: str, process: subprocess.Popen):
        """Запуск потока для чтения вывода компонента"""

        def read_output():
            while True:
                output = process.stdout.readline()
                if output:
                    logger.info(f"[{component}] {output.strip()}")
                elif process.poll() is not None:
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

        # Мониторинг ресурсов
        resource_thread = threading.Thread(target=self._monitor_resources, daemon=True)
        resource_thread.start()
        self.monitoring_threads["resource_monitor"] = resource_thread

        # Мониторинг производительности
        perf_thread = threading.Thread(target=self._monitor_performance, daemon=True)
        perf_thread.start()
        self.monitoring_threads["performance_monitor"] = perf_thread

    def _monitor_processes(self):
        """Мониторинг процессов компонентов"""
        logger.info("Мониторинг процессов запущен")

        while self.running:
            time.sleep(30)  # Проверка каждые 30 секунд

            for component, process in list(self.processes.items()):
                if process.poll() is not None:
                    logger.warning(
                        f"Компонент {component} завершился с кодом: {process.returncode}"
                    )

                    # Попытка перезапуска
                    if self.config.get("autonomy", {}).get("level") == "high":
                        logger.info(f"Попытка перезапуска компонента: {component}")
                        self._start_component(component)

    def _monitor_resources(self):
        """Мониторинг использования ресурсов"""
        logger.info("Мониторинг ресурсов запущен")

        while self.running:
            time.sleep(60)  # Проверка каждую минуту

            try:
                # Мониторинг использования памяти
                import psutil

                process = psutil.Process()
                memory_info = process.memory_info()

                memory_mb = memory_info.rss / 1024 / 1024
                cpu_percent = process.cpu_percent(interval=1)

                if memory_mb > 1024:  # Более 1GB
                    logger.warning(f"Высокое использование памяти: {memory_mb:.2f} MB")

                if cpu_percent > 80:  # Более 80% CPU
                    logger.warning(f"Высокая загрузка CPU: {cpu_percent:.1f}%")

            except ImportError:
                logger.debug("psutil не установлен, мониторинг ресурсов ограничен")
            except Exception as e:
                logger.error(f"Ошибка мониторинга ресурсов: {e}")

    def _monitor_performance(self):
        """Мониторинг производительности"""
        logger.info("Мониторинг производительности запущен")

        performance_log = self.agent_root / "logs" / "performance.csv"

        # Создаем заголовок CSV файла
        if not performance_log.exists():
            with open(performance_log, "w", encoding="utf-8") as f:
                f.write("timestamp,component,task_count,success_rate,avg_duration\n")

        while self.running:
            time.sleep(300)  # Запись каждые 5 минут

            try:
                timestamp = datetime.now().isoformat()

                # В реальной реализации здесь будет сбор метрик
                # Сейчас используем заглушку
                metrics = {
                    "scanner": {
                        "task_count": 10,
                        "success_rate": 0.95,
                        "avg_duration": 45.2,
                    },
                    "planner": {
                        "task_count": 5,
                        "success_rate": 0.88,
                        "avg_duration": 120.5,
                    },
                    "learning": {
                        "task_count": 3,
                        "success_rate": 0.92,
                        "avg_duration": 300.0,
                    },
                }

                # Запись метрик в файл
                with open(performance_log, "a", encoding="utf-8") as f:
                    for component, metric in metrics.items():
                        f.write(
                            f"{timestamp},{component},"
                            f"{metric['task_count']},{metric['success_rate']},{metric['avg_duration']}\n"
                        )

                logger.debug("Метрики производительности записаны")

            except Exception as e:
                logger.error(f"Ошибка записи метрик производительности: {e}")

    def stop_agent(self, graceful: bool = True) -> bool:
        """Остановка агента"""
        logger.info("🛑 Остановка Cognitive Automation Agent...")

        self.running = False

        # Остановка компонентов
        for component, process in list(self.processes.items()):
            try:
                if graceful:
                    process.terminate()
                    try:
                        process.wait(timeout=10)
                        logger.info(f"Компонент {component} корректно остановлен")
                    except subprocess.TimeoutExpired:
                        logger.warning(
                            f"Компонент {component} не ответил на terminate, принудительная остановка"
                        )
                        process.kill()
                else:
                    process.kill()
                    logger.info(f"Компонент {component} принудительно остановлен")
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
            "performance": {},
        }

        # Статус компонентов
        for component, process in self.processes.items():
            status["components"][component] = {
                "pid": process.pid,
                "alive": process.poll() is None,
                "returncode": process.returncode if process.poll() is not None else None,
            }

        # Информация о ресурсах
        try:
            import psutil

            process = psutil.Process()
            status["resources"] = {
                "memory_mb": process.memory_info().rss / 1024 / 1024,
                "cpu_percent": process.cpu_percent(),
                "threads": process.num_threads(),
                "open_files": len(process.open_files()),
            }
        except:
            status["resources"] = {"error": "psutil not available"}

        # Производительность
        performance_log = self.agent_root / "logs" / "performance.csv"
        if performance_log.exists():
            try:
                import pandas as pd

                df = pd.read_csv(performance_log)
                if not df.empty:
                    latest = df.iloc[-1]
                    status["performance"] = {
                        "last_measurement": latest["timestamp"],
                        "scanner_success_rate": latest.get("success_rate", 0),
                    }
            except:
                status["performance"] = {"error": "could not read performance log"}

        return status

    def run_workflow(self, workflow_name: str, params: Dict[str, Any] = None) -> bool:
        """Запуск рабочего процесса"""
        logger.info(f"🚀 Запуск рабочего процесса: {workflow_name}")

        workflow_path = self.agent_root / "workflows" / f"{workflow_name}.yaml"
        if not workflow_path.exists():
            logger.error(f"Рабочий процесс не найден: {workflow_path}")
            return False

        try:
            # В реальной реализации здесь будет запуск workflow engine
            # Сейчас имитируем запуск
            logger.info(f"Запуск workflow: {workflow_name} с параметрами: {params}")

            # Создаем задачу для выполнения workflow
            workflow_thread = threading.Thread(
                target=self._execute_workflow,
                args=(workflow_name, params or {}),
                daemon=True,
            )
            workflow_thread.start()

            logger.info(f"Рабочий процесс {workflow_name} запущен в фоновом режиме")
            return True

        except Exception as e:
            logger.error(f"Ошибка запуска рабочего процесса: {e}")
            return False

    def _execute_workflow(self, workflow_name: str, params: Dict[str, Any]):
        """Выполнение рабочего процесса (заглушка)"""
        logger.info(f"Выполнение workflow: {workflow_name}")

        # Имитация выполнения workflow
        phases = ["scanning", "analysis", "planning", "execution", "validation"]

        for phase in phases:
            logger.info(f"Workflow {workflow_name}: фаза {phase}")
            time.sleep(5)  # Имитация работы

        logger.info(f"Workflow {workflow_name} завершен успешно")

        # Сохранение результатов
        result_file = (
            self.agent_root
            / "reports"
            / f"workflow_{workflow_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        result_file.parent.mkdir(exist_ok=True)

        results = {
            "workflow": workflow_name,
            "timestamp": datetime.now().isoformat(),
            "status": "completed",
            "phases_completed": phases,
            "parameters": params,
        }

        import json

        with open(result_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        logger.info(f"Результаты workflow сохранены: {result_file}")


def signal_handler(signum, frame):
    """Обработчик сигналов для корректного завершения"""
    logger.info(f"Получен сигнал {signum}, остановка агента...")
    if "launcher" in globals():
        globals()["launcher"].stop_agent()


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
    parser.add_argument("--restart", action="store_true", help="Перезапустить агента")

    args = parser.parse_args()

    # Инициализация запускателя
    global launcher
    launcher = CognitiveAgentLauncher()

    # Регистрация обработчиков сигналов
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Обработка команд
    if args.status:
        status = launcher.get_status()
        import json

        print(json.dumps(status, indent=2, ensure_ascii=False))
        return

    if args.stop:
        launcher.stop_agent()
        return

    if args.restart:
        launcher.stop_agent()
        time.sleep(2)
        launcher.start_agent(args.mode)
        return

    if args.workflow:
        params = {}
        if args.params:
            try:
                import json

                params = json.loads(args.params)
            except json.JSONDecodeError as e:
                logger.error(f"Ошибка разбора параметров: {e}")
                return

        if launcher.run_workflow(args.workflow, params):
            # Ждем завершения workflow
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                logger.info("Workflow прерван пользователем")
        return

    # Стандартный запуск агента
    if launcher.start_agent(args.mode):
        logger.info("Агент запущен. Нажмите Ctrl+C для остановки.")

        # Бесконечный цикл ожидания
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
