"""
Enterprise-level security controls for Cognitive Agent
Implementing AAA (Authentication, Authorization, Accounting)
and fine-grained access control
"""

import hashlib
import logging
import os
import re
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path

# Настройка логирования
logger = logging.getLogger(__name__)


class UserRole(Enum):
    """Роли пользователей в системе"""

    ADMIN = "admin"
    DEVELOPER = "developer"
    AUDITOR = "auditor"


class AccessLevel(Enum):
    """Уровни доступа"""

    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    DELETE = "delete"


@dataclass
class UserSession:
    """Информация о сессии пользователя"""

    user_id: str
    role: UserRole
    created_at: datetime
    expires_at: datetime
    token: str
    ip_address: str = "127.0.0.1"


@dataclass
class FileAccessRule:
    """Правило доступа к файлам"""

    pattern: str  # Regex pattern for file path
    allowed_roles: set[UserRole]
    allowed_actions: set[AccessLevel]
    approval_required: bool = False
    requires_two_factor: bool = False
    description: str = ""


class AuthenticationManager:
    """Менеджер аутентификации"""

    def __init__(self, secret_key: str | None = None):
        # ✅ БЕЗОПАСНОСТЬ: Загружать secret_key из переменной окружения
        # Приоритет: явный параметр > COGNITIVE_AGENT_SECRET_KEY > GIGACHAT_API_KEY > GIGACHAT_CLIENT_SECRET
        self.secret_key = (
            secret_key
            or os.environ.get("COGNITIVE_AGENT_SECRET_KEY")
            or os.environ.get("GIGACHAT_API_KEY")
            or os.environ.get("GIGACHAT_CLIENT_SECRET")
        )
        if not self.secret_key:
            raise ValueError(
                " neither COGNITIVE_AGENT_SECRET_KEY nor GIGACHAT_API_KEY nor GIGACHAT_CLIENT_SECRET is set. "
                "Please set one of these environment variables."
            )

        self.sessions: dict[str, UserSession] = {}
        self.session_timeout = timedelta(hours=1)
        self.max_concurrent_sessions = 5
        # ✅ БЕЗОПАСНОСТЬ: Хеш-мапа для быстрого поиска сессий по токену
        self._token_hash_index: dict[str, str] = {}

    def _hash_token(self, token: str) -> str:
        """✅ БЕЗОПАСНОСТЬ: Создать хеш токена для безопасного хранения"""
        return hashlib.sha256(token.encode()).hexdigest()

    def create_session(self, user_id: str, role: UserRole, ip_address: str = "127.0.0.1") -> str:
        """Создать сессию для пользователя"""
        # Проверить лимит сессий
        user_sessions = [s for s in self.sessions.values() if s.user_id == user_id]
        if len(user_sessions) >= self.max_concurrent_sessions:
            raise Exception(f"Maximum sessions reached for user {user_id}")

        # Создать токен
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + self.session_timeout

        session = UserSession(
            user_id=user_id,
            role=role,
            created_at=datetime.now(),
            expires_at=expires_at,
            token=token,
            ip_address=ip_address,
        )

        self.sessions[token] = session
        # ✅ БЕЗОПАСНОСТЬ: Индексация по хешу токена
        self._token_hash_index[self._hash_token(token)] = token
        logger.info(f"Session created for user {user_id} with role {role.value}")
        return token

    def verify_token(self, token: str) -> UserSession | None:
        """Проверить валидность токена"""
        session = self.sessions.get(token)
        if not session:
            return None

        if datetime.now() > session.expires_at:
            # Удалить просроченную сессию и её индекс
            token_hash = self._hash_token(token)
            self._token_hash_index.pop(token_hash, None)
            del self.sessions[token]
            return None

        return session

    def refresh_session(self, token: str) -> bool:
        """Обновить время жизни сессии"""
        session = self.verify_token(token)
        if session:
            session.expires_at = datetime.now() + self.session_timeout
            return True
        return False


