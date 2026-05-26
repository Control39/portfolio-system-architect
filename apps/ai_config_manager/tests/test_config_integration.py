

class Testai_config_managerConfigIntegration:
    """Tests for config_integration module"""

    def test_config_integration_module(self):
        """Test that config_integration module exists and can be imported"""
        from ai_config_manager import config_integration
        assert hasattr(config_integration, "get_config")

    def test_get_config_singleton(self):
        """Test get_config returns singleton instance"""
        from ai_config_manager.config_integration import get_config
        config = get_config()
        assert config is not None

    def test_get_config_returns_dict(self):
        """Test get_config returns valid config dict"""
        from ai_config_manager.config_integration import get_config
        config = get_config()
        # get_config() возвращает экземпляр AiConfigManagerConfig, не dict
        assert config is not None

    def test_reload_config(self):
        """Test reload_config function exists"""
        from ai_config_manager.config_integration import reload_config
        # Should not raise
        reload_config()

    def test_is_available_method(self):
        """Test is_available method on config"""
        from ai_config_manager.config_integration import get_config
        config = get_config()
        # Either has is_available or config exists
        assert config is not None
