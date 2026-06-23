"""
Тесты интеграции с AI Config Manager для Decision Engine
"""

import pytest
from pathlib import Path
import sys

# Добавляем корень проекта в PATH
REPO_ROOT = Path(__file__).parent.parent.parent.parent  # apps/decision_engine/tests -> repo root
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


class TestDecisionEngineConfigIntegration:
    """Тесты интеграции конфигурации Decision Engine"""

    def test_config_manager_available(self):
        """Проверка доступности AI Config Manager"""
        try:
            from apps.ai_config_manager.src.config_manager import ConfigManager

            assert ConfigManager is not None
        except ImportError:
            pytest.skip("AI Config Manager не доступен")

    def test_config_integration_module(self):
        """Проверка импорта модуля интеграции"""
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "config_integration",
            REPO_ROOT / "apps" / "decision_engine" / "src" / "config_integration.py",
        )
        config_integration = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config_integration)

        assert hasattr(config_integration, "DecisionEngineConfig")

    def test_get_config_singleton(self):
        """Проверка singleton паттерна"""
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "config_integration_test",
            REPO_ROOT / "apps" / "decision_engine" / "src" / "config_integration.py",
        )
        config_integration = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config_integration)

        config1 = config_integration.get_config()
        config2 = config_integration.get_config()

        assert config1 is config2, "get_config() должен возвращать один и тот же объект (singleton)"

    def test_get_config_returns_dict(self):
        """Проверка что config.get_config() возвращает dict"""
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "config_integration_test2",
            REPO_ROOT / "apps" / "decision_engine" / "src" / "config_integration.py",
        )
        config_integration = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config_integration)

        config = config_integration.get_config()
        result = config.get_config()

        assert isinstance(result, dict), "get_config() должен возвращать dict"

    def test_reload_config(self):
        """Проверка hot reload"""
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "config_integration_test3",
            REPO_ROOT / "apps" / "decision_engine" / "src" / "config_integration.py",
        )
        config_integration = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config_integration)

        # Не должно выбрасывать исключений
        config_integration.reload_config()

    def test_is_available_method(self):
        """Проверка метода is_available"""
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "config_integration_test4",
            REPO_ROOT / "apps" / "decision_engine" / "src" / "config_integration.py",
        )
        config_integration = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config_integration)

        config = config_integration.get_config()
        assert hasattr(config, "is_available"), "Объект должен иметь метод is_available"
        assert callable(config.is_available), "is_available должен быть методом"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
