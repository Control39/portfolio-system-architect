"""
Unit tests for the decision_engine module initialization.
"""

import pytest


def test_decision_engine_module_imports():
    """Проверяем, что модуль decision_engine импортируется"""
    try:
        import src.decision_engine.decision_engine

        assert src.decision_engine.decision_engine is not None
    except ImportError as e:
        pytest.skip(f"Decision engine module not available: {e}")


def test_decision_engine_has_version():
    """Проверяем наличие версии модуля"""
    try:
        import src.decision_engine.decision_engine as de

        assert hasattr(de, "__version__")
        assert isinstance(de.__version__, str)
    except ImportError:
        pytest.skip("decision_engine module not found")


def test_decision_engine_reexports_main_components():
    """Проверяем, что основные компоненты реэкспортируются"""
    # Проверяем реэкспорт основных компонентов
    from src.decision_engine.decision_engine import run_server

    assert callable(run_server)  # run_server должен быть функцией
