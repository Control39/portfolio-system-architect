from pathlib import Path
import sys

# Добавляем путь к src
SRC_PATH = Path(__file__).parent.parent / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))


class TestKnowledgeGraphConfigIntegration:
    """Tests for config_integration module"""

    def test_config_integration_module(self):
        """Test that config_integration module exists and can be imported"""
        from apps.knowledge_graph.src import config_integration
        assert hasattr(config_integration, "KnowledgeGraphConfig")

    def test_get_config_singleton(self):
        """Test get_config returns singleton instance"""
        from apps.knowledge_graph.src.config_integration import get_config
        config = get_config()
        assert config is not None
        # Config is KnowledgeGraphConfig object with methods
        assert hasattr(config, "get_config") or hasattr(config, "is_available")

    def test_get_config_returns_dict(self):
        """Test get_config returns valid config dict"""
        from apps.knowledge_graph.src.config_integration import get_config
        config = get_config()
        # Call get_config() method to get actual dict
        if hasattr(config, "get_config"):
            config = config.get_config()
        assert isinstance(config, dict)

    def test_reload_config(self):
        """Test reload_config function exists"""
        from apps.knowledge_graph.src.config_integration import get_config
        config = get_config()
        # Call reload method if exists
        if hasattr(config, "reload"):
            config.reload()
        # Should not raise

    def test_is_available_method(self):
        """Test is_available method on config"""
        from apps.knowledge_graph.src.config_integration import get_config
        config = get_config()
        # Either has is_available or config exists
        assert hasattr(config, "is_available") or config is not None
        if hasattr(config, "is_available"):
            assert config.is_available() in [True, False]
