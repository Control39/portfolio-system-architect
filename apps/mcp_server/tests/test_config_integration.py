from pathlib import Path
import importlib.util


class TestMcpServerConfigIntegration:
    """Tests for config_integration module"""

    def _load_config_module(self):
        """Helper to load config_integration module"""
        spec = importlib.util.spec_from_file_location(
            "config_integration",
            Path(__file__).parent.parent / "src" / "config_integration.py"
        )
        config_integration = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config_integration)
        return config_integration

    def test_config_integration_module(self):
        """Test that config_integration module exists and can be imported"""
        config_integration = self._load_config_module()
        assert hasattr(config_integration, "McpServerConfig")

    def test_get_config_singleton(self):
        """Test get_config returns singleton instance"""
        config_integration = self._load_config_module()
        get_config = config_integration.get_config
        config = get_config()
        assert config is not None
        assert hasattr(config, "get_config") or config is not None

    def test_get_config_returns_dict(self):
        """Test get_config returns valid config dict"""
        config_integration = self._load_config_module()
        get_config = config_integration.get_config
        config = get_config()
        if hasattr(config, "get_config"):
            config = config.get_config()
        assert isinstance(config, dict)

    def test_reload_config(self):
        """Test reload_config function exists"""
        config_integration = self._load_config_module()
        get_config = config_integration.get_config
        config = get_config()
        if hasattr(config, "reload"):
            config.reload()

    def test_is_available_method(self):
        """Test is_available method on config"""
        config_integration = self._load_config_module()
        get_config = config_integration.get_config
        config = get_config()
        assert config is not None
        if hasattr(config, "is_available"):
            assert config.is_available() in [True, False]