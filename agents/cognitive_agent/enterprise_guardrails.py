"""
Enterprise-level security controls for Cognitive Agent
Implementing AAA (Authentication, Authorization, Accounting)
and fine-grained access control
"""

import logging
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

    def __init__(self, secret_key: str = None):
        self.secret_key = secret_key or secrets.token_hex(32)
        self.sessions: dict[str, UserSession] = {}
        self.session_timeout = timedelta(hours=1)
        self.max_concurrent_sessions = 5

    def create_session(self, user_id: str, role: UserRole, ip_address: str = "127.0.0.1") -> str:
        """Создать сессию для пользователя"""
        # Проверить лимит сессий
        user_sessions = [s for s in self.sessions.values() if s.user_id == user_id]
        if len(user_sessions) >= self.max_concurrent_sessions:
            raise Exception(f"Maximum sessions reached for user {user_id}")

        # Создать токен
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + self.session_timeout

        session = UserSession(
            user_id=user_id,
            role=role,
            created_at=datetime.utcnow(),
            expires_at=expires_at,
            token=token,
            ip_address=ip_address,
        )

        self.sessions[token] = session
        logger.info(f"Session created for user {user_id} with role {role.value}")
        return token

    def verify_token(self, token: str) -> UserSession | None:
        """Проверить валидность токена"""
        session = self.sessions.get(token)
        if not session:
            return None

        if datetime.utcnow() > session.expires_at:
            del self.sessions[token]  # Удалить просроченную сессию
            return None

        return session

    def refresh_session(self, token: str) -> bool:
        """Обновить время жизни сессии"""
        session = self.verify_token(token)
        if session:
            session.expires_at = datetime.utcnow() + self.session_timeout
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

    def check_access(self, user_role: UserRole, file_path: str, action: AccessLevel) -> dict[str, any]:
        """Проверить доступ к файлу"""
        path = Path(file_path).as_posix()  # Привести к POSIX формату

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

    def __init__(self):
        self.auth_manager = AuthenticationManager()
        self.authz_manager = AuthorizationManager()
        self.audit_log = []

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

    def _log_audit(self, event_type: str, user_id: str, role: str, details: str):
        """Залогировать событие в аудит-лог"""
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "user_id": user_id,
            "role": role,
            "details": details,
        }
        self.audit_log.append(audit_entry)
        logger.info(f"Audit: {event_type} - {user_id}({role}): {details}")

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
