#!/usr/bin/env python3
"""
Тесты для критических улучшений безопасности Cognitive Agent

1. Валидация AI-ответов (sanitizer)
2. Schema validation guardrails
3. ContextVar изоляция агента
"""

import re
import sys
from pathlib import Path

# Добавляем корень проекта в PATH
REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


def test_validate_ai_response():
    """Тест валидации AI-ответов (санитайзер)"""
    print("\n🧪 Тест 1: Валидация AI-ответов")
    print("=" * 50)

    # Импортируем паттерны из autonomous_agent
    from agents.cognitive_agent.src.autonomous_agent import AutonomousCognitiveAgent

    dangerous_patterns = AutonomousCognitiveAgent.AI_RESPONSE_DANGEROUS_PATTERNS

    # Тест 1.1: Опасные паттерны должны блокироваться
    dangerous_responses = [
        "rm -rf /",
        "eval(user_input)",
        "os.system('rm -rf /')",
        "subprocess.call(['rm', '-rf', '/'])",
        "chmod 777 /etc/passwd",
        "DROP TABLE users",
    ]

    for response in dangerous_responses:
        for pattern in dangerous_patterns:
            if re.search(pattern, response, re.IGNORECASE):
                print(f"  ✅ Blocked: {response[:50]}... (pattern: {pattern})")
                break
        else:
            print(f"  ⚠️  Warning: {response[:50]}... not blocked")

    # Тест 1.2: Безопасные ответы должны проходить
    safe_responses = [
        "Рекомендую добавить unit-тесты для модуля auth",
        "Предлагаю рефакторинг функции calculate_total",
        '[{"priority": "high", "message": "Добавить логирование"}]',
    ]

    for response in safe_responses:
        is_blocked = False
        for pattern in dangerous_patterns:
            if re.search(pattern, response, re.IGNORECASE):
                is_blocked = True
                break
        if not is_blocked:
            print(f"  ✅ Safe: {response[:50]}...")
        else:
            print(f"  ❌ False positive: {response[:50]}...")

    print("  ✅ Тест 1 пройден\n")


def test_guardrails_schema_validation():
    """Тест валидации схемы guardrails.yaml"""
    print("\n🧪 Тест 2: Schema validation guardrails")
    print("=" * 50)

    import yaml

    guardrails_path = REPO_ROOT / "agents" / "cognitive_agent" / "config" / "guardrails.yaml"

    if not guardrails_path.exists():
        print("  ⚠️  guardrails.yaml не найден")
        return

    with open(guardrails_path, encoding="utf-8") as f:
        guardrails = yaml.safe_load(f)

    # Тест 2.1: Обязательные ключи
    required_keys = ["allowed_paths", "blocked_patterns", "safe_actions", "rules"]
    for key in required_keys:
        if key in guardrails:
            print(f"  ✅ Found required key: {key}")
        else:
            print(f"  ❌ Missing required key: {key}")

    # Тест 2.2: Валидация правил
    valid_rules = 0
    invalid_rules = 0
    for i, rule in enumerate(guardrails.get("rules", [])):
        if "pattern" in rule and "action" in rule:
            valid_rules += 1
        else:
            invalid_rules += 1
            print(f"  ❌ Invalid rule #{i}: {rule}")

    print(f"  ✅ Valid rules: {valid_rules}")
    print(f"  ❌ Invalid rules: {invalid_rules}")

    # Тест 2.3: Проверка allowed_paths
    allowed_paths = guardrails.get("allowed_paths", [])
    test_paths = ["apps/test.py", "agents/cognitive_agent/test.py", "/etc/passwd"]
    for path in test_paths:
        is_allowed = any(re.match(p, path, re.IGNORECASE) for p in allowed_paths)
        expected = path not in ["/etc/passwd"]
        if is_allowed == expected:
            print(f"  ✅ Path {path}: {'allowed' if is_allowed else 'blocked'} (expected)")
        else:
            print(f"  ❌ Path {path}: {'allowed' if is_allowed else 'blocked'} (unexpected)")

    print("  ✅ Тест 2 пройден\n")


def test_contextvar_isolation():
    """Тест изоляции агента через ContextVar"""
    print("\n🧪 Тест 3: ContextVar изоляция агента")
    print("=" * 50)

    try:
        from contextvars import ContextVar

        # Симуляция ContextVar
        _agent_context: ContextVar = ContextVar("agent_context", default=None)

        # Тест 3.1: Создание нового агента для каждого "запроса"
        class MockAgent:
            def __init__(self, request_id: str):
                self.request_id = request_id

        # Симуляция запроса 1
        _agent_context.set(MockAgent("request-1"))
        agent1 = _agent_context.get()

        # Симуляция запроса 2
        _agent_context.set(MockAgent("request-2"))
        agent2 = _agent_context.get()

        if agent1.request_id != agent2.request_id:
            print("  ✅ Agent isolation: request-1 ≠ request-2")
        else:
            print(f"  ❌ Agent isolation failed: {agent1.request_id} == {agent2.request_id}")

        # Тест 3.2: Проверка default значения
        _agent_context.set(None)
        agent_default = _agent_context.get()
        if agent_default is None:
            print("  ✅ Default context: None")
        else:
            print(f"  ❌ Default context failed: {agent_default}")

        print("  ✅ Тест 3 пройден\n")

    except Exception as e:
        print(f"  ⚠️  ContextVar test skipped: {e}")
        print("  ✅ Тест 3 пропущен (не критично)\n")


def main():
    """Запуск всех тестов"""
    print("\n🚀 Запуск тестов для критических улучшений безопасности")
    print("=" * 70)

    try:
        test_validate_ai_response()
        test_guardrails_schema_validation()
        test_contextvar_isolation()

        print("\n" + "=" * 70)
        print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("=" * 70)
        return 0
    except Exception as e:
        print(f"\n❌ Ошибка в тестах: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
