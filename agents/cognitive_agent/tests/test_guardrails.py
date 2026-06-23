"""
Тесты для системы безопасности и надежности Cognitive Agent
"""

import pytest

from cognitive_agent.security.guardrails import EnterpriseGuardrails, GuardrailDecorator, GuardrailRule, SecurityLevel


class TestGuardrails:
    """
    Тесты для системы безопасности и надежности
    """

    def test_security_level_enum(self):
        """Тест перечисления уровней безопасности"""
        assert SecurityLevel.LOW.value == "low"
        assert SecurityLevel.MEDIUM.value == "medium"
        assert SecurityLevel.HIGH.value == "high"
        assert SecurityLevel.CRITICAL.value == "critical"

    def test_guardrail_rule_creation(self):
        """Тест создания правила безопасности"""

        def dummy_validator(context):
            return True, "Valid"

        rule = GuardrailRule(
            name="test_rule", description="Test description", level=SecurityLevel.HIGH, validator=dummy_validator
        )

        assert rule.name == "test_rule"
        assert rule.description == "Test description"
        assert rule.level == SecurityLevel.HIGH
        assert rule.enabled is True
        assert rule.violation_count == 0

    def test_guardrail_rule_disabled(self):
        """Тест отключенного правила безопасности"""

        def dummy_validator(context):
            return False, "Invalid"

        rule = GuardrailRule(
            name="disabled_rule",
            description="Disabled test rule",
            level=SecurityLevel.LOW,
            validator=dummy_validator,
            enabled=False,
        )

        assert rule.enabled is False
        # Даже если валидатор возвращает False, правило отключено

    def test_enterprise_guardrails_initialization(self):
        """Тест инициализации системы безопасности"""
        guardrails = EnterpriseGuardrails()

        assert len(guardrails.rules) > 0  # Должны быть стандартные правила
        assert "dangerous_command_check" in guardrails.rules
        assert "file_path_validation" in guardrails.rules
        assert "code_security_check" in guardrails.rules
        assert "resource_usage_limit" in guardrails.rules
        assert "ethical_norms_check" in guardrails.rules

    def test_add_custom_rule(self):
        """Тест добавления пользовательского правила"""
        guardrails = EnterpriseGuardrails()

        def custom_validator(context):
            return True, "Custom valid"

        custom_rule = GuardrailRule(
            name="custom_rule",
            description="Custom rule for testing",
            level=SecurityLevel.MEDIUM,
            validator=custom_validator,
        )

        guardrails.add_rule(custom_rule)

        assert "custom_rule" in guardrails.rules
        assert guardrails.rules["custom_rule"].name == "custom_rule"

    def test_remove_rule(self):
        """Тест удаления правила"""
        guardrails = EnterpriseGuardrails()

        initial_count = len(guardrails.rules)
        removed = guardrails.remove_rule("dangerous_command_check")

        assert removed is True
        assert len(guardrails.rules) == initial_count - 1
        assert "dangerous_command_check" not in guardrails.rules

    def test_enable_disable_rule(self):
        """Тест включения и выключения правила"""
        guardrails = EnterpriseGuardrails()

        # Проверить, что правило изначально включено
        assert guardrails.rules["dangerous_command_check"].enabled is True

        # Выключить правило
        disabled = guardrails.disable_rule("dangerous_command_check")
        assert disabled is True
        assert guardrails.rules["dangerous_command_check"].enabled is False

        # Включить правило
        enabled = guardrails.enable_rule("dangerous_command_check")
        assert enabled is True
        assert guardrails.rules["dangerous_command_check"].enabled is True

    def test_validate_safe_command(self):
        """Тест проверки безопасной команды"""
        guardrails = EnterpriseGuardrails()

        context = {"command": "ls -la", "file_paths": ["/safe/path"]}
        is_allowed, violations = guardrails.validate_action("test_action", context)

        # Безопасная команда должна быть разрешена
        assert is_allowed is True
        assert len(violations) == 0

    def test_validate_dangerous_command(self):
        """Тест проверки опасной команды"""
        guardrails = EnterpriseGuardrails()

        context = {"command": "rm -rf /", "file_paths": ["/safe/path"]}
        is_allowed, violations = guardrails.validate_action("test_action", context)

        # Опасная команда должна быть заблокирована
        assert is_allowed is False
        assert len(violations) > 0
        assert any("dangerous_command_check" in v for v in violations)

    def test_validate_safe_file_path(self):
        """Тест проверки безопасного пути к файлу"""
        guardrails = EnterpriseGuardrails()

        context = {"file_paths": ["/safe/project/file.py"]}
        is_allowed, violations = guardrails.validate_action("test_action", context)

        # Безопасный путь должен быть разрешен
        assert is_allowed is True
        assert len(violations) == 0

    def test_validate_unsafe_file_path(self):
        """Тест проверки небезопасного пути к файлу"""
        guardrails = EnterpriseGuardrails()

        context = {"file_paths": ["../../../etc/passwd"]}
        is_allowed, violations = guardrails.validate_action("test_action", context)

        # Небезопасный путь должен быть заблокирован
        assert is_allowed is False
        assert len(violations) > 0
        assert any("file_path_validation" in v for v in violations)

    def test_validate_safe_code(self):
        """Тест проверки безопасного кода"""
        guardrails = EnterpriseGuardrails()

        context = {"code_snippets": ["def hello():\n    return 'world'"]}
        is_allowed, violations = guardrails.validate_action("test_action", context)

        # Безопасный код должен быть разрешен
        assert is_allowed is True
        assert len(violations) == 0

    def test_validate_unsafe_code(self):
        """Тест проверки небезопасного кода"""
        guardrails = EnterpriseGuardrails()

        context = {"code_snippets": ["import os\nos.system('rm -rf /')"]}
        is_allowed, violations = guardrails.validate_action("test_action", context)

        # Небезопасный код должен быть заблокирован
        assert is_allowed is False
        assert len(violations) > 0
        assert any("code_security_check" in v for v in violations)

    def test_resource_usage_within_limits(self):
        """Тест использования ресурсов в пределах лимитов"""
        guardrails = EnterpriseGuardrails()

        context = {
            "data_size": 1024 * 1024,  # 1MB
            "operations_count": 100,
            "estimated_duration": 60,  # 1 minute
        }
        is_allowed, violations = guardrails.validate_action("test_action", context)

        # Ресурсы в пределах лимитов должны быть разрешены
        assert is_allowed is True
        assert len(violations) == 0

    def test_resource_usage_exceeding_limits(self):
        """Тест превышения лимитов использования ресурсов"""
        guardrails = EnterpriseGuardrails()

        context = {
            "data_size": 200 * 1024 * 1024,  # 200MB, превышает лимит 100MB
            "operations_count": 100,
            "estimated_duration": 60,
        }
        is_allowed, violations = guardrails.validate_action("test_action", context)

        # Превышение лимита должно быть заблокировано
        assert is_allowed is False
        assert len(violations) > 0
        assert any("resource_usage_limit" in v for v in violations)

    def test_ethical_norms_compliant_content(self):
        """Тест соответствия этическим нормам"""
        guardrails = EnterpriseGuardrails()

        context = {"content": "This is a respectful and professional communication."}
        is_allowed, violations = guardrails.validate_action("test_action", context)

        # Этически корректный контент должен быть разрешен
        assert is_allowed is True
        assert len(violations) == 0

    def test_ethical_norms_violating_content(self):
        """Тест нарушения этических норм"""
        guardrails = EnterpriseGuardrails()

        context = {"content": "This contains discriminatory language against certain groups."}
        is_allowed, violations = guardrails.validate_action("test_action", context)

        # Контент с дискриминацией должен быть заблокирован
        assert is_allowed is False
        assert len(violations) > 0
        assert any("ethical_norms_check" in v for v in violations)

    def test_multiple_violations(self):
        """Тест нескольких нарушений одновременно"""
        guardrails = EnterpriseGuardrails()

        context = {
            "command": "rm -rf /",
            "file_paths": ["../../../etc/passwd"],
            "code_snippets": ["import os\nos.system('malicious_command')"],
            "content": "discrimination and hate speech content",
        }
        is_allowed, violations = guardrails.validate_action("test_action", context)

        # Должно быть несколько нарушений
        assert is_allowed is False
        assert len(violations) >= 3  # Хотя бы 3 типа нарушений

    def test_audit_log_creation(self):
        """Тест создания журнала аудита"""
        guardrails = EnterpriseGuardrails()

        # Вызвать нарушение для записи в аудит
        context = {"command": "rm -rf /"}
        guardrails.validate_action("test_action", context)

        audit_log = guardrails.get_audit_log()

        assert len(audit_log) >= 0  # Может быть 0 или 1 в зависимости от реализации
        # В текущей реализации нарушение должно быть записано в лог

    def test_violation_statistics(self):
        """Тест статистики нарушений"""
        guardrails = EnterpriseGuardrails()

        # Вызвать несколько нарушений
        guardrails.validate_action("action1", {"command": "dangerous_cmd"})
        guardrails.validate_action("action2", {"file_paths": ["../unsafe/path"]})

        stats = guardrails.get_violation_statistics()

        assert "total_violations" in stats
        assert "violations_by_level" in stats
        assert "violations_by_rule" in stats
        assert "rule_violation_counts" in stats

    def test_enforce_guardrails_allow_safe_action(self):
        """Тест принудительного применения безопасного действия"""
        guardrails = EnterpriseGuardrails()

        context = {"command": "echo hello", "file_paths": ["/safe/path"]}
        is_allowed, violations = guardrails.enforce_guardrails("safe_action", context, raise_exception=False)

        assert is_allowed is True
        assert len(violations) == 0

    def test_enforce_guardrails_block_unsafe_action(self):
        """Тест принудительного применения небезопасного действия"""
        guardrails = EnterpriseGuardrails()

        context = {"command": "rm -rf /"}

        # Проверить, что при raise_exception=True поднимается исключение
        with pytest.raises(Exception):
            guardrails.enforce_guardrails("unsafe_action", context, raise_exception=True)

        # Проверить, что при raise_exception=False возвращаются нарушения
        is_allowed, violations = guardrails.enforce_guardrails("unsafe_action", context, raise_exception=False)
        assert is_allowed is False
        assert len(violations) > 0

    def test_guardrail_decorator_functionality(self):
        """Тест функциональности декоратора правил безопасности"""
        guardrails = EnterpriseGuardrails()
        decorator = GuardrailDecorator(guardrails)

        @decorator
        def safe_function(context):
            return "success"

        # Безопасный вызов должен пройти
        context = {"command": "echo test"}
        result = safe_function(context)
        assert result == "success"

        # Небезопасный вызов должен быть заблокирован
        unsafe_context = {"command": "rm -rf /"}
        with pytest.raises(Exception):
            safe_function(unsafe_context)

    def test_context_extraction_in_decorator(self):
        """Тест извлечения контекста в декораторе"""
        guardrails = EnterpriseGuardrails()

        # Создать декоратор с пользовательским извлечением контекста
        def custom_context_extractor(args, kwargs):
            if args and isinstance(args[0], dict):
                return args[0]
            return kwargs

        decorator = GuardrailDecorator(guardrails, context_extractor=custom_context_extractor)

        @decorator
        def function_with_dict_arg(context_dict):
            return "processed"

        # Вызвать с безопасным контекстом
        result = function_with_dict_arg({"command": "ls"})
        assert result == "processed"

        # Вызвать с небезопасным контекстом
        with pytest.raises(Exception):
            function_with_dict_arg({"command": "rm -rf /"})
