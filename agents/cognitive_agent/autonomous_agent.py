#!/usr/bin/env python3
"""
Autonomous Cognitive Agent - Автономный AI-агент

Запускается при открытии проекта и работает в фоновом режиме:
- Сканирует код и архитектуру
- Анализирует зависимости и проблемы
- Предлагает улучшения
- Автоматически выполняет задачи (с подтверждением)

Интеграция с AI Provider Manager:
- Primary: GigaChat (облако)
- Fallback: Ollama (локально)
"""

import json
import logging
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any

# Добавляем корень проекта в PATH
REPO_ROOT = Path(__file__).parent.parent.parent

from agents.cognitive_agent.src.project_scanner import ProjectScanner
from apps.ai_config_manager.src.ai_config_manager.config_manager import ConfigManager
from apps.ai_provider_manager.src.ai_provider_manager import (
    chat_with_fallback,
    get_provider_manager,
)
from apps.it_compass.src.it_compass_scanner import get_scanner

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(REPO_ROOT / "logs" / "cognitive_agent.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class AutonomousCognitiveAgent:
    """
    Автономный когнитивный агент

    Работает в фоне и:
    1. Сканирует проект при запуске
    2. Анализирует код и архитектуру
    3. Предлагает улучшения
    4. Выполняет задачи (с подтверждением)
    """

    def __init__(self, project_path: str = None):
        self.project_path = Path(project_path) if project_path else REPO_ROOT
        self.agent_id = f"agent-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        self.running = False
        self.scan_interval = 1800  # 30 минут (экономия ресурсов)
        self.last_scan: datetime | None = None

        # Инициализация
        config_path = self.project_path / "apps" / "cognitive_agent" / "config" / "agent-config.yaml"
        self.config = ConfigManager(str(config_path)) if config_path.exists() else None
        self.ai_manager = get_provider_manager()

        # Результаты сканирования
        self.scan_results: dict[str, Any] = {}
        self.recommendations: list[dict[str, Any]] = []

        logger.info(f"🚀 Agent initialized: {self.agent_id}")
        logger.info(f"📁 Project path: {self.project_path}")

    def start(self, background: bool = True):
        """Запустить агента"""
        if self.running:
            logger.warning("Agent already running")
            return

        self.running = True
        logger.info("🟢 Agent started")

        if background:
            # Запуск в фоновом потоке
            thread = threading.Thread(target=self._background_loop, daemon=True)
            thread.start()
        else:
            # Запуск в главном потоке
            self._background_loop()

    def stop(self):
        """Остановить агента"""
        self.running = False
        logger.info("🔴 Agent stopped")

    def _background_loop(self):
        """Фоновый цикл работы"""
        logger.info("🔄 Background loop started")

        # Первое сканирование
        self.scan_project()

        while self.running:
            try:
                time.sleep(self.scan_interval)

                if self.running:
                    logger.info(f"📊 Periodic scan #{len(self.scan_results) + 1}")
                    self.scan_project()

            except Exception as e:
                logger.error(f"Error in background loop: {e}")

    def scan_project(self, mode: str = "auto"):
        """
        Сканировать проект

        Args:
            mode: Режим сканирования
                - "auto": автоматический (git diff если есть изменения, иначе skip)
                - "git_diff": только изменённые файлы
                - "full": полное сканирование
                - "paths": выборочное (конфигурируется в self.scan_paths)
        """
        logger.info(f"🔍 Сканирование проекта: {self.project_path} (режим: {mode})")

        scan_start = datetime.now()

        # 1. Инициализация проектного сканера
        project_scanner = ProjectScanner(str(self.project_path))

        # 2. Выбор режима сканирования
        if mode == "auto":
            # Пробуем git diff, если пусто — пропускаем
            git_results = project_scanner.scan_git_diff()
            if git_results["scanned_files"] == 0:
                logger.info("✅ Нет изменённых файлов. Пропуск сканирования.")
                # Всё равно запускаем IT Compass для прогресса
                compass_results = self._run_compass_scan()
                self.scan_results = {
                    "mode": "auto",
                    "timestamp": scan_start.isoformat(),
                    "agent_id": self.agent_id,
                    "project_path": str(self.project_path),
                    "incremental": git_results,
                    "it_compass": compass_results,
                    "status": "no_changes",
                }
                return self.scan_results
            # Если есть изменения — продолжаем с ними
            scan_data = git_results
        elif mode == "git_diff":
            scan_data = project_scanner.scan_git_diff()
        elif mode == "full":
            scan_data = project_scanner.scan_full()
        elif mode == "paths":
            paths = getattr(self, "scan_paths", ["apps/", "apps/cognitive_agent/"])
            scan_data = project_scanner.scan_paths(paths)
        else:
            logger.warning(f"Неизвестный режим: {mode}, используем auto")
            scan_data = project_scanner.scan_git_diff()

        # 3. Сканирование IT Compass (маркеры компетенций)
        logger.info("🧭 Running IT Compass scan...")
        compass_results = self._run_compass_scan()

        # 4. Сбор метаданных проекта
        self.scan_results = {
            "mode": mode,
            "timestamp": scan_start.isoformat(),
            "agent_id": self.agent_id,
            "project_path": str(self.project_path),
            "incremental": scan_data,
            "files": scan_data.get("scanned_files", 0),
            "it_compass": compass_results,
            "issues": self._detect_issues_from_scan(scan_data),
            "recommendations": self._generate_recommendations(),
        }

        self.last_scan = scan_start

        logger.info(f"✅ Scan completed in {(datetime.now() - scan_start).total_seconds():.2f}s")
        logger.info(f"   Mode: {mode}")
        logger.info(f"   Files scanned: {self.scan_results['files']}")
        if compass_results:
            logger.info(
                f"   IT Compass markers: {compass_results.get('markers_detected', 0)}/{compass_results.get('markers_total', 0)}"
            )

        # Сохранение результатов
        self._save_scan_results()

        return self.scan_results

    def _run_compass_scan(self):
        """Запустить сканирование IT Compass"""
        try:
            compass_scanner = get_scanner()
            return compass_scanner.scan_project()
        except Exception as e:
            logger.error(f"IT Compass scan failed: {e}")
            return None

    def _detect_issues_from_scan(self, scan_data: dict) -> list[dict[str, str]]:
        """Обнаружить проблемы на основе данных сканирования"""
        issues = []

        # Анализ изменённых файлов
        for file_info in scan_data.get("files", []):
            # Проверка на большие файлы
            if file_info.get("size", 0) > 1_000_000:
                issues.append(
                    {
                        "type": "large_file",
                        "path": file_info["path"],
                        "message": f"Большой файл: {file_info['size'] / 1_000_000:.1f} MB",
                    }
                )

        return issues

    def _count_files(self) -> int:
        """Подсчитать количество файлов"""
        count = 0
        for _ in self.project_path.rglob("*"):
            if _.is_file() and not self._is_excluded(_):
                count += 1
        return count

    def _count_directories(self) -> int:
        """Подсчитать количество директорий"""
        count = 0
        for _ in self.project_path.rglob("*"):
            if _.is_dir() and not self._is_excluded(_):
                count += 1
        return count

    def _is_excluded(self, path: Path) -> bool:
        """Проверить, исключён ли путь"""
        excluded_dirs = [".git", ".venv", "__pycache__", "node_modules", ".pytest_cache"]
        return any(part in excluded_dirs for part in path.parts)

    def _detect_languages(self) -> dict[str, int]:
        """Определить языки программирования"""
        languages = {}
        extensions = {
            ".py": "Python",
            ".js": "JavaScript",
            ".ts": "TypeScript",
            ".json": "JSON",
            ".yaml": "YAML",
            ".yml": "YAML",
            ".md": "Markdown",
            ".ps1": "PowerShell",
            ".sh": "Bash",
        }

        for file in self.project_path.rglob("*"):
            if file.is_file() and not self._is_excluded(file):
                ext = file.suffix.lower()
                if ext in extensions:
                    lang = extensions[ext]
                    languages[lang] = languages.get(lang, 0) + 1

        return languages

    def _detect_frameworks(self) -> list[str]:
        """Определить используемые фреймворки"""
        frameworks = []

        # Проверка по файлам
        if (self.project_path / "package.json").exists():
            frameworks.append("Node.js")

        if (self.project_path / "requirements.txt").exists():
            frameworks.append("Python")

        if (self.project_path / "docker-compose.yml").exists():
            frameworks.append("Docker")

        if (self.project_path / "pytest.ini").exists():
            frameworks.append("Pytest")

        return frameworks

    def _detect_issues(self) -> list[dict[str, str]]:
        """Обнаружить проблемы"""
        issues = []

        # Проверка на большие файлы
        for file in self.project_path.rglob("*.py"):
            if file.is_file() and not self._is_excluded(file):
                try:
                    size = file.stat().st_size
                    if size > 1_000_000:  # > 1MB
                        issues.append(
                            {
                                "type": "large_file",
                                "path": str(file.relative_to(self.project_path)),
                                "message": f"Файл слишком большой: {size / 1_000_000:.1f} MB",
                            }
                        )
                except:
                    pass

        # Проверка на TODO комментарии
        for file in self.project_path.rglob("*.py"):
            if file.is_file() and not self._is_excluded(file):
                try:
                    content = file.read_text(encoding="utf-8")
                    todos = [line for line in content.split("\n") if "TODO" in line]
                    if todos:
                        issues.append(
                            {
                                "type": "todos",
                                "path": str(file.relative_to(self.project_path)),
                                "message": f"Найдено TODO: {len(todos)}",
                            }
                        )
                except:
                    pass

        return issues

    def _generate_recommendations(self) -> list[dict[str, str]]:
        """Сгенерировать рекомендации через AI"""
        recommendations = []

        # Если AI недоступен, используем простые правила
        if not self.ai_manager.get_active_provider():
            logger.warning("AI provider not available, using simple rules")

            if len(self.scan_results.get("issues", [])) > 5:
                recommendations.append(
                    {
                        "priority": "high",
                        "category": "code_quality",
                        "message": "Много проблем в коде. Рекомендуется рефакторинг.",
                    }
                )

            if self.scan_results.get("files", 0) > 1000:
                recommendations.append(
                    {
                        "priority": "medium",
                        "category": "architecture",
                        "message": "Проект большой. Рассмотрите модульную архитектуру.",
                    }
                )

            return recommendations

        # Используем AI для генерации рекомендаций
        try:
            languages = ", ".join(self.scan_results.get("languages", {}).keys())
            issues_count = len(self.scan_results.get("issues", []))

            prompt = f"""
Анализ проекта:
- Языки: {languages}
- Проблем найдено: {issues_count}

Предложи 3-5 конкретных рекомендаций по улучшению кода и архитектуры.
Формат: JSON массив с полями: priority (high/medium/low), category, message.
"""

            response = chat_with_fallback(
                [
                    {"role": "system", "content": "Ты — эксперт по анализу кода и архитектуры."},
                    {"role": "user", "content": prompt},
                ]
            )

            if response:
                # Пытаемся распарсить JSON
                try:
                    import re

                    json_match = re.search(r"\[.*\]", response, re.DOTALL)
                    if json_match:
                        ai_recommendations = json.loads(json_match.group())
                        recommendations.extend(ai_recommendations)
                except:
                    logger.warning("Failed to parse AI recommendations")

        except Exception as e:
            logger.error(f"Error generating AI recommendations: {e}")

        return recommendations

    def _save_scan_results(self):
        """Сохранить результаты сканирования"""
        output_dir = self.project_path / "cognitive_agent" / "scans"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Сохранение в JSON
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        scan_file = output_dir / f"scan_{timestamp}.json"

        with open(scan_file, "w", encoding="utf-8") as f:
            json.dump(self.scan_results, f, indent=2, ensure_ascii=False)

        # Обновление последнего скана
        last_scan_file = output_dir / "last_scan.json"
        with open(last_scan_file, "w", encoding="utf-8") as f:
            json.dump(self.scan_results, f, indent=2, ensure_ascii=False)

        logger.info(f"💾 Scan results saved: {scan_file}")

    def get_status(self) -> dict[str, Any]:
        """Получить статус агента"""
        return {
            "agent_id": self.agent_id,
            "running": self.running,
            "project_path": str(self.project_path),
            "last_scan": self.last_scan.isoformat() if self.last_scan else None,
            "scan_interval_seconds": self.scan_interval,
            "ai_provider": self.ai_manager.get_active_provider(),
            "ai_providers_status": self.ai_manager.get_status(),
            "total_scans": len(self.scan_results),
            "total_recommendations": len(self.recommendations),
        }

    def execute_task(self, task: str, auto_approve: bool = False) -> dict[str, Any]:
        """
        Выполнить задачу через AI

        Args:
            task: Описание задачи
            auto_approve: Автоматически выполнять без подтверждения

        Returns:
            Результат выполнения
        """
        logger.info(f"📝 Task received: {task}")

        # Генерация плана через AI
        plan_prompt = f"""
Задача: {task}

Предложи пошаговый план выполнения:
1. Анализ текущего состояния
2. Необходимые изменения
3. Тестирование
4. Документация

Формат: JSON с полями steps (массив), estimated_time, risk_level.
"""

        plan_response = chat_with_fallback(
            [
                {"role": "system", "content": "Ты — помощник по выполнению задач в коде."},
                {"role": "user", "content": plan_prompt},
            ]
        )

        if not plan_response:
            return {"status": "error", "message": "AI не доступен"}

        # Проверка подтверждения
        if not auto_approve:
            print("\n🤖 Предложен план выполнения задачи:")
            print(plan_response)
            print("\nВыполнить? (y/n): ", end="")
            response = input().lower()
            if response != "y":
                return {"status": "cancelled", "message": "Пользователь отменил"}

        # Выполнение задачи (упрощённая версия)
        return {
            "status": "success",
            "task": task,
            "plan": plan_response,
            "message": "Задача запланирована (полное выполнение требует дополнительных прав)",
        }


# Глобальный экземпляр
_agent: AutonomousCognitiveAgent | None = None


def get_agent() -> AutonomousCognitiveAgent:
    """Получить глобальный экземпляр агента"""
    global _agent
    if _agent is None:
        _agent = AutonomousCognitiveAgent()
    return _agent


def start_agent(project_path: str = None, background: bool = True):
    """Запустить агента"""
    agent = get_agent()
    agent.start(background=background)
    return agent


def stop_agent():
    """Остановить агента"""
    global _agent
    if _agent:
        _agent.stop()
        _agent = None


if __name__ == "__main__":
    # CLI интерфейс
    import argparse

    parser = argparse.ArgumentParser(description="Autonomous Cognitive Agent")
    parser.add_argument("--start", action="store_true", help="Запустить агента")
    parser.add_argument("--stop", action="store_true", help="Остановить агента")
    parser.add_argument("--status", action="store_true", help="Показать статус")
    parser.add_argument("--scan", action="store_true", help="Запустить сканирование")
    parser.add_argument("--project", type=str, help="Путь к проекту")
    parser.add_argument("--foreground", action="store_true", help="Запуск в foreground")

    args = parser.parse_args()

    if args.start:
        agent = start_agent(project_path=args.project, background=not args.foreground)
        print(f"✅ Agent started: {agent.agent_id}")

        if args.foreground:
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🔴 Stopping...")
                stop_agent()

    elif args.stop:
        stop_agent()
        print("✅ Agent stopped")

    elif args.status:
        agent = get_agent()
        status = agent.get_status()
        print(json.dumps(status, indent=2, ensure_ascii=False))

    elif args.scan:
        agent = get_agent()
        results = agent.scan_project()
        print(f"✅ Scan completed: {len(results.get('recommendations', []))} recommendations")

    else:
        parser.print_help()
