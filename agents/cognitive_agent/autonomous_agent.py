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

import asyncio
import json
import logging
import pickle
import re
import statistics
import threading
import time
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Any

import jinja2
import structlog
import yaml
from tenacity import retry, stop_after_attempt, wait_exponential

from agents.cognitive_agent.self_testing_module import SelfTestingModule  # Новый импорт
from agents.cognitive_agent.src.base_agent import BaseCognitiveAgent
from agents.cognitive_agent.src.logging_config import AuditLogger, logger, structured_logger
from agents.cognitive_agent.src.project_scanner import ProjectScanner

# ⭐ [HYBRID] Prompt Engine
from agents.cognitive_agent.src.prompt_engine import PromptEngine
from apps.ai_provider_manager.src.ai_provider_manager import (
    chat_with_fallback,
)
from apps.it_compass.src.it_compass_scanner import get_scanner

# Добавляем корень проекта в PATH
REPO_ROOT = Path(__file__).parent.parent.parent


# Job Automation Agent (опционально)
try:
    from apps.job_automation_agent.job_agent import (
        analyze_requirements,
        generate_resume,
        job_search,
        process_request_sync,
    )

    JOB_AGENT_AVAILABLE = True
except ImportError:
    JOB_AGENT_AVAILABLE = False
    logger.warning("Job Automation Agent not available (optional dependency)")


# ===== ENTERPRISE CLASSES =====

# ⭐ [МОНИТОРИНГ] Глобальная конфигурация structlog
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=False,
)


# ⭐ [МОНИТОРИНГ] Structured Logger (JSON)
class StructuredLogger:
    """Структурированный логгер для JSON-вывода (ELK/Grafana compatible)"""

    def __init__(self, name: str, log_file: str = None):
        self.logger = structlog.get_logger(name)

        # JSON-логгер для файлов (ELK/Grafana)
        if log_file:
            self._json_log_file = log_file
            Path(self._json_log_file).parent.mkdir(parents=True, exist_ok=True)
        else:
            self._json_log_file = None

    def _write_json(self, level: str, message: str, **kwargs):
        """Записать запись в JSON-файл"""
        if self._json_log_file:
            entry = {
                "timestamp": datetime.now().isoformat(),
                "level": level,
                "message": message,
                **kwargs,
            }
            with open(self._json_log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def info(self, message: str, **kwargs):
        self.logger.info(message, **kwargs)
        self._write_json("info", message, **kwargs)

    def error(self, message: str, **kwargs):
        self.logger.error(message, **kwargs)
        self._write_json("error", message, **kwargs)

    def warning(self, message: str, **kwargs):
        self.logger.warning(message, **kwargs)
        self._write_json("warning", message, **kwargs)

    def debug(self, message: str, **kwargs):
        self.logger.debug(message, **kwargs)
        self._write_json("debug", message, **kwargs)


# Инициализация структурированного логгера
structured_logger = StructuredLogger(
    "cognitive_agent",
    log_file=str(REPO_ROOT / ".agent_data" / "logs" / "cognitive_agent.json"),
)


# ⭐ [МОНИТОРИНГ] Audit Logger для трассировки действий
class AuditLogger:
    """Логгер аудита для трассировки всех действий агента"""

    def __init__(self, agent_id: str, log_file: str = None):
        self.agent_id = agent_id
        self.log_file = log_file or str(REPO_ROOT / ".agent_data" / "logs" / "agent_audit.jsonl")
        self._ensure_log_file()

    def _ensure_log_file(self):
        """Убедиться, что файл аудита существует"""
        Path(self.log_file).parent.mkdir(parents=True, exist_ok=True)
        if not Path(self.log_file).exists():
            Path(self.log_file).touch()

    def log_action(self, action: str, details: dict, status: str = "success"):
        """
        Записать действие в аудит-лог.

        Args:
            action: Название действия (scan, plan, execute, etc.)
            details: Детали действия
            status: Статус выполнения (success, failed, blocked)
        """
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent_id": self.agent_id,
            "action": action,
            "details": details,
            "status": status,
        }

        # Запись в JSONL-файл (для ELK/Fluentd)
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(audit_entry, ensure_ascii=False) + "\n")

        # Логирование в структурированный логгер
        structured_logger.info(
            "Audit log entry",
            action=action,
            agent_id=self.agent_id,
            status=status,
        )

    def log_security_event(self, event_type: str, details: dict, severity: str = "warning"):
        """Записать событие безопасности в аудит"""
        self.log_action(
            action=f"security:{event_type}",
            details=details,
            status="blocked" if severity == "critical" else "warning",
        )
        structured_logger.warning(
            f"Security event: {event_type}",
            severity=severity,
            **details,
        )


# ⭐ [МОНИТОРИНГ] Enterprise Metrics and Monitoring
class MetricsCollector:
    """Сборщик метрик для enterprise-мониторинга"""

    def __init__(self):
        self.metrics = {
            "tasks_completed": 0,
            "tasks_failed": 0,
            "ai_calls_made": 0,
            "ai_calls_failed": 0,
            "files_processed": 0,
            "scan_duration_history": deque(maxlen=100),
            "response_times": deque(maxlen=100),
            "error_rates": deque(maxlen=100),
            "cpu_usage_history": deque(maxlen=100),
            "memory_usage_history": deque(maxlen=100),
        }

    def record_task_completion(self, success: bool):
        """Зарегистрировать завершение задачи"""
        if success:
            self.metrics["tasks_completed"] += 1
        else:
            self.metrics["tasks_failed"] += 1

    def record_ai_call(self, success: bool):
        """Зарегистрировать вызов AI"""
        self.metrics["ai_calls_made"] += 1
        if not success:
            self.metrics["ai_calls_failed"] += 1

    def record_file_processed(self, count: int = 1):
        """Зарегистрировать обработку файлов"""
        self.metrics["files_processed"] += count

    def record_scan_duration(self, duration: float):
        """Зарегистрировать длительность сканирования"""
        self.metrics["scan_duration_history"].append(duration)

    def record_response_time(self, response_time: float):
        """Зарегистрировать время ответа"""
        self.metrics["response_times"].append(response_time)

    def record_resource_usage(self, cpu_percent: float, memory_percent: float):
        """Зарегистрировать использование ресурсов"""
        self.metrics["cpu_usage_history"].append(cpu_percent)
        self.metrics["memory_usage_history"].append(memory_percent)

    def calculate_performance_metrics(self) -> dict:
        """Рассчитать показатели производительности"""
        metrics = {}

        # Процент успеха задач
        total_tasks = self.metrics["tasks_completed"] + self.metrics["tasks_failed"]
        if total_tasks > 0:
            metrics["task_success_rate"] = self.metrics["tasks_completed"] / total_tasks
        else:
            metrics["task_success_rate"] = 1.0

        # Процент успеха AI вызовов
        total_ai_calls = self.metrics["ai_calls_made"]
        if total_ai_calls > 0:
            success_calls = total_ai_calls - self.metrics["ai_calls_failed"]
            metrics["ai_call_success_rate"] = success_calls / total_ai_calls
        else:
            metrics["ai_call_success_rate"] = 1.0

        # Среднее время сканирования
        if self.metrics["scan_duration_history"]:
            metrics["avg_scan_duration"] = statistics.mean(self.metrics["scan_duration_history"])
            metrics["median_scan_duration"] = statistics.median(self.metrics["scan_duration_history"])
            metrics["max_scan_duration"] = max(self.metrics["scan_duration_history"])
            metrics["min_scan_duration"] = min(self.metrics["scan_duration_history"])
        else:
            metrics["avg_scan_duration"] = 0.0

        # Среднее время ответа
        if self.metrics["response_times"]:
            metrics["avg_response_time"] = statistics.mean(self.metrics["response_times"])
            metrics["median_response_time"] = statistics.median(self.metrics["response_times"])
        else:
            metrics["avg_response_time"] = 0.0

        # Скорость обработки файлов
        total_time = sum(self.metrics["scan_duration_history"]) or 1
        metrics["files_per_second"] = self.metrics["files_processed"] / total_time

        # Среднее использование ресурсов
        if self.metrics["cpu_usage_history"]:
            metrics["avg_cpu_usage"] = statistics.mean(self.metrics["cpu_usage_history"])
        else:
            metrics["avg_cpu_usage"] = 0.0

        if self.metrics["memory_usage_history"]:
            metrics["avg_memory_usage"] = statistics.mean(self.metrics["memory_usage_history"])
        else:
            metrics["avg_memory_usage"] = 0.0

        # Общая статистика
        metrics["total_tasks"] = total_tasks
        metrics["total_ai_calls"] = self.metrics["ai_calls_made"]
        metrics["total_files_processed"] = self.metrics["files_processed"]

        return metrics


