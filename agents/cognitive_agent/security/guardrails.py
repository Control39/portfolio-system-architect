"""
Модуль расширенных правил безопасности и надежности для Cognitive Agent
"""

import re
import threading
from collections.abc import Callable
from datetime import datetime
from enum import Enum
from typing import Any

from ..common.base_logger import BaseLogger
from ..common.base_security import BaseSecurityChecker
from ..common.exceptions import SecurityViolationError


class SecurityLevel(Enum):
    """Уровень безопасности"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class GuardrailRule:
    """Правило безопасности"""

    def __init__(
        self,
        name: str,
        description: str,
        level: SecurityLevel,
        validator: Callable[[Any], tuple[bool, str]],
        enabled: bool = True,
    ):
        """
        Инициализировать правило безопасности

        Args:
            name: Название правила
            description: Описание правила
            level: Уровень безопасности
            validator: Функция валидации (возвращает (успешно ли, сообщение))
            enabled: Включено ли правило
        """
        self.name = name
        self.description = description
        self.level = level
        self.validator = validator
        self.enabled = enabled
        self.last_checked = None
        self.violation_count = 0


class EnterpriseGuardrails:
    """
    Расширенная система безопасности и надежности для Cognitive Agent
    """

    def __init__(self, logger: BaseLogger | None = None, security_checker: BaseSecurityChecker | None = None):
        """
        Инициализировать систему безопасности и надежности

        Args:
            logger: Логгер для записи событий
            security_checker: Проверяльщик безопасности
        """
        self.logger = logger or BaseLogger("EnterpriseGuardrails")
        self.security_checker = security_checker or BaseSecurityChecker()

        # Словарь правил безопасности
        self.rules: dict[str, GuardrailRule] = {}

        # Журнал аудита
        self.audit_log: list[dict[str, Any]] = []

        # Блокировка для потокобезопасности
        self._lock = threading.RLock()

        # Инициализировать стандартные правила
        self._initialize_standard_rules()

        self.logger.info("Система безопасности и надежности инициализирована")

    def _initialize_standard_rules(self):
        """
        Инициализировать стандартные правила безопасности
        """
        # Правило проверки команд на опасные паттерны
        dangerous_commands_rule = GuardrailRule(
            name="dangerous_command_check",
            description="Проверка команд на опасные паттерны",
            level=SecurityLevel.HIGH,
            validator=self._validate_dangerous_commands,
        )

        # Правило проверки путей к файлам
        file_path_rule = GuardrailRule(
            name="file_path_validation",
            description="Проверка путей к файлам на безопасность",
            level=SecurityLevel.HIGH,
            validator=self._validate_file_paths,
        )

        # Правило проверки кода на опасные конструкции
        code_security_rule = GuardrailRule(
            name="code_security_check",
            description="Проверка кода на потенциально опасные конструкции",
            level=SecurityLevel.CRITICAL,
            validator=self._validate_code_security,
        )

        # Правило проверки на чрезмерное использование ресурсов
        resource_usage_rule = GuardrailRule(
            name="resource_usage_limit",
            description="Проверка на чрезмерное использование ресурсов",
            level=SecurityLevel.MEDIUM,
            validator=self._validate_resource_usage,
        )

        # Правило проверки этических норм
        ethical_norms_rule = GuardrailRule(
            name="ethical_norms_check",
            description="Проверка действий на соответствие этическим нормам",
            level=SecurityLevel.MEDIUM,
            validator=self._validate_ethical_norms,
        )

        # Добавить правила в систему
        self.add_rule(dangerous_commands_rule)
        self.add_rule(file_path_rule)
        self.add_rule(code_security_rule)
        self.add_rule(resource_usage_rule)
        self.add_rule(ethical_norms_rule)

    def add_rule(self, rule: GuardrailRule) -> bool:
        """
        Добавить правило безопасности

        Args:
            rule: Правило безопасности

        Returns:
            Успешно ли добавлено
        """
        with self._lock:
            if rule.name in self.rules:
                self.logger.warning(f"Правило с именем {rule.name} уже существует, заменяется")

            self.rules[rule.name] = rule
            self.logger.info(
                f"Добавлено правило безопасности: {rule.name}", level=rule.level.value, description=rule.description
            )
            return True

    def remove_rule(self, rule_name: str) -> bool:
        """
        Удалить правило безопасности

        Args:
            rule_name: Имя правила для удаления

        Returns:
            Успешно ли удалено
        """
        with self._lock:
            if rule_name in self.rules:
                del self.rules[rule_name]
                self.logger.info(f"Удалено правило безопасности: {rule_name}")
                return True
            return False

    def enable_rule(self, rule_name: str) -> bool:
        """
        Включить правило безопасности

        Args:
            rule_name: Имя правила для включения

        Returns:
            Успешно ли включено
        """
        with self._lock:
            if rule_name in self.rules:
                self.rules[rule_name].enabled = True
                self.logger.debug(f"Включено правило безопасности: {rule_name}")
                return True
            return False

    def disable_rule(self, rule_name: str) -> bool:
        """
        Выключить правило безопасности

        Args:
            rule_name: Имя правила для выключения

        Returns:
            Успешно ли выключено
        """
        with self._lock:
            if rule_name in self.rules:
                self.rules[rule_name].enabled = False
                self.logger.debug(f"Выключено правило безопасности: {rule_name}")
                return True
            return False

    def validate_action(self, action: str, context: dict[str, Any]) -> tuple[bool, list[str]]:
        """
        Проверить действие на соответствие правилам безопасности

        Args:
            action: Действие для проверки
            context: Контекст действия

        Returns:
            Кортеж (действие разрешено, список нарушений)
        """
        violations = []

        with self._lock:
            for rule_name, rule in self.rules.items():
                if not rule.enabled:
                    continue

                try:
                    is_valid, message = rule.validator(context)

                    if not is_valid:
                        violation = f"Нарушение правила '{rule_name}' ({rule.level.value}): {message}"
                        violations.append(violation)

                        # Обновить счетчик нарушений
                        rule.violation_count += 1

                        # Записать в журнал аудита
                        self._log_audit_event(
                            rule_name=rule_name, action=action, context=context, violation=message, level=rule.level
                        )

                    # Обновить время последней проверки
                    rule.last_checked = datetime.now()

                except Exception as e:
                    self.logger.error(
                        f"Ошибка при проверке правила {rule_name}: {str(e)}", rule_name=rule_name, action=action
                    )
                    # Считать действие недействительным при ошибке проверки
                    violation = f"Ошибка проверки правила '{rule_name}': {str(e)}"
                    violations.append(violation)

        is_allowed = len(violations) == 0

        if is_allowed:
            self.logger.debug(f"Действие разрешено: {action}", context_keys=list(context.keys()))
        else:
            self.logger.warning(f"Действие заблокировано: {action}", violations=violations)

        return is_allowed, violations

    def _validate_dangerous_commands(self, context: dict[str, Any]) -> tuple[bool, str]:
        """
        Проверить контекст на опасные команды

        Args:
            context: Контекст для проверки

        Returns:
            Кортеж (валидно ли, сообщение)
        """
        command = context.get("command", "")

        # Проверить на опасные команды
        is_safe, message = self.security_checker.validate_command(command)

        return is_safe, message

    def _validate_file_paths(self, context: dict[str, Any]) -> tuple[bool, str]:
        """
        Проверить пути к файлам в контексте

        Args:
            context: Контекст для проверки

        Returns:
            Кортеж (валидно ли, сообщение)
        """
        file_paths = context.get("file_paths", [])

        for path in file_paths:
            is_safe, message = self.security_checker.validate_path(path)
            if not is_safe:
                return False, message

        # Также проверить отдельные поля, содержащие пути
        for key, value in context.items():
            if "path" in key.lower() and isinstance(value, str):
                is_safe, message = self.security_checker.validate_path(value)
                if not is_safe:
                    return False, f"Небезопасный путь в поле {key}: {message}"

        return True, "Все пути к файлам безопасны"

    def _validate_code_security(self, context: dict[str, Any]) -> tuple[bool, str]:
        """
        Проверить код на опасные конструкции

        Args:
            context: Контекст для проверки

        Returns:
            Кортеж (валидно ли, сообщение)
        """
        code_snippets = context.get("code_snippets", [])

        for snippet in code_snippets:
            is_safe, message = self.security_checker.validate_code(snippet)
            if not is_safe:
                return False, message

        # Также проверить отдельные поля, содержащие код
        for key, value in context.items():
            if "code" in key.lower() and isinstance(value, str):
                is_safe, message = self.security_checker.validate_code(value)
                if not is_safe:
                    return False, f"Небезопасный код в поле {key}: {message}"

        return True, "Код безопасен"

    def _validate_resource_usage(self, context: dict[str, Any]) -> tuple[bool, str]:
        """
        Проверить использование ресурсов

        Args:
            context: Контекст для проверки

        Returns:
            Кортеж (валидно ли, сообщение)
        """
        # Проверить размеры данных
        data_size = context.get("data_size", 0)
        max_allowed_size = 100 * 1024 * 1024  # 100MB

        if data_size > max_allowed_size:
            return False, f"Превышен лимит размера данных: {data_size} > {max_allowed_size}"

        # Проверить количество операций
        operations_count = context.get("operations_count", 0)
        max_operations = 1000

        if operations_count > max_operations:
            return False, f"Превышен лимит количества операций: {operations_count} > {max_operations}"

        # Проверить длительность операций
        estimated_duration = context.get("estimated_duration", 0)
        max_duration = 300  # 5 минут

        if estimated_duration > max_duration:
            return False, f"Превышен лимит длительности операции: {estimated_duration} > {max_duration} секунд"

        return True, "Использование ресурсов в пределах допустимых значений"

    def _validate_ethical_norms(self, context: dict[str, Any]) -> tuple[bool, str]:
        """
        Проверить соответствие этическим нормам

        Args:
            context: Контекст для проверки

        Returns:
            Кортеж (валидно ли, сообщение)
        """
        # Проверить на дискриминационный контент
        content = context.get("content", "")

        discriminatory_patterns = [
            r"\b(дискриминаци[яиоа]|дискриминирующ|предвзят|предвзятость)\b",
            r"\b(нацист|фашист|экстремист|радикал)\b",
            r"\b(уничижительн|оскорбл|ругательств|ненависть)\b",
        ]

        for pattern in discriminatory_patterns:
            if re.search(pattern, content, re.IGNORECASE | re.UNICODE):
                return False, "Обнаружен потенциально дискриминационный контент"

        # Проверить на вредоносные инструкции
        harmful_instructions = [
            r"\b(вред|поврежд|уничтож|уничтожение|взлом|взломать|обман|обмануть)\b",
            r"\b(вредоносн|вредный|опасн|угроз|угрожающ)\b",
        ]

        for pattern in harmful_instructions:
            if re.search(pattern, content, re.IGNORECASE | re.UNICODE):
                return False, "Обнаружены потенциально вредоносные инструкции"

        return True, "Содержание соответствует этическим нормам"

    def _log_audit_event(
        self, rule_name: str, action: str, context: dict[str, Any], violation: str, level: SecurityLevel
    ):
        """
        Записать событие в журнал аудита

        Args:
            rule_name: Имя правила
            action: Действие
            context: Контекст
            violation: Нарушение
            level: Уровень безопасности
        """
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "rule_name": rule_name,
            "action": action,
            "context_summary": self._sanitize_context(context),
            "violation": violation,
            "level": level.value,
            "session_id": context.get("session_id", "unknown"),
        }

        with self._lock:
            self.audit_log.append(audit_entry)

        # Логировать событие аудита
        try:
            self.logger.warning(
                f"Нарушение безопасности: {violation}",
                rule_name=rule_name,
                action=action,
                level=level.value,
                session_id=audit_entry["session_id"],
            )
        except Exception as e:
            self.logger.error(f"Ошибка при логировании события аудита: {str(e)}")

    def _sanitize_context(self, context: dict[str, Any]) -> dict[str, Any]:
        """
        Очистить контекст для журнала аудита (удалить чувствительные данные)

        Args:
            context: Контекст для очистки

        Returns:
            Очищенный контекст
        """
        sanitized = {}
        sensitive_keys = ["password", "token", "secret", "key", "auth", "credential"]

        for key, value in context.items():
            if any(sensitive_key in key.lower() for sensitive_key in sensitive_keys):
                sanitized[key] = "***SANITIZED***"
            else:
                # Ограничить размер значений для журнала
                if isinstance(value, str) and len(value) > 1000:
                    sanitized[key] = value[:1000] + "...[TRUNCATED]"
                else:
                    sanitized[key] = value

        return sanitized

    def get_audit_log(self, limit: int = 100) -> list[dict[str, Any]]:
        """
        Получить журнал аудита

        Args:
            limit: Ограничение на количество записей

        Returns:
            Список записей журнала аудита
        """
        with self._lock:
            return self.audit_log[-limit:]

    def get_violation_statistics(self) -> dict[str, Any]:
        """
        Получить статистику нарушений

        Returns:
            Статистика нарушений
        """
        with self._lock:
            total_violations = len(self.audit_log)
            violations_by_level = {}
            violations_by_rule = {}

            for entry in self.audit_log:
                level = entry["level"]
                rule_name = entry["rule_name"]

                violations_by_level[level] = violations_by_level.get(level, 0) + 1
                violations_by_rule[rule_name] = violations_by_rule.get(rule_name, 0) + 1

            # Также получить счетчики нарушений из самих правил
            rule_violations = {}
            for name, rule in self.rules.items():
                rule_violations[name] = rule.violation_count

            return {
                "total_violations": total_violations,
                "violations_by_level": violations_by_level,
                "violations_by_rule": violations_by_rule,
                "rule_violation_counts": rule_violations,
                "timestamp": datetime.now().isoformat(),
            }

    def enforce_guardrails(
        self, action: str, context: dict[str, Any], raise_exception: bool = True
    ) -> tuple[bool, list[str]]:
        """
        Принудительно применить правила безопасности

        Args:
            action: Действие для проверки
            context: Контекст действия
            raise_exception: Поднимать ли исключение при нарушении

        Returns:
            Кортеж (действие разрешено, список нарушений)
        """
        is_allowed, violations = self.validate_action(action, context)

        if not is_allowed and raise_exception:
            violation_msg = "; ".join(violations)
            raise SecurityViolationError(
                f"Нарушение правил безопасности: {violation_msg}",
                details={"action": action, "violations": violations, "context_keys": list(context.keys())},
            )

        return is_allowed, violations


class GuardrailDecorator:
    """
    Декоратор для применения правил безопасности к функциям
    """

    def __init__(self, guardrails: EnterpriseGuardrails, context_extractor: Callable | None = None):
        """
        Инициализировать декоратор

        Args:
            guardrails: Система правил безопасности
            context_extractor: Функция извлечения контекста из аргументов
        """
        self.guardrails = guardrails
        self.context_extractor = context_extractor or self._default_context_extractor

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            # Извлечь контекст
            context = self.context_extractor(args, kwargs)

            # Проверить на безопасность
            is_allowed, violations = self.guardrails.validate_action(action=func.__name__, context=context)

            if not is_allowed:
                # Логировать нарушения
                for violation in violations:
                    self.guardrails.logger.warning(f"Нарушение безопасности в функции {func.__name__}: {violation}")

                # Поднять исключение
                raise SecurityViolationError(
                    f"Доступ к функции {func.__name__} заблокирован из-за нарушения безопасности",
                    details={"violations": violations},
                )

            # Выполнить функцию
            return func(*args, **kwargs)

        return wrapper

    def _default_context_extractor(self, args, kwargs) -> dict[str, Any]:
        """
        Извлечь контекст по умолчанию из аргументов

        Args:
            args: Позиционные аргументы
            kwargs: Ключевые аргументы

        Returns:
            Контекст из аргументов
        """
        context = {"args": args, "kwargs": kwargs}

        # Попробовать извлечь специфичные поля
        if args:
            if isinstance(args[0], dict):
                context.update(args[0])  # Обычно первый аргумент - контекст

        context.update(kwargs)

        return context
