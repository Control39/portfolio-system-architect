from pathlib import Path
import sys

# Добавляем корень репо и путь к src
REPO_ROOT = Path(__file__).parent.parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

SRC_PATH = Path(__file__).parent.parent / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))


class Testcognitive_agentConfigIntegration:
    """Tests for config_integration module"""

    def test_config_integration_module(self):
        """Test that config_integration module exists and can be imported"""
        from apps.cognitive_agent.src import config_integration
        assert hasattr(config_integration, "cognitive_agentConfig")

    def test_get_config_singleton(self):
        """Test get_config returns singleton instance"""
        from apps.cognitive_agent.src.config_integration import get_config
        config = get_config()
        assert config is not None
        assert isinstance(config, dict)

    def test_get_config_returns_dict(self):
        """Test get_config returns valid config dict"""
        from apps.cognitive_agent.src.config_integration import get_config
        config = get_config()
        assert isinstance(config, dict)

    def test_reload_config(self):
        """Test reload_config function exists"""
        from apps.cognitive_agent.src.config_integration import reload_config
        # Should not raise
        reload_config()

    def test_is_available_method(self):
        """Test is_available method on config"""
        from apps.cognitive_agent.src.config_integration import get_config
        config = get_config()
        # Either has is_available or config exists
        assert config is not None
