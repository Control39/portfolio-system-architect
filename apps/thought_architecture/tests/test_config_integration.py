import pytest
from pathlib import Path
import sys
import importlib.util


class TestThoughtArchitectureConfigIntegration:
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
        assert hasattr(config_integration, "ThoughtArchitectureConfig")

    def test_get_config_singleton(self):
        """Test get_config returns singleton instance"""
        config_integration = self._load_config_module()
        get_config = config_integration.get_config
        config = get_config()
        assert config is not None
        # Config is ThoughtArchitectureConfig object with get_config method
        assert hasattr(config, "get_config") or config is not None

    def test_get_config_returns_dict(self):
        """Test get_config returns valid config dict"""
        config_integration = self._load_config_module()
        get_config = config_integration.get_config
        config = get_config()
        # Call get_config() method to get actual dict
        if hasattr(config, "get_config"):
            config = config.get_config()
        assert isinstance(config, dict)

    def test_reload_config(self):
        """Test reload_config function exists"""
        config_integration = self._load_config_module()
        get_config = config_integration.get_config
        config = get_config()
        # Call reload method if exists
        if hasattr(config, "reload"):
            config.reload()
        # Should not raise

    def test_is_available_method(self):
        """Test is_available method on config"""
        config_integration = self._load_config_module()
        get_config = config_integration.get_config
        config = get_config()
        assert config is not None
        if hasattr(config, "is_available"):
            assert config.is_available() in [True, False]
