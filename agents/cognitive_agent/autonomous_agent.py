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

Этот файл - main entry point, остальная логика вынесена в модули:
- core/ - базовые классы
- security/ - guardrails
- integrations/ - внешние интеграции
- monitoring/ - метрики и логи
"""

import asyncio
import datetime
import json
import re
from pathlib import Path
from typing import Any


# Импорты из новых модулей
from agents.cognitive_agent.core.base_agent import get_agent_data_dir, get_repo_root
from agents.cognitive_agent.integrations import AIProviderIntegration, JobAgentIntegration
from agents.cognitive_agent.monitoring.audit_logger import AuditLogger
from agents.cognitive_agent.monitoring.metrics import MetricsCollector
from agents.cognitive_agent.self_testing_module import SelfTestingModule
from agents.cognitive_agent.src.base_agent import BaseCognitiveAgent
from agents.cognitive_agent.src.logging_config import logger, structured_logger
from agents.cognitive_agent.src.project_scanner import ProjectScanner

# ⭐ [HYBRID] Prompt Engine
from agents.cognitive_agent.src.prompt_engine import PromptEngine

# Добавляем корень проекта в PATH
REPO_ROOT = get_repo_root()
AGENT_DATA_DIR = get_agent_data_dir()


class AutonomousCognitiveAgent(BaseCognitiveAgent):
    """
    Автономный когнитивный агент

    Работает в фоне и:
    1. Сканирует проект при запуске
    2. Анализирует код и архитектуру
    3. Предлагает улучшения
    4. Выполняет задачи (с подтверждением)
    """

    def __init__(self, project_path: str = None):
        super().__init__(project_path)
        logger.info(f"🚀 Autonomous Agent initialized: {self.agent_id}")

        # ⭐ [ENTERPRISE] Initialize Metrics Collector
        self.metrics_collector = MetricsCollector()
        logger.info("✅ Metrics collector initialized")

        # ⭐ [ENTERPRISE] Initialize Audit Logger
        self.audit_logger = AuditLogger(
            agent_id=self.agent_id,
            structured_logger=structured_logger,
        )
        logger.info("✅ Audit logger initialized")

        # ⭐ [ENTERPRISE] Initialize AI Provider Integration
        self.ai_provider = AIProviderIntegration()
        logger.info("✅ AI provider integration initialized")

        # ⭐ [ENTERPRISE] Initialize Job Agent Integration
        self.job_agent = JobAgentIntegration()
        if self.job_agent.is_available():
            logger.info("✅ Job agent integration available")
        else:
            logger.warning("⚠️ Job agent not available (optional dependency)")

        # ⭐ [HYBRID] Initialize Prompt Engine (Layer 2: Strategy Manager)
        prompts_dir = Path(__file__).parent / "prompts"
        self.prompt_engine = PromptEngine(prompts_dir=prompts_dir, llm_client=None)
        logger.info(f"✅ Prompt engine initialized: {prompts_dir}")

        # Инициализация модуля самотестирования
        self.project_scanner = ProjectScanner(str(self.project_path))
        self.self_testing_module = SelfTestingModule(
            project_scanner=self.project_scanner,
            code_analyzer=self._get_code_analyzer(),
            test_analyzer=self._get_test_analyzer(),
            task_planner=None,
            logger=logger,
        )

    def _get_code_analyzer(self):
        """Получить code_analyzer (ленивая инициализация)"""
        try:
            from agents.cognitive_agent.src.code_analyzer import CodeAnalyzer

            return CodeAnalyzer(str(self.project_path))
        except ImportError:
            return None

    def _get_test_analyzer(self):
        """Получить test_analyzer (ленивая инициализация)"""
        try:
            from agents.cognitive_agent.src.test_analyzer import TestAnalyzer

            return TestAnalyzer(str(self.project_path))
        except ImportError:
            return None

    # Реализация абстрактных методов из BaseCognitiveAgent

    def start(self, background: bool = True):
        """Запустить агента

        Args:
            background: Запустить в фоновом режиме
        """
        if self.running:
            logger.warning("Agent is already running")
            return

        self.running = True
        # Сохранение handle для graceful shutdown
        self._periodic_scan_task = getattr(self, "_periodic_scan_task", None)
        self.audit_logger.log_action("agent_started", {"background": background})

        logger.info(f"🚀 Autonomous Agent started in {'background' if background else 'foreground'} mode")

        # Запуск сканирования при старте
        if background:
            # В фоновом режиме запускаем периодическое сканирование
            if (
                getattr(self, "_periodic_scan_task", None) is None
                or getattr(self._periodic_scan_task, "done", lambda: True)()
            ):
                self._periodic_scan_task = asyncio.create_task(self._run_periodic_scan())
        else:
            # В foreground режиме выполняем одно сканирование
            self.scan_project(mode="auto")

    def stop(self):
        """Остановить агента (graceful shutdown)."""
        if not self.running:
            logger.warning("Agent is not running")
            return

        self.running = False

        task = getattr(self, "_periodic_scan_task", None)
        if task is not None and not task.done():
            task.cancel()

        self.audit_logger.log_action("agent_stopped", {})
        logger.info(f"🛑 Autonomous Agent stopped: {self.agent_id}")

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
        logger.info(f"🔍 Scanning project in '{mode}' mode")

        try:
            # Используем project_scanner для анализа
            if self.project_scanner:
                self.scan_results = self.project_scanner.scan_project(mode)
                self.last_scan = datetime.datetime.now()

                # Обнаружить проблемы
                self.recommendations = self._detect_issues_from_scan(self.scan_results)

                # Сохранить результаты
                self._save_scan_results()

                logger.info(f"✅ Project scan complete: {len(self.scan_results.get('files', []))} files analyzed")
                self.audit_logger.log_action(
                    "scan_completed",
                    {
                        "mode": mode,
                        "files_scanned": len(self.scan_results.get("files", [])),
                        "issues_found": len(self.recommendations),
                    },
                )
        except Exception as e:
            logger.error(f"❌ Scan failed: {e}")
            self.audit_logger.log_action("scan_failed", {"mode": mode, "error": str(e)}, "failed")
            raise

    def execute_task(self, task: str, auto_approve: bool = False) -> dict[str, Any]:
        """
        Выполнить задачу через AI — **с проверкой guardrails**

        Args:
            task: Описание задачи
            auto_approve: Автоматическое одобрение безопасных задач

        Returns:
            dict[str, Any]: Результат выполнения
        """
        # Валидация задачи
        is_valid, validation_msg = self._validate_task(task)
        if not is_valid:
            logger.error(f"❌ Task validation failed: {validation_msg}")
            self.audit_logger.log_action(
                "task_rejected", {"task_preview": task[:100], "reason": validation_msg}, "blocked"
            )
            return {"success": False, "error": validation_msg}

        # Проверка guardrails
        try:
            # Проверка rate limiting
            self._check_rate_limit()

            logger.info(f"⚡ Executing task: {task[:100]}...")
            self.audit_logger.log_action(
                "task_execution_started", {"task_preview": task[:100], "auto_approve": auto_approve}
            )

            # Генерация решения через AI
            response = self._call_ai_with_timeout(
                prompt=task,
                system_message="Ты — автономный когнитивный агент. Предложи конкретное решение задачи. Формат: JSON с полями: action, description, files_to_modify.",
            )

            if response is None:
                return {"success": False, "error": "AI timeout or error", "task": task}

            # Валидация AI-ответа
            is_safe, safety_msg = self._validate_ai_response(response)
            if not is_safe:
                logger.error(f"🚫 AI response blocked: {safety_msg}")
                return {"success": False, "error": safety_msg, "task": task}

            # Парсинг ответа (strict-ish)
            try:
                # Сначала пытаемся распарсить ответ целиком как JSON
                response_stripped = response.strip()
                solution: dict[str, Any]

                if response_stripped.startswith("{") and response_stripped.endswith("}"):
                    solution = json.loads(response_stripped)
                else:
                    # Если модель вернула обёртку/текст — извлекаем первое JSON-объектное содержимое
                    start = response_stripped.find("{")
                    end = response_stripped.rfind("}")
                    if start == -1 or end == -1 or end <= start:
                        raise json.JSONDecodeError("No JSON object found", response_stripped, 0)
                    solution = json.loads(response_stripped[start : end + 1])

                # Минимальная валидация схемы (production hardening)
                action = solution.get("action") if isinstance(solution, dict) else None
                description = solution.get("description") if isinstance(solution, dict) else None

                if not action or not isinstance(action, str):
                    raise ValueError("Missing/invalid 'action' in AI solution")
                if not description or not isinstance(description, str):
                    # В fallback не ломаем — но фиксируем как текстовый ответ
                    solution = {"action": action, "description": str(description) if description is not None else ""}

                self._remember_decision({"task": task}, action, "success")
                logger.info(f"✅ Solution generated: {action}")

            except Exception as parse_exc:
                logger.warning(f"AI solution parsing failed: {parse_exc}")
                solution = {"action": "text_response", "description": response}

            # Сохранение результата
            self.audit_logger.log_action(
                "task_completed", {"task_preview": task[:100], "action": solution.get("action", "unknown")}, "success"
            )

            return {"success": True, "solution": solution, "task": task}

        except Exception as e:
            logger.error(f"❌ Task execution failed: {e}")
            self.audit_logger.log_action("task_failed", {"task_preview": task[:100], "error": str(e)}, "failed")
            return {"success": False, "error": str(e), "task": task}

    async def _run_periodic_scan(self):
        """Периодическое сканирование в фоновом режиме"""
        while self.running:
            try:
                await asyncio.sleep(self.scan_interval)
                self.scan_project(mode="auto")
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Periodic scan failed: {e}")
                await asyncio.sleep(60)  # Подождать перед повтором


def main():
    """Main entry point"""
    agent = AutonomousCognitiveAgent()
    agent.start(background=True)
    logger.info("Autonomous Agent started")


if __name__ == "__main__":
    main()
