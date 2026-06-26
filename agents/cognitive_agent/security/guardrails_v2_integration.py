"""
Guardrails V2 Integration Module

Интеграция системы безопасности guardrails версии 2.0
Включает:
- Pydantic валидацию конфигурации
- Контекстно-зависимые правила
- MIME-типы файлов
- Sandbox execution
- Rate limiting
- Audit logging
- Проверку кода на опасные конструкции (eval, exec, subprocess, etc.)
"""

import hashlib
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

from agents.cognitive_agent.src.models.guardrails import GuardrailsV2

logger = logging.getLogger(__name__)


class GuardrailsV2Integration:
    """
    Интеграция guardrails v2.0 в агент

    Обеспечивает:
    - Валидацию конфигурации через Pydantic
    - Контекстную проверку правил
    - Интеграцию с file type validator
    - Интеграцию с sandbox executor
    - Проверку кода на опасные конструкции
    """

    def __init__(self, guardrails_path: Optional[Path] = None):
        """
        Инициализация guardrails v2.0

        Args:
            guardrails_path: Путь к файлу guardrails.yaml
        """
        self.guardrails_path = guardrails_path
        self.guardrails_config: Optional[GuardrailsV2] = None
        self.guardrails_loaded = False
        self.environment = "development"
        self.current_user_role = "developer"

        if guardrails_path and guardrails_path.exists():
            self.load_guardrails(guardrails_path)

    def load_guardrails(self, guardrails_path: Path) -> bool:
        """Загрузить и валидировать guardrails.yaml"""
        try:
            with open(guardrails_path, encoding="utf-8") as f:
                raw_config = yaml.safe_load(f)

            self.guardrails_config = GuardrailsV2(**raw_config)

            logger.info(f"✅ Guardrails v2.0 loaded from {guardrails_path}")
            self.guardrails_loaded = True
            return True

        except Exception as e:
            logger.error(f"❌ Guardrails v2.0 loading failed: {e}")
            self.guardrails_loaded = False
            self.guardrails_config = None
            return False

    def _check_dangerous_code(self, code: str) -> Tuple[bool, str]:
        """
        Проверка кода на опасные конструкции

        Args:
            code: Python-код для проверки

        Returns:
            tuple[bool, str]: (безопасен ли, причина)
        """
        if not code:
            return True, "Empty code"

        # Опасные паттерны
        dangerous_patterns = [
            # Выполнение произвольного кода
            (r"eval\s*\(", "eval() execution"),
            (r"exec\s*\(", "exec() execution"),
            (r"__import__\s*\(", "__import__() execution"),
            (r"compile\s*\(", "compile() execution"),
            # Системные команды
            (r"subprocess\s*\.\s*run\s*\(", "subprocess.run()"),
            (r"subprocess\s*\.\s*call\s*\(", "subprocess.call()"),
            (r"subprocess\s*\.\s*Popen\s*\(", "subprocess.Popen()"),
            (r"os\.system\s*\(", "os.system()"),
            (r"os\.popen\s*\(", "os.popen()"),
            # Деструктивные операции
            (r"shutil\.rmtree\s*\(", "shutil.rmtree()"),
            (r"os\.remove\s*\(", "os.remove()"),
            (r"os\.rmdir\s*\(", "os.rmdir()"),
            (r"pathlib.*\.unlink\s*\(", "Path.unlink()"),
            (r"pathlib.*\.rmdir\s*\(", "Path.rmdir()"),
            # Форматирование дисков (Windows)
            (r"format\s+[a-zA-Z]:", "Disk formatting"),
            # Удаление с рекурсией
            (r"rm\s+-rf\s+", "rm -rf"),
            (r"del\s+/[fs]", "del /f /s"),
            # Десериализация
            (r"pickle\.loads\s*\(", "pickle.loads()"),
            (r"pickle\.load\s*\(", "pickle.load()"),
            # Небезопасный YAML
            (r"yaml\.load\s*\([^,]*\)", "yaml.load() without safe"),
        ]

        for pattern, description in dangerous_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                lines = code.split("\n")
                for i, line in enumerate(lines):
                    if re.search(pattern, line, re.IGNORECASE):
                        line_num = i + 1
                        line_preview = line.strip()[:100]
                        return False, f"Dangerous code at line {line_num}: {description} (code: {line_preview}...)"

                return False, f"Dangerous code detected: {description}"

        # Проверка размера кода
        max_code_size = self.guardrails_config.max_code_size if self.guardrails_config else 1024 * 1024
        if len(code) > max_code_size:
            return False, f"Code size exceeds limit: {len(code)} > {max_code_size}"

        return True, "Code is safe"

    def check_guardrail(
        self,
        action: str,
        path: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Tuple[bool, str]:
        """
        Умная проверка guardrails с учётом контекста

        Args:
            action: Действие (read, write, execute, delete)
            path: Путь к файлу или ресурсу
            context: Дополнительный контекст (environment, user_role, code, etc.)

        Returns:
            tuple[bool, str]: (разрешено, причина)
        """
        if not self.guardrails_loaded or not self.guardrails_config:
            return True, "Guardrails not loaded - allowing by default"

        ctx = context or {}
        environment = ctx.get("environment", self.environment)
        user_role = ctx.get("user_role", self.current_user_role)

        # 1. Проверка опасных действий (Blacklist)
        if action in self.guardrails_config.dangerous_actions:
            return False, f"Dangerous action '{action}' is explicitly blocked"

        # 2. Проверка разрешённых действий (Whitelist)
        if self.guardrails_config.safe_actions and action not in self.guardrails_config.safe_actions:
            return False, f"Action '{action}' is not in the safe actions list"

        # 3. Проверка заблокированных паттернов
        for pattern in self.guardrails_config.blocked_patterns:
            try:
                if re.search(pattern, path, re.IGNORECASE):
                    return False, f"Path '{path}' matches blocked pattern '{pattern}'"
            except re.error:
                pass

        # 4. Проверка разрешённых путей
        if self.guardrails_config.allowed_paths:
            allowed = False
            for allowed_pattern in self.guardrails_config.allowed_paths:
                try:
                    if re.match(allowed_pattern, path, re.IGNORECASE):
                        allowed = True
                        break
                except re.error:
                    pass

            if not allowed:
                return False, f"Path '{path}' is not within allowed boundaries"

        # 5. Контекстные правила
        for rule_data in self.guardrails_config.context_aware_rules:
            rule_name = rule_data.get("name", "unknown")
            condition = rule_data.get("condition", "")
            forbidden_actions = rule_data.get("forbidden_actions", [])
            required_approval = rule_data.get("required_approval", False)
            approvers = rule_data.get("approvers", [])

            if condition == "environment == 'production'":
                if environment == "production" and action in forbidden_actions:
                    return False, f"Action '{action}' forbidden in production (rule: {rule_name})"

            if required_approval and action in forbidden_actions:
                approvers_str = ", ".join(approvers) if approvers else "admin"
                return False, f"Sensitive operation requires approval from {approvers_str} (rule: {rule_name})"

            role_condition = f"user_role == '{user_role}'"
            if condition == role_condition and action in forbidden_actions:
                return False, f"Action '{action}' forbidden for role '{user_role}' (rule: {rule_name})"

        # 6. ⭐ Проверка кода на опасные конструкции (если передан code)
        code = ctx.get("code", "")
        if code:
            is_safe, reason = self._check_dangerous_code(code)
            if not is_safe:
                return False, reason

        return True, "OK"

    def validate_file_type(self, file_path: Path) -> Tuple[bool, str]:
        """Проверить тип файла"""
        try:
            from agents.cognitive_agent.security.file_type_validator import FileTypeValidator

            validator = FileTypeValidator()
            return validator.validate_file(file_path)
        except ImportError:
            return True, "File type validation not available"

    def execute_in_sandbox(self, command: str, timeout: int = 30) -> Dict[str, Any]:
        """Выполнить команду в sandbox"""
        try:
            from agents.cognitive_agent.security.sandbox_executor import SandboxExecutor

            executor = SandboxExecutor()
            return executor.execute(command, timeout=timeout)
        except Exception as e:
            return {"success": False, "error": str(e), "exit_code": -1, "output": ""}

    def get_rate_limits(self) -> Dict[str, int]:
        """Получить лимиты из конфигурации"""
        if not self.guardrails_config:
            return {"max_requests_per_minute": 60, "max_ai_calls_per_hour": 100, "max_file_operations_per_minute": 300}
        return self.guardrails_config.rate_limiting or {}

    def should_log_audit(self, action: str) -> bool:
        """Проверить нужно ли логировать действие"""
        if not self.guardrails_config:
            return True
        audit_config = self.guardrails_config.audit_trail or {}
        return audit_config.get("enabled", True)

    def get_audit_config(self) -> Dict[str, Any]:
        """Получить конфигурацию аудита"""
        if not self.guardrails_config:
            return {"enabled": True, "log_level": "INFO", "retention_days": 90, "encryption": True}
        audit_config = self.guardrails_config.audit_trail or {}
        return {
            "enabled": audit_config.get("enabled", True),
            "log_level": audit_config.get("log_level", "INFO"),
            "retention_days": audit_config.get("retention_days", 90),
            "encryption": audit_config.get("encryption", True),
        }

    def set_environment(self, environment: str):
        """Установить окружение"""
        self.environment = environment

    def set_user_role(self, role: str):
        """Установить роль пользователя"""
        self.current_user_role = role


# Глобальный экземпляр
_guardrails_v2_instance: Optional[GuardrailsV2Integration] = None


def get_guardrails_v2(guardrails_path: Optional[Path] = None) -> GuardrailsV2Integration:
    global _guardrails_v2_instance
    if _guardrails_v2_instance is None:
        _guardrails_v2_instance = GuardrailsV2Integration(guardrails_path)
    return _guardrails_v2_instance