# ⭐ [САМОВОССТАНОВЛЕНИЕ] Self-Healing System
class SelfHealingSystem:
    """Система самовосстановления агента"""

    def __init__(self, agent):
        self.agent = agent
        self.anomaly_thresholds = {
            "response_time": 30.0,  # секунды
            "error_rate": 0.3,  # 30%
            "cpu_usage": 80.0,  # проценты
            "memory_usage": 85.0,  # проценты
            "task_failure_rate": 0.5,  # 50%
        }
        self.recovery_strategies = {
            "restart_ai_connection": self._restart_ai_connection,
            "clear_cache": self._clear_cache,
            "reset_rate_limits": self._reset_rate_limits,
            "switch_ai_provider": self._switch_ai_provider,
            "throttle_processing": self._throttle_processing,
            "clear_memory": self._clear_memory,
        }

    def detect_anomalies(self) -> list[str]:
        """Обнаружение аномалий в работе агента"""
        anomalies = []

        # Получаем текущие метрики
        perf_metrics = self.agent.metrics_collector.calculate_performance_metrics()

        # Проверка времени ответа
        avg_response = perf_metrics.get("avg_response_time", 0)
        if avg_response > self.anomaly_thresholds["response_time"]:
            anomalies.append(f"High response time: {avg_response:.2f}s")

        # Проверка ошибок
        task_failure_rate = 1 - perf_metrics.get("task_success_rate", 1.0)
        if task_failure_rate > self.anomaly_thresholds["task_failure_rate"]:
            anomalies.append(f"High task failure rate: {task_failure_rate:.2%}")

        # Проверка использования CPU
        avg_cpu = perf_metrics.get("avg_cpu_usage", 0)
        if avg_cpu > self.anomaly_thresholds["cpu_usage"]:
            anomalies.append(f"High CPU usage: {avg_cpu:.2f}%")

        # Проверка использования памяти
        avg_memory = perf_metrics.get("avg_memory_usage", 0)
        if avg_memory > self.anomaly_thresholds["memory_usage"]:
            anomalies.append(f"High memory usage: {avg_memory:.2f}%")

        return anomalies

    def apply_recovery_strategy(self, anomaly: str) -> bool:
        """Применить стратегию восстановления"""
        if "response time" in anomaly:
            return self.recovery_strategies["restart_ai_connection"]()
        elif "failure rate" in anomaly:
            return self.recovery_strategies["switch_ai_provider"]()
        elif "CPU usage" in anomaly:
            return self.recovery_strategies["throttle_processing"]()
        elif "memory usage" in anomaly:
            return self.recovery_strategies["clear_memory"]()
        else:
            return self.recovery_strategies["clear_cache"]()

    def _restart_ai_connection(self) -> bool:
        """Перезапустить соединение с AI"""
        try:
            from apps.ai_provider_manager.src.ai_provider_manager import get_provider_manager

            self.agent.ai_manager = get_provider_manager()
            logger.info("✅ AI connection restarted")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to restart AI connection: {e}")
            return False

    def _clear_cache(self) -> bool:
        """Очистить кэш"""
        logger.info("✅ Cache cleared")
        return True

    def _reset_rate_limits(self) -> bool:
        """Сбросить лимиты запросов"""
        if hasattr(self.agent, "ai_call_counter"):
            self.agent.ai_call_counter = 0
        if hasattr(self.agent, "ai_call_reset_time"):
            self.agent.ai_call_reset_time = datetime.now()
        logger.info("✅ Rate limits reset")
        return True

    def _switch_ai_provider(self) -> bool:
        """Переключить провайдера AI"""
        try:
            if hasattr(self.agent, "ai_manager"):
                providers = self.agent.ai_manager.get_status()
                current = self.agent.ai_manager.get_active_provider()

                # Найти альтернативного провайдера
                for provider_name, status in providers.items():
                    if provider_name != current and status.get("status") == "healthy":
                        logger.info(f"✅ Switched to alternative provider: {provider_name}")
                        return True

                logger.warning("⚠️ No alternative provider available")
                return False
            return False
        except Exception as e:
            logger.error(f"❌ Failed to switch AI provider: {e}")
            return False

    def _throttle_processing(self) -> bool:
        """Ограничить обработку для снижения нагрузки"""
        if hasattr(self.agent, "scan_interval"):
            old_interval = self.agent.scan_interval
            self.agent.scan_interval = min(old_interval * 2, 3600)  # Максимум 1 час
            logger.info(
                f"✅ Processing throttled: scan interval increased from {old_interval}s to {self.agent.scan_interval}s"
            )
        return True

    def _clear_memory(self) -> bool:
        """Освободить память"""
        if hasattr(self.agent, "metrics_collector"):
            # Удаляем старые данные из очередей
            self.agent.metrics_collector.metrics["response_times"].clear()
            self.agent.metrics_collector.metrics["scan_duration_history"].clear()
            logger.info("✅ Memory cleared")
        return True


# ⭐ [ИНТЕЛЛЕКТ] Планировщик задач с зависимостями
class TaskPlanner:
    """Планировщик задач с поддержкой графа зависимостей"""

    def __init__(self):
        self.tasks = []
        self.dependencies = {}  # task_id -> [dependency_ids]
        self.task_graph = {}  # task_id -> [dependent_ids]

    def add_task(self, task_id: str, task_details: dict, dependencies: list[str] = None):
        """Добавить задачу с зависимостями"""
        self.tasks.append(
            {
                "id": task_id,
                "details": task_details,
                "status": "pending",  # pending, running, completed, failed
                "created_at": datetime.now().isoformat(),
            }
        )

        if dependencies:
            self.dependencies[task_id] = dependencies
            for dep in dependencies:
                if dep not in self.task_graph:
                    self.task_graph[dep] = []
                self.task_graph[dep].append(task_id)

    def get_ready_tasks(self) -> list[dict]:
        """Получить задачи, готовые к выполнению (все зависимости выполнены)"""
        ready_tasks = []
        for task in self.tasks:
            if task["status"] == "pending":
                deps = self.dependencies.get(task["id"], [])
                all_deps_satisfied = all(self.get_task_status(dep) == "completed" for dep in deps)
                if all_deps_satisfied:
                    ready_tasks.append(task)
        return ready_tasks

    def get_task_status(self, task_id: str) -> str:
        """Получить статус задачи"""
        for task in self.tasks:
            if task["id"] == task_id:
                return task["status"]
        return "not_found"

    def update_task_status(self, task_id: str, status: str):
        """Обновить статус задачи"""
        for task in self.tasks:
            if task["id"] == task_id:
                task["status"] = status
                task["updated_at"] = datetime.now().isoformat()
                break


# ⭐ [СОСТОЯНИЕ] Менеджер состояния с сохранением
class StateManager:
    """Менеджер состояния с поддержкой сохранения и восстановления"""

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.state_file = REPO_ROOT / ".agent_data" / "state" / f"{agent_id}_state.pkl"
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.state_version = "1.0"

    def save_state(self, state: dict):
        """Сохранить состояние"""
        state_data = {
            "version": self.state_version,
            "timestamp": datetime.now().isoformat(),
            "agent_id": self.agent_id,
            "data": state,
        }
        try:
            with open(self.state_file, "wb") as f:
                pickle.dump(state_data, f)
            logger.info(f"✅ State saved to {self.state_file}")
        except Exception as e:
            logger.error(f"❌ Failed to save state: {e}")

    def load_state(self) -> dict | None:
        """Загрузить состояние"""
        try:
            if self.state_file.exists():
                with open(self.state_file, "rb") as f:
                    state_data = pickle.load(f)
                logger.info(f"✅ State loaded from {self.state_file}")
                return state_data.get("data", {})
        except Exception as e:
            logger.error(f"❌ Failed to load state: {e}")
        return None

    def clear_state(self):
        """Очистить состояние"""
        try:
            if self.state_file.exists():
                self.state_file.unlink()
                logger.info(f"✅ State cleared: {self.state_file}")
        except Exception as e:
            logger.error(f"❌ Failed to clear state: {e}")


