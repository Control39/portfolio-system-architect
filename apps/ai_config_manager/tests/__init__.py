# test_init.py
from ai_config_manager import AgentConfig, AIConfig, ConfigManager


def test_imports_work():
    assert ConfigManager is not None
    assert AIConfig is not None
    assert AgentConfig is not None