class AuthorizationManager:
    """Менеджер авторизации"""

    def __init__(self):
        self.file_access_rules: list[FileAccessRule] = [
            # Документация - больше свободы
            FileAccessRule(
                pattern=r"^docs/.*$",
                allowed_roles={UserRole.DEVELOPER, UserRole.AUDITOR, UserRole.ADMIN},
                allowed_actions={AccessLevel.READ, AccessLevel.WRITE},
                approval_required=False,
                description="Documentation files - more access for developers and auditors",
            ),
            # Тесты - свободный доступ для разработчиков
            FileAccessRule(
                pattern=r"^tests/.*$",
                allowed_roles={UserRole.DEVELOPER, UserRole.ADMIN},
                allowed_actions={AccessLevel.READ, AccessLevel.WRITE, AccessLevel.EXECUTE},
                approval_required=False,
                description="Test files - developers can modify and execute",
            ),
            # Конфигурация - ограниченный доступ
            FileAccessRule(
                pattern=r"^config/.*$",
                allowed_roles={UserRole.ADMIN},
                allowed_actions={AccessLevel.READ, AccessLevel.WRITE},
                approval_required=True,
                description="Configuration files - admin only with approval",
            ),
            # Критический код - только чтение
            FileAccessRule(
                pattern=r"^src/core/.*$",
                allowed_roles={UserRole.ADMIN},
                allowed_actions={AccessLevel.READ},
                approval_required=True,
                requires_two_factor=True,
                description="Core source code - read-only with 2FA",
            ),
            # Секреты - запрет доступа
            FileAccessRule(
                pattern=r".*\.(env|key|pem|secret)$",
                allowed_roles=set(),
                allowed_actions=set(),
                approval_required=True,
                requires_two_factor=True,
                description="Secret files - no access allowed",
            ),
            # Apps директории - ограниченный доступ
            FileAccessRule(
                pattern=r"^apps/README\.md$",
                allowed_roles={UserRole.DEVELOPER, UserRole.ADMIN},
                allowed_actions={AccessLevel.READ, AccessLevel.WRITE, AccessLevel.EXECUTE},
                approval_required=False,
                description="apps/README.md - developer access allowed",
            ),
            FileAccessRule(
                pattern=r"^apps/[^/]+/.*$",
                allowed_roles={UserRole.DEVELOPER, UserRole.ADMIN},
                allowed_actions={AccessLevel.READ, AccessLevel.WRITE},
                approval_required=False,
                description="Application services - developer access allowed",
            ),
            # Agents директории - ограниченный доступ
            FileAccessRule(
                pattern=r"^agents/[^/]+/.*$",
                allowed_roles={UserRole.DEVELOPER, UserRole.ADMIN},
                allowed_actions={AccessLevel.READ, AccessLevel.WRITE},
                approval_required=True,
                description="Agent services - restricted access",
            ),
        ]

    def _sanitize_path(self, file_path: str) -> str:
        """
        ✅ БЕЗОПАСНОСТЬ: Санация пути для защиты от path traversal

        Args:
            file_path: Путь от пользователя

        Returns:
            str: Нормализованный путь

        Raises:
            ValueError: Если обнаружен path traversal
        """
        # Удалить потенциально опасные символы
        sanitized = file_path.replace("\\", "/")

        # Проверить на path traversal паттерны
        dangerous_patterns = ["../", "..\\", "/etc/", "/root/", "C:\\Windows"]
        for pattern in dangerous_patterns:
            if pattern in sanitized:
                raise ValueError(f"Path traversal detected: {file_path}")

        # Нормализовать путь
        normalized = Path(sanitized).as_posix()

        # Удалить ведущие слеши для относительных путей
        if normalized.startswith("/"):
            normalized = normalized.lstrip("/")

        return normalized

    def check_access(self, user_role: UserRole, file_path: str, action: AccessLevel) -> dict[str, any]:
        """Проверить доступ к файлу"""
        # ✅ БЕЗОПАСНОСТЬ: Санация пути
        try:
            path = self._sanitize_path(file_path)
        except ValueError as e:
            return {
                "allowed": False,
                "reason": str(e),
                "requires_approval": False,
                "requires_two_factor": False,
                "rule_description": "Security violation",
            }

        # Найти подходящее правило
        applicable_rule = None
        for rule in self.file_access_rules:
            if re.match(rule.pattern, path):
                applicable_rule = rule
                break

        # Если правило не найдено, использовать по умолчанию (запрет)
        if not applicable_rule:
            return {
                "allowed": False,
                "reason": f"No rule found for path: {path}",
                "requires_approval": False,
                "requires_two_factor": False,
                "rule_description": "Default deny policy",
            }

        # Проверить роль
        if user_role not in applicable_rule.allowed_roles:
            return {
                "allowed": False,
                "reason": f"Role {user_role.value} not allowed for path {path}",
                "requires_approval": False,
                "requires_two_factor": False,
                "rule_description": applicable_rule.description,
            }

        # Проверить действие
        if action not in applicable_rule.allowed_actions:
            return {
                "allowed": False,
                "reason": f"Action {action.value} not allowed for path {path}",
                "requires_approval": False,
                "requires_two_factor": False,
                "rule_description": applicable_rule.description,
            }

        # Если всё OK
        return {
            "allowed": True,
            "reason": "Access granted by rule",
            "requires_approval": applicable_rule.approval_required,
            "requires_two_factor": applicable_rule.requires_two_factor,
            "rule_description": applicable_rule.description,
        }

    def get_accessible_paths(self, user_role: UserRole, action: AccessLevel) -> list[str]:
        """Получить список доступных путей для роли и действия"""
        accessible_paths = []
        for rule in self.file_access_rules:
            if user_role in rule.allowed_roles and action in rule.allowed_actions:
                accessible_paths.append(rule.pattern)
        return accessible_paths


