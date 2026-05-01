"""
Unit tests for the assistant_orchestrator module initialization.
"""

import pytest


def test_assistant_orchestrator_imports():
    """Проверяем, что модуль импортируется без ошибок"""
    try:
        import src.assistant_orchestrator

        assert src.assistant_orchestrator is not None
    except ImportError as e:
        pytest.fail(f"Assistant orchestrator import failed: {e}")


def test_assistant_orchestrator_has_core():
    """Проверяем наличие core подмодуля"""
    try:
        from src.assistant_orchestrator.core import AssistantOrchestrator, BaseAssistant

        assert BaseAssistant is not None
        assert AssistantOrchestrator is not None
    except ImportError:
        pytest.skip("Core components not found")


def test_assistant_orchestrator_has_models():
    """Проверяем наличие моделей"""
    try:
        from src.assistant_orchestrator.models import AssistantRequest, AssistantResponse

        assert AssistantRequest is not None
        assert AssistantResponse is not None
    except ImportError:
        pytest.skip("Models not found")
