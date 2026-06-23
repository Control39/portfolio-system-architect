#!/usr/bin/env python3
"""
Базовый класс для когнитивного агента

Содержит общую функциональность для стандартной и enterprise-версии
"""

import asyncio
import contextlib
import json
import logging
import re
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any

import structlog
import yaml
from tenacity import retry, stop_after_attempt, wait_exponential

# Импорты общих зависимостей
# Правильные пути для импортов
from agents.cognitive_agent.enterprise_guardrails import AccessLevel, EnterpriseGuardrails, UserRole
from agents.cognitive_agent.src.code_analyzer import CodeAnalyzer  # Новый импорт
from agents.cognitive_agent.src.documentation_analyzer import DocumentationAnalyzer  # Новый импорт
from agents.cognitive_agent.src.test_analyzer import TestAnalyzer  # Новый импорт
from apps.ai_config_manager.src.ai_config_manager.config_manager import ConfigManager
from apps.ai_provider_manager.src.ai_provider_manager import (
    chat_with_fallback,
    get_provider_manager,
)
from apps.it_compass.src.it_compass_scanner import get_scanner

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
    analyze_requirements = None  # type: ignore
    generate_resume = None  # type: ignore
    job_search = None  # type: ignore
    process_request_sync = None  # type: ignore

# ChromaDB (опционально)
try:
    from apps.embedding_agent.chroma_indexer import ChromaDocumentIndexer
    from apps.embedding_agent.embedder import DocumentEmbedder

    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False
    ChromaDocumentIndexer = None  # type: ignore
    DocumentEmbedder = None  # type: ignore

# Добавляем корень проекта в PATH
REPO_ROOT = Path(__file__).parent.parent.parent

# ⭐ [КОНФИГУРАЦИЯ] Базовый путь для runtime данных агента
AGENT_DATA_DIR = Path(__file__).parent.parent / ".agent_data"
AGENT_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Поддиректории для различных типов данных
AGENT_LOGS_DIR = AGENT_DATA_DIR / "logs"
AGENT_REPORTS_DIR = AGENT_DATA_DIR / "reports"
AGENT_SCANS_DIR = AGENT_DATA_DIR / "scans"
AGENT_CONFIG_DIR = AGENT_DATA_DIR / "config"
AGENT_DATA_STORAGE_DIR = AGENT_DATA_DIR / "data"
AGENT_STATUS_DIR = AGENT_DATA_DIR / "status"
AGENT_PLANS_DIR = AGENT_DATA_DIR / "plans"
AGENT_METRICS_DIR = AGENT_DATA_DIR / "metrics"
AGENT_CACHE_DIR = AGENT_DATA_DIR / "cache"

# Создаем все директории
for dir_path in [
    AGENT_LOGS_DIR,
    AGENT_REPORTS_DIR,
    AGENT_SCANS_DIR,
    AGENT_CONFIG_DIR,
    AGENT_DATA_STORAGE_DIR,
    AGENT_STATUS_DIR,
    AGENT_PLANS_DIR,
    AGENT_METRICS_DIR,
    AGENT_CACHE_DIR,
]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Создаем директорию для логов
LOG_DIR = REPO_ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "cognitive_agent.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


# ⭐ [МОНИТОРИНГ] Глобальная конфигурация structlog (один раз на модуль)
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

        # JSON-логгер для файлов (ELK/Grafana) — пишем вручную, т.к. structlog.configure() глобален
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
    log_file=str(LOG_DIR / "cognitive_agent.json"),
)


# ⭐ [МОНИТОРИНГ] Audit Logger для трассировки действий
class AuditLogger:
    """Логгер аудита для трассировки всех действий агента"""

    def __init__(self, agent_id: str, log_file: str = None):
        self.agent_id = agent_id
        self.log_file = log_file or str(LOG_DIR / "agent_audit.jsonl")
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