class EnterpriseGuardrails:
    """Главный класс enterprise-level guardrails"""

    def __init__(self, config: dict | None = None):
        # ✅ БЕЗОПАСНОСТЬ: Передача secret_key из конфигурации
        # Приоритет: явный параметр > config["secret_key"] > COGNITIVE_AGENT_SECRET_KEY > GIGACHAT_SECRET_KEY
        secret_key = None
        if config and "secret_key" in config:
            secret_key = config["secret_key"]
        self.auth_manager = AuthenticationManager(secret_key=secret_key)
        self.authz_manager = AuthorizationManager()
        self.audit_log = []
        # ✅ БЕЗОПАСНОСТЬ: Ограничение размера аудит-лога
        self.max_audit_log_size = 10000
        # Инициализация правил доступа из конфигурации или использование стандартных
        self.file_access_rules: list[FileAccessRule] = self.authz_manager.file_access_rules

    def authenticate_user(self, user_id: str, role: UserRole, ip_address: str = "127.0.0.1") -> str:
        """Аутентифицировать пользователя и создать сессию"""
        token = self.auth_manager.create_session(user_id, role, ip_address)
        self._log_audit("AUTHENTICATE", user_id, role.value, f"Session created with token {token[:8]}...")
        return token

    def authorize_file_access(self, token: str, file_path: str, action: AccessLevel) -> dict[str, any]:
        """Авторизовать доступ к файлу"""
        session = self.auth_manager.verify_token(token)
        if not session:
            return {
                "allowed": False,
                "reason": "Invalid or expired token",
                "requires_approval": False,
                "requires_two_factor": False,
            }

        result = self.authz_manager.check_access(session.role, file_path, action)

        # Залогировать попытку доступа
        self._log_audit(
            "FILE_ACCESS_ATTEMPT",
            session.user_id,
            session.role.value,
            f"Path: {file_path}, Action: {action.value}, Result: {'ALLOWED' if result['allowed'] else 'DENIED'}",
        )

        return result

    @staticmethod
    def _mask_sensitive_data(data: str) -> str:
        """✅ БЕЗОПАСНОСТЬ: Маскировка чувствительных данных для логов"""
        if not data:
            return ""
        if len(data) <= 8:
            return "*" * len(data)
        return data[:4] + "*" * (len(data) - 8) + data[-4:]

    def _log_audit(self, event_type: str, user_id: str, role: str, details: str):
        """Залогировать событие в аудит-лог"""
        # ✅ БЕЗОПАСНОСТЬ: Маскировка токенов и чувствительных данных в логах
        masked_details = details
        if "token" in details.lower():
            # Найти токен в строке и замаскировать его
            masked_details = self._mask_sensitive_data(details)

        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "user_id": user_id,
            "role": role,
            "details": masked_details,
        }
        self.audit_log.append(audit_entry)

        # ✅ БЕЗОПАСНОСТЬ: Ограничение размера логов
        if len(self.audit_log) > self.max_audit_log_size:
            self.audit_log = self.audit_log[-self.max_audit_log_size // 2 :]

        logger.info(f"Audit: {event_type} - {user_id}({role}): {masked_details}")

    def log_security_event(self, event_type: str, user_id: str, resource: str, outcome: str):
        """Логировать событие безопасности"""
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "user_id": user_id,
            "resource": resource,
            "outcome": outcome,
        }
        self.audit_log.append(audit_entry)
        logger.info(f"Security Event: {event_type} - {user_id}: {resource} = {outcome}")

    def get_audit_trail(self, user_id: str = None, event_type: str = None, limit: int = 100) -> list[dict]:
        """Получить аудит- trail"""
        trail = self.audit_log.copy()

        if user_id:
            trail = [entry for entry in trail if entry["user_id"] == user_id]

        if event_type:
            trail = [entry for entry in trail if entry["event_type"] == event_type]

        return trail[-limit:]  # Последние N записей

    def validate_token(self, token: str) -> bool:
        """Проверить валидность токена"""
        return self.auth_manager.verify_token(token) is not None

    def add_file_access_rule(self, rule: FileAccessRule):
        """Добавить правило доступа к файлам"""
        self.file_access_rules.append(rule)
        self.authz_manager.file_access_rules.append(rule)
        logger.info(f"File access rule added for pattern: {rule.pattern}")

    def validate_file_access(self, token: str, file_path: str, access_level: AccessLevel) -> bool:
        """Валидировать доступ к файлу"""
        session = self.auth_manager.verify_token(token)
        if not session:
            return False

        result = self.authz_manager.check_access(session.role, file_path, access_level)
        return result.get("allowed", False)

    def validate_command_execution(self, token: str, command: str, allowed_commands: list[str]) -> tuple[bool, str]:
        """Валидировать выполнение команды"""
        session = self.auth_manager.verify_token(token)
        if not session:
            return False, "Invalid or expired token"

        # Проверить, разрешена ли команда
        cmd_parts = command.strip().split()
        if not cmd_parts:
            return False, "Empty command"

        cmd_base = cmd_parts[0]

        if cmd_base not in allowed_commands:
            return False, f"Command '{cmd_base}' is not in the allowed list"

        # Проверить на опасные паттерны
        dangerous_patterns = [";", "|", "&", "$", "`", "\\", ">", "<"]
        for pattern in dangerous_patterns:
            if pattern in command:
                return False, f"Dangerous character '{pattern}' detected in command"

        return True, "Command is safe"

    def check_privilege_escalation(self, token: str, requested_role: UserRole) -> bool:
        """Проверить попытку эскалации привилегий"""
        session = self.auth_manager.verify_token(token)
        if not session:
            return False

        # Определить иерархию ролей (ADMIN > DEVELOPER > AUDITOR)
        role_hierarchy = {
            UserRole.ADMIN: 3,
            UserRole.DEVELOPER: 2,
            UserRole.AUDITOR: 1,
        }

        current_level = role_hierarchy.get(session.role, 0)
        requested_level = role_hierarchy.get(requested_role, 0)

        # Если пользователь пытается повысить свою роль - это эскалация, доступ запрещен
        # Возвращаем True только если пользователь может получить запрошенную роль
        return requested_level <= current_level

    def enforce_ethical_constraints(self, content: str) -> tuple[bool, str]:
        """Применить этические ограничения к контенту"""
        if not content:
            return True, "Empty content is allowed"

        # Определить потенциально опасные паттерны
        dangerous_patterns = [
            r"\b(hack|crack|breach|infiltrate)\b",
            r"\b(dangerous|harmful|malicious)\b",
            r"\b(virus|trojan|worm|ransomware)\b",
            r"\b(inject|exploit|payload)\b",
        ]

        import re

        for pattern in dangerous_patterns:
            if re.search(pattern, content.lower()):
                return False, f"Content contains potentially harmful language: {pattern}"

        return True, "Content passes ethical constraints"


# Пример использования
if __name__ == "__main__":
    # Инициализация системы
    guardrails = EnterpriseGuardrails()

    # Аутентификация пользователя
    token = guardrails.authenticate_user("john_dev", UserRole.DEVELOPER)
    print(f"Token created: {token[:16]}...")

    # Попытка доступа к разным файлам
    access_tests = [
        ("docs/readme.md", AccessLevel.WRITE),  # Должно пройти
        ("src/core/auth.py", AccessLevel.WRITE),  # Должно быть запрещено
        ("tests/unit/test_core.py", AccessLevel.EXECUTE),  # Должно пройти
        ("config/database.env", AccessLevel.READ),  # Должно быть запрещено
    ]

    for file_path, action in access_tests:
        result = guardrails.authorize_file_access(token, file_path, action)
        status = "✅ ALLOWED" if result["allowed"] else "❌ DENIED"
        print(f"{status}: {action.value} {file_path} - {result['reason']}")

    # Показать аудит-лог
    print("\nRecent audit events:")
    for event in guardrails.get_audit_trail(limit=5):
        print(f"  {event['timestamp']}: {event['event_type']} - {event['details']}")
