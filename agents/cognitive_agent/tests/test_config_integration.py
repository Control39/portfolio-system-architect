"""
Тесты интеграции с AI Config Manager для Cognitive Agent
"""

import sys
from pathlib import Path

import pytest

# Добавляем корень проекта в PATH
REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


class TestCognitiveAgentConfigIntegration:
    """Тесты интеграции конфигурации Cognitive Agent"""

    def test_config_manager_available(self):
        """Проверка доступности AI Config Manager"""
        try:
            from src.ai.config import ConfigManager

            assert ConfigManager is not None
        except ImportError:
            pytest.skip("AI Config Manager не доступен")

    def test_config_integration_module(self):
        """Проверка импорта модуля интеграции"""
        from agents.cognitive_agent.src.config_integration import CognitiveAgentConfig

        assert CognitiveAgentConfig is not None

    def test_get_config_singleton(self):
        """Проверка singleton-паттерна для конфигурации"""
        from agents.cognitive_agent.src.config_integration import CognitiveAgentConfig, get_config

        config1 = get_config()
        config2 = get_config()

        assert isinstance(config1, CognitiveAgentConfig)
        assert isinstance(config2, CognitiveAgentConfig)
        assert config1 is config2  # singleton: один и тот же объект

    def test_get_config_returns_dict(self):
        """Проверка что get_config возвращает dict"""
        from agents.cognitive_agent.src.config_integration import get_config

        config = get_config()
        result = config.get_config()  # вызываем метод экземпляра

        assert isinstance(result, dict)
        # Проверяем, что возвращается хотя бы пустой словарь, если конфигурация недоступна
        # Вместо конкретных ключей проверим общую структуру

    def test_config_initialization(self):
        """Проверка инициализации конфига"""
        from agents.cognitive_agent.src.config_integration import get_config

        config = get_config()

        assert config is not None
        assert hasattr(config, "get_config")
        assert hasattr(config, "reload")
        assert hasattr(config, "is_available")

    def test_config_singleton_consistency(self):
        """Проверка согласованности singleton-конфигурации"""
        from agents.cognitive_agent.src.config_integration import get_config

        config1 = get_config()
        config2 = get_config()

        # Объекты должны быть одинаковыми
        assert config1 is config2

        # Метод get_config должен возвращать одинаковые типы данных
        data1 = config1.get_config()
        data2 = config2.get_config()
        assert type(data1) == type(data2)

    def test_is_available_method(self):
        """Проверка метода is_available"""
        from agents.cognitive_agent.src.config_integration import get_config

        config = get_config()
        result = config.is_available()

        # Метод должен возвращать boolean
        assert isinstance(result, bool)

    def test_reload_method_exists(self):
        """Проверка наличия метода reload"""
        from agents.cognitive_agent.src.config_integration import get_config

        config = get_config()

        # Метод должен существовать и быть вызываемым
        assert hasattr(config, "reload")
        assert callable(config.reload)
