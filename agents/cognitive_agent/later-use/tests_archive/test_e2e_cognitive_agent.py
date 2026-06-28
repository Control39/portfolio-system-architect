#!/usr/bin/env python3
"""
E2E-тесты для Cognitive Agent

Тестируют полный жизненный цикл агента:
- Инициализация
- Сканирование проекта
- Генерация плана
- Остановка
"""

import sys
from pathlib import Path

# Добавляем корень проекта в PATH
REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

import pytest

from agents.cognitive_agent.src.autonomous_agent import AutonomousCognitiveAgent


class TestAgentLifecycle:
    """Тесты жизненного цикла агента"""

    def test_initialization(self):
        """Проверка инициализации агента"""
        agent = AutonomousCognitiveAgent()
        assert agent is not None
        assert agent.agent_id is not None
        assert agent.running is False
        assert agent.project_path == REPO_ROOT
        print(f"✅ Agent initialized: {agent.agent_id}")

    def test_start_stop(self):
        """Тест запуска и остановки агента"""
        agent = AutonomousCognitiveAgent()
        assert agent.status == "initialized"

        # Запуск
        agent.start(background=False)
        assert agent.running is True
        print("✅ Agent started")

        # Остановка
        agent.stop()
        assert agent.running is False
        print("✅ Agent stopped")

    def test_scan_project(self):
        """Тест сканирования проекта"""
        agent = AutonomousCognitiveAgent()
        result = agent.scan_project("auto")

        assert result is not None
        assert "status" in result
        assert "timestamp" in result
        print(f"✅ Scan completed: {len(result.get('recommendations', []))} recommendations")

    def test_create_plan(self):
        """Тест создания плана задачи"""
        agent = AutonomousCognitiveAgent()
        plan = agent.create_plan("Test task")

        assert "tasks" in plan
        assert len(plan["tasks"]) > 0
        print(f"✅ Plan created: {len(plan['tasks'])} tasks")

    def test_guardrails_block_dangerous_pattern(self):
        """Проверка блокировки опасных паттернов"""
        agent = AutonomousCognitiveAgent()

        # Проверка безопасных путей
        assert agent._is_safe_path("./apps/example.py") is True
        assert agent._is_safe_path("./agents/cognitive_agent/test.py") is True

        # Проверка опасных путей
        assert agent._is_safe_path("/etc/passwd") is False
        assert agent._is_safe_path("../../../etc/shadow") is False
        print("✅ Guardrails working correctly")

    @pytest.mark.skip(reason="Pending E2E implementation")
    def test_full_lifecycle(self):
        """Полный цикл: запуск → сканирование → планирование → выполнение"""
        agent = AutonomousCognitiveAgent()
        agent.start()

        try:
            # Тест сканирования
            result = agent.scan_project("apps/example")
            assert result["status"] == "success"

            # Тест планирования
            plan = agent.create_plan("Fix bug in user auth")
            assert len(plan["tasks"]) > 0

        finally:
            agent.stop()
            assert agent.status == "stopped"


class TestAISafetyValidation:
    """Тесты валидации AI-ответов"""

    def test_dangerous_patterns_blocked(self):
        """Проверка блокировки опасных паттернов в AI-ответах"""
        agent = AutonomousCognitiveAgent()

        dangerous_responses = [
            "rm -rf /",
            "eval(user_input)",
            "os.system('rm -rf /')",
            "subprocess.call(['rm', '-rf', '/'])",
        ]

        for response in dangerous_responses:
            is_safe, _ = agent._validate_ai_response(response)
            assert is_safe is False, f"Should block: {response}"
            print(f"✅ Blocked dangerous response: {response}")

    def test_safe_responses_allowed(self):
        """Проверка, что безопасные ответы проходят"""
        agent = AutonomousCognitiveAgent()

        safe_responses = [
            "Рекомендую добавить unit-тесты для модуля auth",
            "Предлагаю рефакторинг функции calculate_total",
            '[{"priority": "high", "message": "Добавить логирование"}]',
        ]

        for response in safe_responses:
            is_safe, _ = agent._validate_ai_response(response)
            assert is_safe is True, f"Should allow: {response}"
            print(f"✅ Allowed safe response: {response}")


if __name__ == "__main__":
    # Запуск тестов
    pytest.main([__file__, "-v"])
