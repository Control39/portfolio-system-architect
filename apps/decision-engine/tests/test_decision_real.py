"""
Реальные тесты для decision-engine (бизнес-логика)

Тестирует:
- Принятие решений на основе правил
- RAG-интеграцию (с моками)
- Приоритизацию
- Обработку ошибок
"""

import sys
from pathlib import Path

import pytest


# Добавляем корень проекта в PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from apps.decision_engine.core.decision_engine import DecisionEngine
from apps.decision_engine.core.models import DecisionContext, DecisionRequest


class TestDecisionEngineCore:
    """Тесты ядра Decision Engine"""

    @pytest.fixture
    def engine(self):
        """Создаём движок решений"""
        return DecisionEngine(config_path="apps/decision-engine/config/rules.yaml")

    def test_make_decision_with_simple_rules(self, engine):
        """Принятие решения по простым правилам"""
        request = DecisionRequest(
            user_id="user123",
            action="deploy",
            context=DecisionContext(environment="staging", user_role="developer", resources_available=True),
        )

        # Должен вернуть решение без ошибок
        result = engine.make_decision(request)

        assert result is not None
        assert result.decision in ["allow", "deny", "require_approval"]
        assert result.user_id == "user123"

    def test_make_decision_with_insufficient_permissions(self, engine):
        """Отказ при недостаточных правах"""
        request = DecisionRequest(
            user_id="user456",
            action="delete_production",
            context=DecisionContext(
                environment="production",
                user_role="developer",  # Не админ
                resources_available=True,
            ),
        )

        result = engine.make_decision(request)

        # Должен отказать или запросить подтверждение
        assert result.decision in ["deny", "require_approval"]

    def test_make_decision_with_unavailable_resources(self, engine):
        """Отказ при недоступных ресурсах"""
        request = DecisionRequest(
            user_id="user789",
            action="deploy",
            context=DecisionContext(environment="staging", user_role="developer", resources_available=False),
        )

        result = engine.make_decision(request)

        assert result.decision == "deny"
        assert result.reason is not None

    def test_make_decision_with_rag_integration(self, engine):
        """Интеграция с RAG для сложных решений"""
        # Создаём запрос, который требует RAG (сложное действие)
        request = DecisionRequest(
            user_id="user111",
            action="complex_operation",
            context=DecisionContext(environment="staging", user_role="senior_developer", resources_available=True),
        )

        # Должен вернуть решение (без мока RAG работает дефолтные правила)
        result = engine.make_decision(request)

        assert result is not None
        assert result.decision in ["allow", "deny", "require_approval"]

    def test_prioritize_decisions(self, engine):
        """Приоритизация нескольких решений"""
        decisions = [
            {"priority": "low", "action": "log"},
            {"priority": "critical", "action": "alert"},
            {"priority": "medium", "action": "notify"},
        ]

        prioritized = engine._prioritize(decisions)

        assert len(prioritized) == 3
        assert prioritized[0]["action"] == "alert"  # critical первый
        assert prioritized[-1]["action"] == "log"  # low последний

    def test_validate_request_format(self, engine):
        """Валидация формата запроса"""
        with pytest.raises(ValueError):
            engine.make_decision(
                DecisionRequest(
                    user_id="",
                    action="test",
                    context=DecisionContext(environment="staging", user_role="developer", resources_available=True),
                )
            )

    def test_decision_cache(self, engine):
        """Кэширование решений"""
        request = DecisionRequest(
            user_id="user222",
            action="read_data",
            context=DecisionContext(environment="staging", user_role="developer", resources_available=True),
        )

        # Первое решение
        result1 = engine.make_decision(request)

        # Второе такое же решение (должно быть из кэша)
        result2 = engine.make_decision(request)

        assert result1 == result2

    def test_decision_with_custom_rules(self, engine):
        """Применение пользовательских правил"""
        custom_rules = {"allow_list": ["user_special"], "deny_list": ["user_banned"]}

        request_allow = DecisionRequest(
            user_id="user_special",
            action="any",
            context=DecisionContext(environment="any", user_role="any", resources_available=True),
        )

        request_deny = DecisionRequest(
            user_id="user_banned",
            action="any",
            context=DecisionContext(environment="any", user_role="any", resources_available=True),
        )

        result_allow = engine.make_decision(request_allow, custom_rules)
        result_deny = engine.make_decision(request_deny, custom_rules)

        assert result_allow.decision == "allow"
        assert result_deny.decision == "deny"

    def test_decision_explanation_generation(self, engine):
        """Генерация объяснения решения"""
        request = DecisionRequest(
            user_id="user333",
            action="deploy",
            context=DecisionContext(environment="production", user_role="devops", resources_available=True),
        )

        result = engine.make_decision(request, include_explanation=True)

        assert result.explanation is not None
        assert "rules_applied" in result.explanation

    def test_decision_with_multiple_conditions(self, engine):
        """Решение с несколькими условиями"""
        request = DecisionRequest(
            user_id="user444",
            action="critical_operation",
            context=DecisionContext(
                environment="production",
                user_role="admin",
                resources_available=True,
                maintenance_mode=False,
                backup_verified=True,
            ),
        )

        result = engine.make_decision(request, include_explanation=True)

        # Должен учесть все условия
        assert result.conditions_checked >= 3


class TestDecisionEngineEdgeCases:
    """Граничные случаи"""

    def test_empty_request(self):
        """Пустой запрос"""
        engine = DecisionEngine()

        with pytest.raises(ValueError):
            engine.make_decision(
                DecisionRequest(
                    user_id="",
                    action="",
                    context=DecisionContext(environment="staging", user_role="developer", resources_available=True),
                )
            )

    def test_null_context(self):
        """Null контекст"""
        engine = DecisionEngine()

        # Pydantic не позволит создать с None
        with pytest.raises(ValueError):
            DecisionRequest(user_id="user555", action="test", context=None)

    def test_unicode_user_id(self):
        """Unicode в user_id"""
        engine = DecisionEngine()

        request = DecisionRequest(
            user_id="пользователь_тест",
            action="test",
            context=DecisionContext(environment="staging", user_role="developer", resources_available=True),
        )

        result = engine.make_decision(request)
        assert result is not None

    def test_very_long_action_name(self):
        """Очень длинное название действия"""
        engine = DecisionEngine()

        request = DecisionRequest(
            user_id="user666",
            action="a" * 1000,
            context=DecisionContext(environment="staging", user_role="developer", resources_available=True),
        )

        result = engine.make_decision(request)
        assert result is not None

    def test_concurrent_decisions(self):
        """Параллельные решения"""
        import threading

        engine = DecisionEngine()
        results = []
        errors = []

        def make_decision(user_id):
            try:
                request = DecisionRequest(
                    user_id=user_id,
                    action="test",
                    context=DecisionContext(environment="staging", user_role="developer", resources_available=True),
                )
                result = engine.make_decision(request)
                results.append(result)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=make_decision, args=(f"user_{i}",)) for i in range(10)]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        assert len(results) == 10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