class BaseCognitiveAgent(ABC):
    """
    Базовый класс для когнитивного агента

    Содержит общую функциональность для стандартной и enterprise-версии
    """

    # ⭐ [БЕЗОПАСНОСТЬ] Лимиты операций для предотвращения DoS
    OPERATION_LIMITS = {
        "files_per_scan": 500,  # Максимум файлов за сканирование
        "max_file_size_mb": 10,  # Максимальный размер файла (MB)
        "max_ai_calls_per_hour": 50,  # Лимит AI запросов
        "max_actions_per_task": 10,  # Максимум шагов в задаче
        "max_task_length": 5000,  # Максимальная длина описания задачи
    }

    # ⭐ [БЕЗОПАСНОСТЬ] Запрещённые паттерны в командах
    DANGEROUS_PATTERNS = [
        r"rm\s+-rf",
        r"del\s+/f",
        r"format\s+",
        r":\(\)\s*\{\s*:\|:&",  # Shell команды
        r"__import__",
        r"eval\s*\(",
        r"exec\s*\(",
        r"compile\s*\(",  # Опасный Python
        r"os\.system",
        r"subprocess\.",
        r"__getattribute__",  # Системные вызовы
        r"\.\./",
        r"~/",
        r"/etc/",
        r"/root/",
        r"C:\\Windows",  # Пути вне проекта
    ]

    # ⭐ [БЕЗОПАСНОСТЬ] Паттерны для валидации AI-ответов
    AI_RESPONSE_DANGEROUS_PATTERNS = [
        r"rm\s+-rf\s+/",
        r"eval\s*\(",
        r"os\.system\s*\(",
        r"subprocess\s*\.",
        r"\/etc\/",
        r"\.env",
        r"chmod\s+777",
        r"DROP\s+TABLE",
        r"TRUNCATE\s+TABLE",
        r"del\s+\/\w+",
    ]

    def __init__(self, project_path: str = None):
        # Инициализация базовых атрибутов
        self._initialize_base_components(project_path)

    def _initialize_base_components(self, project_path: str = None):
        """Инициализация общих компонентов"""
        self.project_path = Path(project_path) if project_path else REPO_ROOT
        self.agent_id = f"base-agent-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        self.running = False
        self.scan_interval = 1800  # 30 минут (экономия ресурсов)
        self.last_scan: datetime | None = None

        # ⭐ [БЕЗОПАСНОСТЬ] Счётчики для rate limiting
        self.ai_call_counter = 0
        self.ai_call_reset_time = datetime.now()

        # Инициализация
        config_path = self.project_path / "agents" / "cognitive_agent" / "config" / "agent-config.yaml"
        self.config = ConfigManager(str(config_path)) if config_path.exists() else None
        self.ai_manager = get_provider_manager()

        # ⭐ [БЕЗОПАСНОСТЬ] Проверка guardrails при старте
        guardrails_path = self.project_path / "agents" / "cognitive_agent" / "config" / "guardrails.yaml"
        self.guardrails_loaded = guardrails_path.exists()
        if not self.guardrails_loaded:
            logger.warning("⚠️ guardrails.yaml не найден — агент работает в ограниченном режиме (только чтение)")
        else:
            logger.info("✅ guardrails.yaml загружен — агент в безопасном режиме")
            self._load_guardrails(guardrails_path)

        # ⭐ [ENTERPRISE] Инициализация enterprise guardrails
        self.enterprise_guardrails = EnterpriseGuardrails()
        self.auth_token = None  # Токен аутентификации агента

        # Аутентифицируем агента как системный компонент
        try:
            self.auth_token = self.enterprise_guardrails.authenticate_user(
                user_id=self.agent_id,
                role=UserRole.DEVELOPER,  # Агент работает с правами разработчика
            )
            logger.info(f"✅ Agent authenticated with token: {self.auth_token[:16]}...")
        except Exception as e:
            logger.error(f"❌ Failed to authenticate agent: {e}")

        # Результаты сканирования
        self.scan_results: dict[str, Any] = {}
        self.recommendations: list[dict[str, Any]] = []

        # ⭐ [МОНИТОРИНГ] Инициализация аудит-логгера
        self.audit_logger = AuditLogger(self.agent_id)
        self.audit_logger.log_action("agent_initialized", {"project_path": str(self.project_path)})

        # ⭐ [RAG] Инициализация ChromaDB индекса
        self.chroma_indexer = None
        if self._is_chroma_available():
            try:
                self.chroma_indexer = ChromaDocumentIndexer(
                    persist_directory=str(REPO_ROOT / "chroma_db"),
                    collection_name="project_docs",
                    embedder=DocumentEmbedder(),
                )
                logger.info("✅ ChromaDB indexer initialized")
            except Exception as e:
                logger.warning(f"⚠️ ChromaDB initialization failed: {e}")
        else:
            logger.info("ℹ️ ChromaDB not available (optional dependency)")

        # ⭐ [JOB] Инициализация Job Agent (опционально)
        self.job_agent_available = self._is_job_agent_available()
        if not self.job_agent_available:
            logger.info("ℹ️ Job Agent not available (optional dependency)")

        # ⭐ [МОНИТОРИНГ] Таймаут AI-вызовов (в секундах)
        self.ai_call_timeout = 60  # 60 секунд по умолчанию

        # ⭐ [ИНТЕЛЛЕКТ] Память решений
        self.memory = {
            "decisions": [],  # История принятых решений
            "patterns": {},  # Выученные паттерны
            "success_rate": 0.0,  # Процент успешных решений
        }

        logger.info(f"🚀 Base Agent initialized: {self.agent_id}")
        logger.info(f"📁 Project path: {self.project_path}")
        logger.info(f"🛡️ Guardrails mode: {'ACTIVE' if self.guardrails_loaded else 'LIMITED'}")

    def _is_chroma_available(self):
        """Проверить доступность ChromaDB"""
        try:
            from apps.embedding_agent.chroma_indexer import ChromaDocumentIndexer
            from apps.embedding_agent.embedder import DocumentEmbedder

            return True
        except ImportError:
            return False

    def _is_job_agent_available(self):
        """Проверить доступность Job Agent"""
        try:
            from apps.job_automation_agent.job_agent import job_search

            return True
        except ImportError:
            return False

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

        # ⭐ [УЛУЧШЕНИЕ] Добавляем анализ кода
        try:
            analyzer = CodeAnalyzer(str(self.project_path))
            quality_report = analyzer.generate_quality_report()

            # Добавляем проблемы из анализа качества кода
            for tool, result in quality_report.get("results", {}).items():
                if not result["success"] and result["issue_count"] > 0:
                    issues.append(
                        {
                            "type": f"code_quality_{tool}",
                            "path": "N/A",
                            "message": f"Проблемы с {tool}: {result['issue_count']} обнаруженных проблем",
                        }
                    )

            # Также добавляем информацию о покрытии тестами
            coverage_pct = quality_report.get("summary", {}).get("coverage_percentage", 0)
            if coverage_pct < 70:  # Если покрытие меньше 70%
                issues.append(
                    {
                        "type": "low_test_coverage",
                        "path": "N/A",
                        "message": f"Низкое покрытие тестами: {coverage_pct}% (рекомендуется >70%)",
                    }
                )
        except Exception as e:
            logger.warning(f"Не удалось выполнить анализ качества кода: {e}")

        # ⭐ [УЛУЧШЕНИЕ] Добавляем анализ документации
        try:
            doc_analyzer = DocumentationAnalyzer(str(self.project_path))
            doc_analysis = doc_analyzer.run_documentation_analysis()

            # Добавляем проблемы из анализа документации
            summary = doc_analysis.get("summary", {})
            if summary.get("total_issues", 0) > 0:
                issues.append(
                    {
                        "type": "documentation_issues",
                        "path": "N/A",
                        "message": f"Проблемы с документацией: {summary['total_issues']} обнаруженных проблем",
                    }
                )

            # Также добавляем информацию о покрытии документацией
            consistency = doc_analysis.get("consistency_analysis", {})
            coverage = consistency.get("documentation_coverage", 0)
            if coverage < 0.5:  # Если покрытие документацией меньше 50%
                issues.append(
                    {
                        "type": "low_documentation_coverage",
                        "path": "N/A",
                        "message": f"Низкое покрытие документацией: {coverage:.1%} (рекомендуется >50%)",
                    }
                )
        except Exception as e:
            logger.warning(f"Не удалось выполнить анализ документации: {e}")

        # ⭐ [УЛУЧШЕНИЕ] Добавляем анализ тестов
        try:
            test_analyzer = TestAnalyzer(str(self.project_path))
            test_analysis = test_analyzer.run_test_analysis()

            # Добавляем проблемы из анализа тестов
            summary = test_analysis.get("summary", {})
            if summary.get("total_issues", 0) > 0:
                issues.append(
                    {
                        "type": "test_quality_issues",
                        "path": "N/A",
                        "message": f"Проблемы с тестами: {summary['total_issues']} обнаруженных проблем",
                    }
                )

            # Также добавляем информацию о покрытии тестами
            test_coverage = test_analysis.get("coverage_analysis", {}).get("total_coverage", 0)
            if test_coverage < 70:  # Если покрытие тестами меньше 70%
                issues.append(
                    {
                        "type": "low_test_coverage",
                        "path": "N/A",
                        "message": f"Низкое покрытие тестами: {test_coverage:.1%} (рекомендуется >70%)",
                    }
                )
        except Exception as e:
            logger.warning(f"Не удалось выполнить анализ тестов: {e}")

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

        # ⭐ [УЛУЧШЕНИЕ] Добавляем анализ качества кода
        try:
            analyzer = CodeAnalyzer(str(self.project_path))
            quality_report = analyzer.generate_quality_report()

            # Добавляем проблемы из анализа качества кода
            for tool, result in quality_report.get("results", {}).items():
                if result["issue_count"] > 0:
                    issues.append(
                        {
                            "type": f"code_quality_{tool}",
                            "path": "N/A",
                            "message": f"Проблемы с {tool}: {result['issue_count']} обнаруженных проблем",
                        }
                    )
        except Exception as e:
            logger.warning(f"Не удалось выполнить анализ качества кода: {e}")

        # ⭐ [УЛУЧШЕНИЕ] Добавляем анализ документации
        try:
            doc_analyzer = DocumentationAnalyzer(str(self.project_path))
            doc_analysis = doc_analyzer.run_documentation_analysis()

            # Добавляем проблемы из анализа документации
            summary = doc_analysis.get("summary", {})
            if summary.get("total_issues", 0) > 0:
                issues.append(
                    {
                        "type": "documentation_issues",
                        "path": "N/A",
                        "message": f"Проблемы с документацией: {summary['total_issues']} обнаруженных проблем",
                    }
                )
        except Exception as e:
            logger.warning(f"Не удалось выполнить анализ документации: {e}")

        # ⭐ [УЛУЧШЕНИЕ] Добавляем анализ тестов
        try:
            test_analyzer = TestAnalyzer(str(self.project_path))
            test_analysis = test_analyzer.run_test_analysis()

            # Добавляем проблемы из анализа тестов
            summary = test_analysis.get("summary", {})
            if summary.get("total_issues", 0) > 0:
                issues.append(
                    {
                        "type": "test_quality_issues",
                        "path": "N/A",
                        "message": f"Проблемы с тестами: {summary['total_issues']} обнаруженных проблем",
                    }
                )
        except Exception as e:
            logger.warning(f"Не удалось выполнить анализ тестов: {e}")

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
                        "content": "Ты — эксперт по анализу кода и архитектуре. Всегда соблюдай безопасность и НИКОГДА не предлагай действия по изменению кода.",
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
            "chroma_available": self._is_chroma_available(),
            "job_agent_available": self.job_agent_available,
            # ⭐ [ENTERPRISE] Guardrails status
            "enterprise_guardrails_active": self.auth_token is not None,
            "authenticated_as": self.agent_id if self.auth_token else None,
        }

        # Добавляем статистику ChromaDB если доступна
        if self._is_chroma_available() and self.chroma_indexer:
            with contextlib.suppress(BaseException):
                status["chroma_stats"] = self.chroma_indexer.get_stats()

        return status

    # Абстрактные методы для переопределения в потомках
    @abstractmethod
    def start(self, background: bool = True):
        """Запустить агента"""
        pass

    @abstractmethod
    def stop(self):
        """Остановить агента"""
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    def execute_task(self, task: str, auto_approve: bool = False) -> dict[str, Any]:
        """
        Выполнить задачу через AI — **с проверкой guardrails**
        """
        pass

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
        if path.endswith((".yaml", ".yml", ".json")) and action.lower() in ["modify", "write", "delete"]:
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