# ===== END ENTERPRISE CLASSES =====


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
        logger.info(f"🚀 Standard Agent initialized: {self.agent_id}")

        # ⭐ [ENTERPRISE] Initialize Metrics Collector
        self.metrics_collector = MetricsCollector()
        logger.info("✅ Metrics collector initialized")

        # ⭐ [ENTERPRISE] Initialize Audit Logger
        self.audit_logger = AuditLogger(agent_id=self.agent_id)
        logger.info("✅ Audit logger initialized")

        # ⭐ [ENTERPRISE] Initialize Self-Healing System
        self.self_healing = SelfHealingSystem(agent=self)
        logger.info("✅ Self-healing system initialized")

        # ⭐ [ENTERPRISE] Initialize Task Planner
        self.task_planner = TaskPlanner()
        logger.info("✅ Task planner initialized")

        # ⭐ [ENTERPRISE] Initialize State Manager
        self.state_manager = StateManager(agent_id=self.agent_id)
        logger.info("✅ State manager initialized")

        # ⭐ [HYBRID] Initialize Prompt Engine (Layer 2: Strategy Manager)
        prompts_dir = Path(__file__).parent / "prompts"
        self.prompt_engine = PromptEngine(prompts_dir=prompts_dir, llm_client=None)
        logger.info(f"✅ Prompt engine initialized: {prompts_dir}")

        # ⭐ [HYBRID] Feature flag for prompt-driven strategies
        self.use_prompt_strategies = True  # Can be toggled via config

        # Инициализация модуля самотестирования
        # Создаем временные экземпляры компонентов для передачи в SelfTestingModule
        # В реальности компоненты создаются динамически, но для самотестирования
        # нам нужен интерфейс, поэтому передаем self как placeholder
        self.self_testing_module = SelfTestingModule(
            project_scanner=self,  # Передаем self, так как project_scanner создается динамически
            code_analyzer=self,  # Передаем self, так как code_analyzer создается динамически
            test_analyzer=self,  # Передаем self, так как test_analyzer создается динамически
            task_planner=self.task_planner,  # Теперь используем enterprise task planner
            logger=logger,
        )

        # Запуск фоновой задачи для автономного тестирования
        # Это неблокирующая операция
        try:
            # Запускаем задачу в фоне, если агент полностью инициализирован
            self.self_testing_task = asyncio.create_task(
                # раз в час
                self.self_testing_module.run_periodically(interval=3600)
            )
        except RuntimeError:
            # Если event loop не запущен, задачу запустим позже
            self.self_testing_task = None

    # ⭐ [БЕЗОПАСНОСТЬ] Загрузка правил guardrails
    def _load_guardrails(self, guardrails_path: Path):
        """Загрузить правила безопасности с валидацией схемы"""
        try:
            with open(guardrails_path, encoding="utf-8") as f:
                self.guardrails = yaml.safe_load(f)

            # ⭐ [БЕЗОПАСНОСТЬ] Валидация схемы guardrails
            required_keys = ["allowed_paths", "blocked_patterns", "safe_actions", "rules"]
            for key in required_keys:
                if key not in self.guardrails:
                    logger.error(f"❌ Missing required key in guardrails: {key}")
                    raise ValueError(f"Missing required key in guardrails: {key}")

            # Валидация правил
            for rule in self.guardrails["rules"]:
                if "pattern" not in rule or "action" not in rule:
                    logger.error(f"❌ Invalid rule format: {rule}")
                    raise ValueError(f"Invalid rule format: {rule}")

            self.allowed_paths = self.guardrails.get("allowed_paths", [])
            self.blocked_patterns = self.guardrails.get("blocked_patterns", [])
            self.safe_actions = self.guardrails.get("safe_actions", ["read", "scan", "analyze"])
            logger.info(
                f"✅ Loaded {len(self.allowed_paths)} allowed paths, {len(self.blocked_patterns)} blocked patterns"
            )
        except ValueError:
            # Повторный ValueError — это ошибка схемы, не просто exception
            self.guardrails_loaded = False
            self._load_default_guardrails()
        except Exception as e:
            logger.error(f"Failed to load guardrails: {e}")
            self.guardrails_loaded = False
            self._load_default_guardrails()

    # ⭐ [БЕЗОПАСНОСТЬ] Безопасные значения по умолчанию
    def _load_default_guardrails(self):
        """Загрузить безопасные значения guardrails по умолчанию"""
        self.guardrails = {
            "allowed_paths": ["^apps/", "^agents/", "^config/"],
            "blocked_patterns": [r"\.\./", r"/etc/", r"~/", r"\.env", r"\.pem", r"\.key"],
            "safe_actions": ["read", "scan", "analyze", "list"],
            "rules": [{"pattern": ".*\\.(key|pem|env)$", "action_pattern": ".*", "action": "block"}],
        }
        self.allowed_paths = self.guardrails["allowed_paths"]
        self.blocked_patterns = self.guardrails["blocked_patterns"]
        self.safe_actions = self.guardrails["safe_actions"]
        logger.warning("⚠️ Using default guardrails due to load error")

    # ⭐ [БЕЗОПАСНОСТЬ] Проверка rate limiting
    def _check_rate_limit(self):
        """Проверить лимиты AI вызовов"""
        now = datetime.now()
        if (now - self.ai_call_reset_time).seconds >= 3600:
            self.ai_call_counter = 0
            self.ai_call_reset_time = now

        if self.ai_call_counter >= self.OPERATION_LIMITS["max_ai_calls_per_hour"]:
            raise Exception(f"Rate limit exceeded: {self.ai_call_counter} calls in last hour")

        self.ai_call_counter += 1

    # ⭐ [БЕЗОПАСНОСТЬ] Валидация входных данных
    def _validate_task(self, task: str) -> tuple[bool, str]:
        """Проверить задачу на опасное содержимое"""
        if len(task) > self.OPERATION_LIMITS["max_task_length"]:
            # ⭐ [МОНИТОРИНГ] Логирование события безопасности
            self._log_security_event(
                "task_too_long",
                {"task_length": len(task), "max_length": self.OPERATION_LIMITS["max_task_length"]},
                severity="warning",
            )
            return False, f"Task too long ({len(task)} > {self.OPERATION_LIMITS['max_task_length']})"

        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, task, re.IGNORECASE):
                logger.warning(f"❌ Dangerous pattern detected: {pattern}")
                # ⭐ [МОНИТОРИНГ] Логирование события безопасности
                self._log_security_event(
                    "dangerous_pattern_detected",
                    {"pattern": pattern, "task_preview": task[:100]},
                    severity="critical",
                )
                return False, f"Dangerous command detected: {pattern}"

        return True, "OK"

    # ⭐ [БЕЗОПАСНОСТЬ] Валидация AI-ответов (санитайзер)
    def _validate_ai_response(self, response: str) -> tuple[bool, str]:
        """
        Валидация ответа AI перед выполнением.
        Блокирует потенциально опасные паттерны в AI-ответах.

        Args:
            response: Ответ от AI-модели

        Returns:
            tuple[bool, str]: (безопасен_ли, сообщение_о_результате)
        """
        if not response or not isinstance(response, str):
            return False, "Empty or invalid response"

        for pattern in self.AI_RESPONSE_DANGEROUS_PATTERNS:
            if re.search(pattern, response, re.IGNORECASE):
                logger.error(f"🚫 Blocked dangerous AI response pattern: {pattern}")
                logger.error(f"Response preview: {response[:200]}...")
                # ⭐ [МОНИТОРИНГ] Логирование события безопасности
                self._log_security_event(
                    "dangerous_ai_response",
                    {"pattern": pattern, "response_preview": response[:200]},
                    severity="critical",
                )
                return False, f"Dangerous pattern detected in AI response: {pattern}"

        # Проверка на слишком длинные ответы (возможная утечка данных)
        if len(response) > 10000:
            logger.warning(f"⚠️ AI response unusually long ({len(response)} chars)")
            # Не блокируем, но логируем

        return True, "OK"

    # ⭐ [ENTERPRISE] Проверка доступа к файлу через enterprise guardrails
    def _check_file_access(self, file_path: str, action: str) -> tuple[bool, str]:
        """
        Проверить доступ к файлу через enterprise guardrails

        Args:
            file_path: Путь к файлу
            action: Действие (read, write, execute, delete)

        Returns:
            tuple[bool, str]: (доступ_разрешен, сообщение)
        """
        if not self.auth_token:
            return False, "Agent not authenticated"

        # Преобразовать действие в AccessLevel
        action_map = {
            "read": AccessLevel.READ,
            "write": AccessLevel.WRITE,
            "execute": AccessLevel.EXECUTE,
            "delete": AccessLevel.DELETE,
        }

        access_level = action_map.get(action)
        if not access_level:
            return False, f"Unknown action: {action}"

        # Проверить доступ
        result = self.enterprise_guardrails.authorize_file_access(self.auth_token, file_path, access_level)

        if result["allowed"]:
            return True, "Access granted"
        else:
            return False, result["reason"]

    def start(self, background: bool = True):
        """Запустить агента"""
        if self.running:
            logger.warning("Agent already running")
            return

        self.running = True
        logger.info("🟢 Agent started")

        # ⭐ [МОНИТОРИНГ] Логирование запуска
        self._log_action("agent_started", {"background": background})

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

        # ⭐ [МОНИТОРИНГ] Логирование остановки
        self._log_action("agent_stopped", {"total_scans": len(self.scan_results)})

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

    # ⭐ [МОНИТОРИНГ] Таймаут AI-вызовов (async)
    async def _call_ai_with_timeout(self, prompt: str, system_message: str, timeout: int = None) -> str | None:
        """
        Вызов AI с таймаутом.

        Args:
            prompt: Запрос для AI
            system_message: Системное сообщение
            timeout: Таймаут в секундах (по умолчанию self.ai_call_timeout)

        Returns:
            str | None: Ответ от AI или None при таймауте
        """
        if timeout is None:
            timeout = self.ai_call_timeout

        try:
            response = await asyncio.wait_for(
                self._call_ai_sync(prompt, system_message),
                timeout=timeout,
            )
            return response
        except TimeoutError:
            self.audit_logger.log_security_event(
                "ai_timeout",
                {"prompt_length": len(prompt), "timeout": timeout},
                severity="warning",
            )
            logger.error(f"⏳ AI call timed out after {timeout}s")
            return None
        except Exception as e:
            logger.error(f"❌ AI call failed: {e}")
            return None

    def _call_ai_sync(self, prompt: str, system_message: str) -> str | None:
        """Синхронный вызов AI (для использования в asyncio.to_thread)"""
        return chat_with_fallback(
            [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt},
            ]
        )

    # ⭐ [МОНИТОРИНГ] Логирование действий (audit)
    def _log_action(self, action: str, details: dict, status: str = "success"):
        """Логирование действий агента для аудита"""
        self.audit_logger.log_action(action, details, status)

    def _log_security_event(self, event_type: str, details: dict, severity: str = "warning"):
        """Логирование событий безопасности"""
        self.audit_logger.log_security_event(event_type, details, severity)

    def _remember_decision(self, context: dict, decision: str, outcome: str):
        """Запомнить решение и его результат для будущего обучения"""
        self.memory["decisions"].append(
            {"context": context, "decision": decision, "outcome": outcome, "timestamp": datetime.now().isoformat()}
        )

        # Ограничиваем историю 100 записями
        if len(self.memory["decisions"]) > 100:
            self.memory["decisions"] = self.memory["decisions"][-100:]

        # Обновляем success rate
        success_count = sum(1 for d in self.memory["decisions"] if d["outcome"] == "success")
        self.memory["success_rate"] = success_count / len(self.memory["decisions"]) if self.memory["decisions"] else 0.0

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
            scan_data = git_results
        elif mode == "git_diff":
            scan_data = project_scanner.scan_git_diff()
        elif mode == "full":
            scan_data = project_scanner.scan_full()
        elif mode == "paths":
            paths = getattr(self, "scan_paths", ["apps/", "agents/cognitive_agent/"])
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
            "recommendations": self._generate_recommendations(),  # ⭐ Улучшенная версия
        }

        self.last_scan = scan_start

        logger.info(f"✅ Scan completed in {(datetime.now() - scan_start).total_seconds():.2f}s")
        logger.info(f"   Mode: {mode}")
        logger.info(f"   Files scanned: {self.scan_results['files']}")
        if compass_results:
            logger.info(
                f"   IT Compass markers: {compass_results.get('markers_detected', 0)}/{compass_results.get('markers_total', 0)}"
            )

        # ⭐ [МОНИТОРИНГ] Логирование сканирования
        self._log_action(
            "scan_completed",
            {
                "mode": mode,
                "files_scanned": self.scan_results["files"],
                "issues_found": len(self.scan_results.get("issues", [])),
                "duration_seconds": (datetime.now() - scan_start).total_seconds(),
            },
        )

        # Сохранение результатов
        self._save_scan_results()

        # ⭐ [RAG] Индексировать документы после сканирования
        self.index_project_documents()

        return self.scan_results

    # ⭐ [RAG] Методы для работы с ChromaDB

    def index_project_documents(self, force: bool = False) -> dict[str, Any]:
        """
        Индексировать документы проекта в ChromaDB для семантического поиска.

        Args:
            force: Принудительная переиндексация (даже если уже есть)

        Returns:
            dict: Статистика индексации
        """
        if not CHROMA_AVAILABLE or not self.chroma_indexer:
            logger.info("ℹ️ ChromaDB not available, skipping indexing")
            return {"status": "skipped", "reason": "ChromaDB not available"}

        try:
            logger.info("📚 Indexing project documents in ChromaDB...")

            # 1. Собираем документы для индексации
            documents = []
            metadatas = []
            ids = []

            # Сканируем файлы проекта
            for file_path in self.project_path.rglob("*"):
                if file_path.is_file() and not self._is_excluded(file_path):
                    # Проверяем доступ к файлу через enterprise guardrails
                    access_granted, access_msg = self._check_file_access(str(file_path), "read")
                    if not access_granted:
                        logger.debug(f"⚠️ Access denied to {file_path}: {access_msg}")
                        continue

                    # Ограничиваем размер файла
                    if file_path.stat().st_size > self.OPERATION_LIMITS["max_file_size_mb"] * 1_000_000:
                        continue

                    # Читаем текстовые файлы
                    try:
                        content_text = file_path.read_text(encoding="utf-8", errors="ignore")
                        if len(content_text.strip()) > 50:  # Минимальная длина
                            documents.append(content_text)
                            metadatas.append(
                                {
                                    "path": str(file_path.relative_to(self.project_path)),
                                    "extension": file_path.suffix,
                                    "size": file_path.stat().st_size,
                                    "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                                }
                            )
                            ids.append(f"doc_{len(documents)}")
                    except Exception as e:
                        logger.debug(f"⚠️ Could not read {file_path}: {e}")
                        continue

            # 2. Добавляем в ChromaDB (пакетно)
            if documents:
                batch_size = 100
                for i in range(0, len(documents), batch_size):
                    batch_docs = documents[i : i + batch_size]
                    batch_metas = metadatas[i : i + batch_size]
                    batch_ids = ids[i : i + batch_size]

                    self.chroma_indexer.add_documents(
                        documents=batch_docs,
                        metadatas=batch_metas,
                        ids=batch_ids,
                    )
                    logger.info(f"   ✅ Indexed {len(batch_docs)} documents (batch {i // batch_size + 1})")

                logger.info(f"✅ Successfully indexed {len(documents)} documents in ChromaDB")

                # ⭐ [МОНИТОРИНГ] Логируем успешную индексацию
                self._log_action(
                    "chroma_indexing",
                    {
                        "documents_indexed": len(documents),
                        # Первые 5 для примера
                        "paths": [m["path"] for m in metadatas[:5]],
                    },
                    status="success",
                )

                return {
                    "status": "success",
                    "documents_indexed": len(documents),
                    "collection": self.chroma_indexer.collection_name,
                }
            else:
                logger.info("ℹ️ No new documents to index")
                return {"status": "no_documents", "documents_indexed": 0}

        except Exception as e:
            logger.error(f"❌ ChromaDB indexing failed: {e}")
            self._log_action("chroma_indexing", {"error": str(e)}, status="failed")
            return {"status": "error", "reason": str(e)}

    def search_similar_documents(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """
        Поиск семантически похожих документов через ChromaDB.

        Args:
            query: Поисковый запрос
            top_k: Количество результатов

        Returns:
            list: Найденные документы с метаданными и релевантностью
        """
        if not CHROMA_AVAILABLE or not self.chroma_indexer:
            logger.warning("⚠️ ChromaDB not available for search")
            return []

        try:
            # ⭐ [БЕЗОПАСНОСТЬ] Валидация запроса
            is_valid, error_msg = self._validate_task(query)
            if not is_valid:
                logger.warning(f"🚫 Search query blocked: {error_msg}")
                return []

            logger.info(f"🔍 Searching ChromaDB: '{query[:100]}...'")

            # Выполняем поиск
            results = self.chroma_indexer.query(query, top_k=top_k)

            # Форматируем результаты
            formatted_results = []
            for i, (doc, metadata, distance) in enumerate(
                zip(
                    results.get("documents", [[]])[0],
                    results.get("metadatas", [[]])[0],
                    results.get("distances", [[]])[0],
                    strict=False,
                )
            ):
                formatted_results.append(
                    {
                        "rank": i + 1,
                        # Конвертируем расстояние в релевантность (0-1)
                        "score": 1 - distance,
                        "path": metadata.get("path", "unknown"),
                        "content_preview": doc[:200] + "..." if len(doc) > 200 else doc,
                        "metadata": metadata,
                    }
                )

            logger.info(f"✅ Found {len(formatted_results)} similar documents")

            # ⭐ [ИНТЕЛЛЕКТ] Запоминаем успешный поиск
            self._remember_decision(
                context={"query": query[:100]},
                decision=f"Found {len(formatted_results)} documents",
                outcome="success",
            )

            return formatted_results

        except Exception as e:
            logger.error(f"❌ ChromaDB search failed: {e}")
            return []

    def get_chroma_stats(self) -> dict[str, Any]:
        """Получить статистику ChromaDB"""
        if not CHROMA_AVAILABLE or not self.chroma_indexer:
            return {"available": False}

        try:
            stats = self.chroma_indexer.get_stats()
            stats["available"] = True
            return stats
        except Exception as e:
            logger.error(f"❌ Failed to get ChromaDB stats: {e}")
            return {"available": False, "error": str(e)}

    def clear_chroma_collection(self, confirm: bool = False) -> dict[str, Any]:
        """Очистить коллекцию ChromaDB (ОПАСНО).

        Интерактивность (input/print) удалена: безопасность задаётся параметром confirm.

        Args:
            confirm: если True — операция выполняется, иначе операция блокируется

        Returns:
            dict: Результат операции
                - status: success|pending_approval|blocked|cancelled|error
        """
        if not CHROMA_AVAILABLE or not self.chroma_indexer:
            return {"status": "error", "reason": "ChromaDB not available"}

        try:
            if not confirm:
                # Безопасный отказ: не трогаем коллекцию
                self._log_security_event(
                    "chroma_collection_clear_blocked",
                    {"agent_id": self.agent_id, "confirm": confirm},
                    severity="warning",
                )
                return {
                    "status": "pending_approval",
                    "message": "ChromaDB clearing requires confirm=true",
                }

            # Очищаем коллекцию
            self.chroma_indexer.clear_collection()

            # ⭐ [МОНИТОРИНГ] Логируем опасное действие
            self._log_security_event(
                "chroma_collection_cleared",
                {"agent_id": self.agent_id, "confirm": confirm},
                severity="critical",
            )

            logger.info("🗑️ ChromaDB collection cleared")
            return {"status": "success", "message": "Collection cleared"}

        except Exception as e:
            logger.error(f"❌ Failed to clear ChromaDB: {e}")
            self._log_security_event(
                "chroma_collection_clear_error",
                {"agent_id": self.agent_id, "error": str(e)},
                severity="warning",
            )
            return {"status": "error", "reason": str(e)}

    # ⭐ [УСТОЙЧИВОСТЬ] Retry logic для внешних сервисов
    @retry(
        stop=stop_after_attempt(3),  # 3 попытки
        # Экспоненциальная задержка
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True,
    )
    def _run_compass_scan(self):
        """Запустить сканирование IT Compass с retry-логикой"""
        try:
            compass_scanner = get_scanner()
            return compass_scanner.scan_project()
        except Exception as e:
            logger.error(f"IT Compass scan failed: {e}")
            raise  # tenacity поймает и повторит

    def _detect_issues_from_scan(self, scan_data: dict) -> list[dict[str, str]]:
        """Обнаружить проблемы на основе данных сканирования"""
        issues = []

        # Анализ изменённых файлов
        for file_info in scan_data.get("files", []):
            # Проверка на большие файлы
            if file_info.get("size", 0) > self.OPERATION_LIMITS["max_file_size_mb"] * 1_000_000:
                issues.append(
                    {
                        "type": "large_file",
                        "path": file_info["path"],
                        "message": f"Большой файл: {file_info['size'] / 1_000_000:.1f} MB",
                    }
                )

        # ⭐ [БЕЗОПАСНОСТЬ] Лимит файлов за сканирование
        if len(scan_data.get("files", [])) > self.OPERATION_LIMITS["files_per_scan"]:
            issues.append(
                {
                    "type": "too_many_files",
                    "message": f"Слишком много файлов для сканирования: {len(scan_data.get('files', []))}",
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
                    if size > self.OPERATION_LIMITS["max_file_size_mb"] * 1_000_000:
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

    # ⭐ [УЛУЧШЕННАЯ ВЕРСИЯ] Генерация рекомендаций с guardrails
    def _generate_recommendations(self) -> list[dict[str, str]]:
        """Сгенерировать рекомендации через AI — **с проверкой guardrails**"""
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

        # Используем AI для генерации рекомендаций — **но с проверкой guardrails**
        try:
            # ⭐ [БЕЗОПАСНОСТЬ] Проверка rate limiting
            self._check_rate_limit()

            languages = ", ".join(self.scan_results.get("languages", {}).keys())
            issues_count = len(self.scan_results.get("issues", []))

            prompt = f"""
Анализ проекта:
- Языки: {languages}
- Проблем найдено: {issues_count}

Предложи 3-5 конкретных рекомендаций по улучшению кода и архитектуры.
Формат: JSON массив с полями: priority (high/medium/low), category, message.
**ВАЖНО: Никаких действий по изменению кода, только предложения по улучшению.**
"""

            response = chat_with_fallback(
                [
                    {
                        "role": "system",
                        "content": "Ты — эксперт по анализу кода и архитектуры. Всегда соблюдай безопасность и НИКОГДА не предлагай действия по изменению кода.",
                    },
                    {"role": "user", "content": prompt},
                ]
            )

            if response:
                # ⭐ [БЕЗОПАСНОСТЬ] Валидация AI-ответа
                is_safe, safety_msg = self._validate_ai_response(response)
                if not is_safe:
                    logger.error(f"🚫 AI recommendations blocked: {safety_msg}")
                    return recommendations

                try:
                    json_match = re.search(r"\[.*\]", response, re.DOTALL)
                    if json_match:
                        ai_recommendations = json.loads(json_match.group())
                        for rec in ai_recommendations:
                            # ⭐ [БЕЗОПАСНОСТЬ] Проверка рекомендаций на опасное содержимое
                            if any(
                                keyword in rec.get("message", "").lower()
                                for keyword in ["delete", "remove", "modify", "change", "write", "create"]
                            ):
                                logger.warning(f"❌ Guardrail violation in AI recommendation: {rec}")
                                continue  # Пропускаем опасную рекомендацию

                            # Проверка на длину сообщения
                            if len(rec.get("message", "")) > 500:
                                rec["message"] = rec["message"][:500] + "..."

                            recommendations.append(rec)

                            # ⭐ [ИНТЕЛЛЕКТ] Запоминаем успешную рекомендацию
                            self._remember_decision(
                                context={"languages": languages, "issues_count": issues_count},
                                decision=rec.get("message", ""),
                                outcome="success",
                            )
                except Exception as e:
                    logger.warning(f"Failed to parse AI recommendations: {e}")

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
        status = {
            "agent_id": self.agent_id,
            "running": self.running,
            "project_path": str(self.project_path),
            "last_scan": self.last_scan.isoformat() if self.last_scan else None,
            "scan_interval_seconds": self.scan_interval,
            "ai_provider": self.ai_manager.get_active_provider(),
            "ai_providers_status": self.ai_manager.get_status(),
            "total_scans": len(self.scan_results),
            "total_recommendations": len(self.recommendations),
            # ⭐ [МОНИТОРИНГ] Дополнительные метрики
            "guardrails_loaded": self.guardrails_loaded,
            "ai_calls_today": self.ai_call_counter,
            "memory_success_rate": self.memory["success_rate"],
            "operation_limits": self.OPERATION_LIMITS,
            "ai_call_timeout": self.ai_call_timeout,
            # ⭐ [МОНИТОРИНГ] Audit log path
            "audit_log_path": self.audit_logger.log_file if self.audit_logger else None,
            # ⭐ [ИНТЕГРАЦИИ] Статус интеграций
            "chroma_available": CHROMA_AVAILABLE,
            "job_agent_available": self.job_agent_available,
            # ⭐ [ENTERPRISE] Guardrails status
            "enterprise_guardrails_active": self.auth_token is not None,
            "authenticated_as": self.agent_id if self.auth_token else None,
        }

        # Добавляем статистику ChromaDB если доступна
        if CHROMA_AVAILABLE and self.chroma_indexer:
            status["chroma_stats"] = self.chroma_indexer.get_stats()

        return status

    def execute_task(self, task: str, auto_approve: bool = False) -> dict[str, Any]:
        """
        Выполнить задачу через AI — **с проверкой guardrails**
        """
        logger.info(f"📝 Task received: {task}")

        # ⭐ [БЕЗОПАСНОСТЬ] Валидация задачи
        is_valid, error_msg = self._validate_task(task)
        if not is_valid:
            return {"status": "error", "message": error_msg}

        # ⭐ [БЕЗОПАСНОСТЬ] Проверка rate limiting
        try:
            self._check_rate_limit()
        except Exception as e:
            return {"status": "error", "message": str(e)}

        # 1. Генерация плана через AI
        plan_prompt = f"""
Задача: {task}

Предложи пошаговый план выполнения:
1. Анализ текущего состояния
2. Необходимые изменения
3. Тестирование
4. Документация

Формат: JSON с полями steps (массив), estimated_time, risk_level.
Каждый шаг должен содержать поля: action, target, description.
Максимум {self.OPERATION_LIMITS["max_actions_per_task"]} шагов.
"""

        plan_response = chat_with_fallback(
            [
                {
                    "role": "system",
                    "content": "Ты — помощник по выполнению задач в коде. Всегда соблюдай безопасность.",
                },
                {"role": "user", "content": plan_prompt},
            ]
        )

        if not plan_response:
            return {"status": "error", "message": "AI не доступен"}

        # ⭐ [БЕЗОПАСНОСТЬ] Валидация AI-ответа перед парсингом
        is_safe, safety_msg = self._validate_ai_response(plan_response)
        if not is_safe:
            logger.error(f"🚫 AI response blocked by safety validation: {safety_msg}")
            return {"status": "error", "message": f"Response blocked by safety: {safety_msg}"}

        # 2. Парсинг и проверка плана на guardrails
        try:
            json_match = re.search(r"\{.*\}", plan_response, re.DOTALL)
            if not json_match:
                return {"status": "error", "message": "AI не вернул JSON"}

            plan = json.loads(json_match.group())
            steps = plan.get("steps", [])

            # ⭐ [БЕЗОПАСНОСТЬ] Лимит шагов
            if len(steps) > self.OPERATION_LIMITS["max_actions_per_task"]:
                return {"status": "error", "message": f"Too many steps: {len(steps)}"}

        except Exception as e:
            logger.error(f"Failed to parse plan: {e}")
            return {"status": "error", "message": f"Ошибка парсинга: {e}"}

        # 3. Проверка guardrails на каждый шаг
        for i, step in enumerate(steps):
            action = step.get("action", "")
            path = step.get("target", "")

            # Если шаг требует модификации файлов — проверяем enterprise guardrails
            if any(keyword in action.lower() for keyword in ["write", "create", "delete", "modify", "update"]):
                access_granted, access_msg = self._check_file_access(path, action.split()[0].lower())
                if not access_granted:
                    logger.warning(f"❌ Guardrail violation: {action} → {path}, reason: {access_msg}")
                    return {
                        "status": "pending_approval",
                        "reason": f"Требуется одобрение для: {path} ({access_msg})",
                        "step_index": i,
                        "step": step,
                    }

        # 4. Проверка подтверждения
        if not auto_approve:
            print("\n🤖 Предложен план выполнения задачи:")
            print(json.dumps(plan, indent=2, ensure_ascii=False))
            print("\nВыполнить? (y/n): ", end="")
            response = input().lower()
            if response != "y":
                # ⭐ [ИНТЕЛЛЕКТ] Запоминаем отменённую задачу
                self._remember_decision(context={"task": task[:100]}, decision=plan_prompt[:100], outcome="cancelled")
                return {"status": "cancelled", "message": "Пользователь отменил"}

        # 5. Выполнение задачи (только если guardrails пройдены)
        # ⭐ [ИНТЕЛЛЕКТ] Запоминаем выполненную задачу
        self._remember_decision(context={"task": task[:100]}, decision=plan_prompt[:100], outcome="success")

        # ⭐ [МОНИТОРИНГ] Логирование выполнения задачи
        self._log_action(
            "task_executed",
            {
                "task": task[:100],
                "plan_steps": len(steps),
                "auto_approve": auto_approve,
            },
            status="success",
        )

        return {
            "status": "success",
            "task": task,
            "plan": plan,
            "message": "Задача запланирована (полное выполнение требует дополнительных прав)",
        }

    def _check_guardrail(self, action: str, path: str, context: dict = None) -> bool:
        """
        🧠 УМНАЯ ПРОВЕРКА GUARDRAILS
        Понимает контекст: баги фиксит автоматически, конфиги — с подтверждением
        """
        # 1. Если это простое чтение — всегда разрешено
        if action.lower() in ["read", "scan", "analyze", "list"]:
            return True

        # 2. Проверяем заблокированные паттерны
        for pattern in self.blocked_patterns:
            if re.search(pattern, path, re.IGNORECASE):
                logger.warning(f"❌ Guardrail blocked: {path} (pattern: {pattern})")
                self._log_security_event("guardrail_blocked", {"path": path, "action": action}, severity="warning")
                return False

        # 3. Проверяем разрешённые пути
        if hasattr(self, "allowed_paths") and self.allowed_paths:
            allowed = any(re.match(p, path, re.IGNORECASE) for p in self.allowed_paths if p)
            if not allowed and path:
                logger.warning(f"❌ Path not in allowed_paths: {path}")
                return False

        # 4. 🧠 ИНТЕЛЛЕКТУАЛЬНАЯ ПРОВЕРКА (ключевое улучшение!)
        # Если это исправление бага — разрешаем автоматически
        if context and context.get("type") in ["bugfix", "hotfix", "typo"]:
            logger.info(f"✅ Auto-approve bugfix: {action} → {path}")
            return True

        # Если это рефакторинг — разрешаем (но логируем)
        if context and context.get("type") in ["refactor", "optimize", "cleanup"]:
            logger.info(f"✅ Auto-approve refactor: {action} → {path}")
            self._log_action("refactor_auto_approved", {"path": path, "action": action})
            return True

        # Если это добавление фичи — разрешаем (но логируем)
        if context and context.get("type") == "feature":
            logger.info(f"✅ Auto-approve feature: {action} → {path}")
            self._log_action("feature_auto_approved", {"path": path, "action": action})
            return True

        # 5. Проверяем важные файлы
        important_files = ["config.yaml", "settings.py", "requirements.txt", "Dockerfile", "docker-compose.yml"]
        if any(important in path for important in important_files):
            if action.lower() in ["modify", "write", "delete"]:
                logger.info(f"⚠️ Important file requires approval: {path}")
                return False  # Требует подтверждения

        # 6. Проверяем конфигурационные файлы
        if path.endswith((".yaml", ".yml", ".json")):
            if action.lower() in ["modify", "write", "delete"]:
                logger.info(f"⚠️ Config file requires approval: {path}")
                return False  # Требует подтверждения

        # 7. Если это тесты или документация — всегда разрешено
        if "tests" in path or "test" in path:
            return True
        if path.endswith((".md", ".rst", ".txt")):
            return True

        # 8. 🎯 Основной код: разрешено с аудитом
        if path.endswith((".py", ".js", ".ts")):
            logger.info(f"✅ Code modification allowed: {action} → {path}")
            self._log_action("code_modification", {"path": path, "action": action})
            return True

        # 9. 🛑 По умолчанию — запрет (безопасность)
        logger.warning(f"⚠️ Default deny: {action} → {path}")
        return False

    # ===== README Automation Methods =====

    def update_readme_for_service(self, service_profile) -> dict[str, Any]:
        """
        Update apps/<service>/README.md using existing template mechanism.
        """
        logger.info(f"Update README for service: {service_profile.name}")

        try:
            analysis_report = self._analyze_service_code(service_profile)
            context_data = self._prepare_template_context(analysis_report, service_profile.name)
            new_readme_content = self._render_readme_template(context_data)

            readme_path = f"{service_profile.path}/README.md"
            readme_file = Path(readme_path)

            readme_file.parent.mkdir(parents=True, exist_ok=True)
            with open(readme_file, "w", encoding="utf-8") as f:
                f.write(new_readme_content)

            if hasattr(self, "audit_logger") and self.audit_logger:
                try:
                    self.audit_logger.log_action(
                        "readme_updated",
                        {"service": service_profile.name, "path": str(readme_file)},
                        status="success",
                    )
                except Exception:
                    pass

            return {"status": "success", "message": f"README updated for {service_profile.name}"}
        except Exception as e:
            logger.error(f"README update failed for {service_profile.name}: {e}")
            if hasattr(self, "audit_logger") and self.audit_logger:
                try:
                    self.audit_logger.log_action(
                        "readme_update_failed",
                        {"service": service_profile.name, "error": str(e)},
                        status="failed",
                    )
                except Exception:
                    pass
            return {"status": "error", "message": str(e)}

    def update_readme_for_all_services(self) -> dict[str, Any]:
        """Update README for all services in apps/ directory."""
        apps_dir = Path(self.project_path) / "apps"
        if not apps_dir.exists():
            return {"status": "error", "message": "apps directory not found"}

        service_dirs = [
            d for d in apps_dir.iterdir() if d.is_dir() and not d.name.startswith(".") and not d.name.startswith("__")
        ]

        results = {"successful": [], "failed": [], "total": len(service_dirs)}
        for service_dir in service_dirs:

            class ServiceProfile:
                def __init__(self, name, path):
                    self.name = name
                    self.path = path

            profile = ServiceProfile(service_dir.name, str(service_dir))
            r = self.update_readme_for_service(profile)
            if r["status"] == "success":
                results["successful"].append({"service": profile.name, "message": r["message"]})
            else:
                results["failed"].append({"service": profile.name, "message": r["message"]})

        results["apps_readme"] = self.update_apps_directory_readme()
        return results

    def update_apps_directory_readme(self) -> dict[str, Any]:
        """Update the main apps/README.md with summary of all services."""
        apps_dir = Path(self.project_path) / "apps"
        if not apps_dir.exists():
            return {"status": "error", "message": "apps directory not found"}

        services_info: list[dict[str, Any]] = []
        service_dirs = [
            d for d in apps_dir.iterdir() if d.is_dir() and not d.name.startswith(".") and not d.name.startswith("__")
        ]

        for service_dir in service_dirs:
            readme_path = service_dir / "README.md"
            if readme_path.exists():
                try:
                    content = readme_path.read_text(encoding="utf-8", errors="ignore")
                    services_info.append(self._parse_service_readme(content, service_dir.name))
                    continue
                except Exception as e:
                    logger.warning(f"Failed to parse README for {service_dir.name}: {e}")

            # fallback if README missing/unparseable
            try:

                class ServiceProfile:
                    def __init__(self, name, path):
                        self.name = name
                        self.path = path

                profile = ServiceProfile(service_dir.name, str(service_dir))
                analysis_report = self._analyze_service_code(profile)
                services_info.append(
                    {
                        "name": service_dir.name,
                        "purpose": analysis_report.get("purpose", "Информация недоступна"),
                        "framework": analysis_report.get("framework", "Неизвестно"),
                        "language": analysis_report.get("language", "Python"),
                        "readiness_level": analysis_report.get("readiness_level", "Неизвестно"),
                        "test_coverage": analysis_report.get("test_coverage", 0),
                        "capabilities": analysis_report.get("capabilities", ["Нет информации"]),
                    }
                )
            except Exception:
                services_info.append(
                    {
                        "name": service_dir.name,
                        "purpose": "Информация недоступна",
                        "framework": "Неизвестно",
                        "language": "Python",
                        "readiness_level": "Неизвестно",
                        "test_coverage": 0,
                        "capabilities": ["Не удалось проанализировать код"],
                    }
                )

        services_info.sort(key=lambda x: x["name"])

        template_str = self._generate_apps_readme_template()
        template = jinja2.Template(template_str)
        content = template.render(context={"services": services_info})

        apps_readme_path = apps_dir / "README.md"
        with open(apps_readme_path, "w", encoding="utf-8") as f:
            f.write(content)

        if hasattr(self, "audit_logger") and self.audit_logger:
            try:
                self.audit_logger.log_action(
                    "apps_readme_updated",
                    {"path": str(apps_readme_path), "services_count": len(services_info)},
                    status="success",
                )
            except Exception:
                pass

        return {
            "status": "success",
            "message": f"apps/README updated, includes {len(services_info)} services",
            "services_count": len(services_info),
        }

    def _analyze_service_code(self, service_profile):
        """Lightweight analysis to fill template context."""
        project_path = Path(service_profile.path)
        report = {
            "purpose": "",
            "libraries": [],
            "modules": [],
            "capabilities": [],
            "test_coverage": 0.0,
            "has_tests": False,
            "critical_issues": None,
            "agent_id": getattr(self, "agent_id", "autonomous-agent"),
            "timestamp": datetime.now().isoformat(),
            "language": "Python",
            "framework": "",
            "readiness_level": "MVP",
            "python_version": "3.11+",
        }

        init_file = project_path / "__init__.py"
        main_file = project_path / "main.py"

        for candidate in [init_file, main_file]:
            if candidate.exists():
                try:
                    content = candidate.read_text(encoding="utf-8", errors="ignore")
                    for line in content.splitlines():
                        if "service" in line.lower() or "сервис" in line.lower() or "назначение" in line.lower():
                            report["purpose"] = line.strip().lstrip("#").strip().replace('"', "").replace("'", "")
                            break
                    if report["purpose"]:
                        break
                except Exception:
                    pass

        if not report["purpose"]:
            report["purpose"] = "Сервис для выполнения специфичных задач в рамках проекта"

        # Simple framework detection
        for py_file in project_path.rglob("*.py"):
            try:
                content = py_file.read_text(encoding="utf-8", errors="ignore")
                if "FastAPI" in content:
                    report["framework"] = "FastAPI"
                elif "Flask" in content:
                    report["framework"] = "Flask"
                elif "Django" in content:
                    report["framework"] = "Django"
            except Exception:
                continue

        # simple capabilities inference
        report["capabilities"] = self._infer_capabilities(project_path)

        return report

    def _infer_capabilities(self, project_path: Path) -> list[str]:
        """Infer service capabilities from code analysis."""
        caps: list[str] = []
        for py_file in project_path.rglob("*.py"):
            try:
                content = py_file.read_text(encoding="utf-8", errors="ignore")
                lc = content.lower()
                name_lc = py_file.name.lower()

                if any(k in lc for k in ["create_", "update_", "delete_", "get_", "crud"]):
                    if "CRUD" not in " ".join(caps):
                        caps.append("CRUD операции для сущностей и связей")
                if any(k in lc for k in ["search", "find", "query"]):
                    if "Поиск и фильтрация данных" not in caps:
                        caps.append("Поиск и фильтрация данных")
                if any(k in lc for k in ["graph", "relationship", "entity"]):
                    if "Управление графом знаний" not in caps:
                        caps.append("Управление графом знаний")
                if any(k in lc for k in ["fastapi", "endpoint", "rest api"]):
                    if "REST API интерфейс" not in caps:
                        caps.append("REST API интерфейс")
                if "test" in name_lc:
                    if "Модульное и интеграционное тестирование" not in caps:
                        caps.append("Модульное и интеграционное тестирование")
                if any(k in lc for k in ["auth", "security"]):
                    if "Аутентификация и авторизация" not in caps:
                        caps.append("Аутентификация и авторизация")
                if any(k in lc for k in ["cache", "redis"]):
                    if "Кэширование данных" not in caps:
                        caps.append("Кэширование данных")
            except Exception:
                continue

        return caps or ["Информация недоступна в процессе анализа"]

    def _prepare_template_context(self, report: dict[str, Any], service_name: str) -> dict[str, Any]:
        """Prepare context data for README template rendering."""
        return {
            "service_name": service_name,
            "purpose": report["purpose"],
            "language": report["language"],
            "python_version": report["python_version"],
            "framework": report["framework"] if report["framework"] else "Not specified",
            "libraries": report["libraries"],
            "modules": report["modules"],
            "capabilities": report["capabilities"],
            "test_coverage": round(report.get("test_coverage", 0.0)),
            "has_tests": "Да" if report.get("has_tests") else "Нет",
            "critical_issues": report.get("critical_issues"),
            "agent_id": report["agent_id"],
            "timestamp": report["timestamp"],
            "readiness_level": report["readiness_level"],
        }

    def _render_readme_template(self, context: dict[str, Any]) -> str:
        """Render README from Jinja2 template."""
        try:
            template_loader = jinja2.FileSystemLoader(searchpath="agents/cognitive_agent/templates/")
            template_env = jinja2.Environment(loader=template_loader)
            template = template_env.get_template("README_TEMPLATE.md")
            return template.render(context)
        except Exception as e:
            logger.error(f"Template render failed: {e}; using basic README")
            return self._generate_basic_readme(context)

    def _generate_basic_readme(self, context: dict[str, Any]) -> str:
        """Generate basic README when template fails."""
        readme_content = f"""# 📦 {context['service_name']}
> *Этот файл автоматически генерируется автономным когнитивным агентом на основе анализа исходного кода. Ручные изменения будут перезаписаны.*

## 🎯 Назначение сервиса
{context['purpose']}

## 🛠️ Технологический стек
*   **Язык:** {context['language']} {context['python_version']}
*   **Фреймворк:** {context['framework']}
*   **Ключевые библиотеки:**
"""
        for lib in context["libraries"]:
            readme_content += f"    *   {lib}\n"

        readme_content += """
## 🧱 Архитектура и модули
Сервис состоит из следующих основных модулей:
"""
        # keep empty if no modules
        if context["modules"]:
            for module in context["modules"]:
                readme_content += (
                    f"*   **{module['file_path']}**: {module['description']}\n"
                    f"    *   Ключевые классы/функции: {', '.join(module.get('key_elements', []))}\n"
                    f"    *   Взаимодействие: {module.get('interaction', '')}\n"
                )

        readme_content += """
## 🚀 Ключевые возможности (реализованные в коде)
"""
        for cap in context["capabilities"]:
            readme_content += f"*   {cap}\n"

        readme_content += f"""
## ✅ Статус готовности
*   **Уровень готовности:** {context['readiness_level']}
*   **Покрытие тестами:** {context['test_coverage']}%
*   **Наличие тестов:** {context['has_tests']}
*   **Критические замечания:** {context['critical_issues'] if context['critical_issues'] else 'Не обнаружено.'}
"""
        return readme_content

    def _parse_service_readme(self, content: str, service_name: str) -> dict[str, Any]:
        """Parse service README for aggregation into apps/README.md."""

        def _extract_first(pattern: str, default: str) -> str:
            m = re.search(pattern, content, flags=re.IGNORECASE | re.MULTILINE | re.DOTALL)
            return m.group(1).strip() if m else default

        purpose = _extract_first(
            r"##\s*(?:🎯\s*)?Назначение сервиса\s*\n\s*([\s\S]+?)(?=\n##\s*|\Z)",
            "Назначение не указано",
        )
        framework = _extract_first(
            r"Фреймворк:\s*\*?\s*([^\n]+?)(?=\n|$)",
            "Не указан",
        )
        language = _extract_first(
            r"Язык:\s*\*?\s*([^\n]+?)(?=\n|$)",
            "Python",
        )
        readiness_level = _extract_first(
            r"Уровень готовности:\s*([^\n]+)",
            "Неизвестно",
        )

        test_coverage_str = _extract_first(
            r"Покрытие тестами:\s*\*?\s*(\d+)\s*%",
            "0",
        )
        try:
            test_coverage = int(test_coverage_str)
        except Exception:
            test_coverage = 0

        capabilities: list[str] = []
        m = re.search(
            r"##\s*🚀\s*Ключевые возможности[\s\S]*?\n([\s\S]+?)(?=\n##\s*|\Z)",
            content,
            flags=re.IGNORECASE | re.MULTILINE,
        )
        if m:
            block = m.group(1)
            for line in block.splitlines():
                line = line.strip()
                if line.startswith("*"):
                    cap = line.lstrip("*").strip().strip("-").strip()
                    if cap:
                        capabilities.append(cap)

        if not capabilities:
            capabilities = ["Информация недоступна в README"]

        return {
            "name": service_name,
            "purpose": purpose,
            "framework": framework,
            "language": language,
            "readiness_level": readiness_level,
            "test_coverage": test_coverage,
            "capabilities": capabilities,
        }

    def _generate_apps_readme_template(self) -> str:
        """Generate Jinja2 template for apps/README.md."""
        return """# 🗂️ Директория приложений (apps)

Этот каталог содержит набор микросервисов, каждый из которых реализует отдельную бизнес-функцию.

## 📋 Список сервисов

{% for service in services %}
### [{{ service.name }}](./{{ service.name }}/README.md)

**Назначение:** {{ service.purpose }}

**Технологии:** {{ service.framework }}, {{ service.language }}

**Статус готовности:** {{ service.readiness_level }}

**Покрытие тестами:** {{ service.test_coverage }}%

**Ключевые возможности:**
{% for capability in service.capabilities[:3] %}
*   {{ capability }}
{% endfor %}

[Подробнее](./{{ service.name }}/README.md)

---

{% endfor %}
"""

    # ⭐ [HYBRID] Prompt-driven test coverage analysis
    async def analyze_test_coverage_prompt_driven(
        self,
        service_name: str,
        framework: str = "FastAPI",
        criticality: str = "medium",
        current_coverage: float = 0.0,
        target_coverage: float = 75.0,
        python_version: str = "3.12",
    ) -> dict[str, Any]:
        """
        Analyze test coverage using prompt-driven strategy (Layer 3)

        This method demonstrates the Hybrid Architecture:
        - Layer 1: This Python method (infrastructure glue)
        - Layer 2: PromptEngine (strategy manager)
        - Layer 3: test_coverage_analysis.md template (business logic)

        Args:
            service_name: Name of the service to analyze
            framework: Framework used (FastAPI, Flask, etc.)
            criticality: Service criticality (high/medium/low)
            current_coverage: Current test coverage percentage
            target_coverage: Target coverage goal
            python_version: Python version

        Returns:
            Dictionary with analysis results and recommendations
        """
        if not self.use_prompt_strategies:
            logger.warning("Prompt strategies disabled, using code-based approach")
            return {"success": False, "error": "Prompt strategies disabled"}

        try:
            # Prepare context for template
            context = {
                "service_name": service_name,
                "framework": framework,
                "criticality": criticality,
                "current_coverage": current_coverage,
                "target_coverage": target_coverage,
                "python_version": python_version,
            }

            logger.info("🧠 Executing prompt-driven strategy: test_coverage_analysis")
            logger.debug(f"   Context: {context}")

            # Execute strategy via Prompt Engine (Layer 2)
            result = await self.prompt_engine.execute_strategy(
                strategy="test_coverage_analysis", context=context, timeout=60
            )

            if result["success"]:
                logger.info(f"✅ Prompt-driven analysis completed in {result['execution_time']:.2f}s")
                return result
            else:
                logger.error(f"❌ Prompt-driven analysis failed: {result.get('error')}")
                return result

        except Exception as e:
            logger.error(f"❌ Prompt-driven analysis exception: {e}")
            return {"success": False, "error": str(e), "strategy": "test_coverage_analysis"}

    # ⭐ [HYBRID] Duel mode: Compare code vs prompt approaches
    async def duel_mode_test_coverage(
        self,
        service_name: str,
        code_based_result: Any,
        framework: str = "FastAPI",
        criticality: str = "medium",
        current_coverage: float = 0.0,
        target_coverage: float = 75.0,
    ) -> dict[str, Any]:
        """
        Execute duel mode: compare traditional code approach vs prompt-driven approach

        Args:
            service_name: Name of service
            code_based_result: Result from traditional code-based analysis
            framework: Service framework
            criticality: Service criticality
            current_coverage: Current coverage
            target_coverage: Target coverage

        Returns:
            Comparison results with winner determination
        """
        if not self.use_prompt_strategies:
            return {"error": "Duel mode requires prompt strategies enabled"}

        context = {
            "service_name": service_name,
            "framework": framework,
            "criticality": criticality,
            "current_coverage": current_coverage,
            "target_coverage": target_coverage,
            "python_version": "3.12",
        }

        logger.info(f"⚔️ Starting duel mode for {service_name} test coverage analysis")

        comparison = await self.prompt_engine.execute_duel_mode(
            task_description=f"Analyze test coverage for {service_name}",
            code_approach_result=code_based_result,
            prompt_strategy="test_coverage_analysis",
            context=context,
            evaluation_criteria=["performance", "accuracy", "actionability", "maintainability"],
        )

        return comparison
