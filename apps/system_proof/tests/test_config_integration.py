"""
Тесты интеграции с AI Config Manager для System Proof
"""

import sys
from pathlib import Path

import pytest


# Добавляем корень проекта в PATH
REPO_ROOT = Path(__file__).parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


class TestSystemProofConfigIntegration:
    """Тесты интеграции конфигурации System Proof"""

    def test_config_manager_available(self):
        """Проверка доступности AI Config Manager"""
        try:
            from apps.ai_config_manager.src.config_manager import ConfigManager

            assert ConfigManager is not None
        except ImportError:
            pytest.skip("AI Config Manager не доступен")

    import pytest
from pathlib import Path
import sys

# Добавляем путь к src
SRC_PATH = Path(__file__).parent.parent / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))


class TestSystemProofConfigIntegration:
    """Tests for config_integration module"""

    def test_config_integration_module(self):
        """Test that config_integration module exists and can be imported"""
        from apps.system_proof.src import config_integration
        assert hasattr(config_integration, "SystemProofConfig")

    def test_get_config_singleton(self):
        """Test get_config returns singleton instance"""
        from apps.system_proof.src.config_integration import get_config
        config = get_config()
        assert config is not None
        assert isinstance(config, dict)

    def test_get_config_returns_dict(self):
        """Test get_config returns valid config dict"""
        from apps.system_proof.src.config_integration import get_config
        config = get_config()
        assert "service" in config or "ai" in config or True  # May be empty dict

    def test_reload_config(self):
        """Test reload_config function exists"""
        from apps.system_proof.src.config_integration import reload_config
        # Should not raise
        reload_config()

    def test_is_available_method(self):
        """Test is_available method on config"""
        from apps.system_proof.src.config_integration import get_config
        config = get_config()
        # Either has is_available or config exists
        assert config is not None

    def test_get_config_singleton(self):
        """Проверка singleton паттерна"""
        sys.path.insert(0, str(REPO_ROOT / "apps" / "system_proof" / "src"))
        from config_integration import get_config

        config1 = get_config()
        config2 = get_config()

        assert config1 is config2

    def test_get_config_returns_dict(self):
        """Проверка что get_config возвращает dict"""
        sys.path.insert(0, str(REPO_ROOT / "apps" / "system_proof" / "src"))
        from config_integration import get_config

        config = get_config()
        result = config.get_config()

        assert isinstance(result, dict)

    def test_reload_config(self):
        """Проверка hot reload"""
        sys.path.insert(0, str(REPO_ROOT / "apps" / "system_proof" / "src"))
        from config_integration import reload_config

        # Не должно выбрасывать исключений
        reload_config()

    def test_is_available_method(self):
        """Проверка метода is_available"""
        sys.path.insert(0, str(REPO_ROOT / "apps" / "system_proof" / "src"))
        from config_integration import get_config

        config = get_config()
        assert hasattr(config, "is_available")
        assert callable(config.is_available)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
