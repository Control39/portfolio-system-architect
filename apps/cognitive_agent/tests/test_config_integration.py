"""
Тесты интеграции с AI Config Manager для Cognitive Agent
"""

import pytest
from pathlib import Path
import sys

# Добавляем корень проекта в PATH
REPO_ROOT = Path(__file__).parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


class TestCognitiveAgentConfigIntegration:
    """Тесты интеграции конфигурации Cognitive Agent"""

    def test_config_manager_available(self):
        """Проверка доступности AI Config Manager"""
        try:
            from apps.ai_config_manager.src.config_manager import ConfigManager

            assert ConfigManager is not None
        except ImportError:
            pytest.skip("AI Config Manager не доступен")

    def test_config_integration_module(self):
        """Проверка импорта модуля интеграции"""
        sys.path.insert(0, str(REPO_ROOT / "apps" / "cognitive_agent" / "src"))
        from config_integration import CognitiveAgentConfig

        assert CognitiveAgentConfig is not None

    def test_get_config_singleton(self):
        """Проверка singleton паттерна"""
        sys.path.insert(0, str(REPO_ROOT / "apps" / "cognitive_agent" / "src"))
        from config_integration import get_config

        config1 = get_config()
        config2 = get_config()

        assert config1 is config2

    def test_get_config_returns_dict(self):
        """Проверка что get_config возвращает dict"""
        sys.path.insert(0, str(REPO_ROOT / "apps" / "cognitive_agent" / "src"))
        from config_integration import get_config

        config = get_config()
        result = config.get_config()

        assert isinstance(result, dict)

    def test_reload_config(self):
        """Проверка hot reload"""
        sys.path.insert(0, str(REPO_ROOT / "apps" / "cognitive_agent" / "src"))
        from config_integration import reload_config

        # Не должно выбрасывать исключений
        reload_config()

    def test_is_available_method(self):
        """Проверка метода is_available"""
        sys.path.insert(0, str(REPO_ROOT / "apps" / "cognitive_agent" / "src"))
        from config_integration import get_config

        config = get_config()
        assert hasattr(config, "is_available")
        assert callable(config.is_available)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
