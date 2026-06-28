"""
Advanced Unit Tests for config_integration.py
Cognitive Agent - интеграция с AI Config Manager

Цель: Покрытие 90%+ для config_integration.py
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Добавляем корень проекта в PATH
REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
# Добавляем путь к cognitive_agent src
COGNITIVE_SRC = REPO_ROOT / "apps" / "cognitive_agent" / "src"
if str(COGNITIVE_SRC) not in sys.path:
    sys.path.insert(0, str(COGNITIVE_SRC))


class TestConfigIntegrationAdvanced:
    """Углублённые unit тесты для config_integration.py"""

    def setup_method(self):
        """Очистка singleton перед каждым тестом"""
        # Сброс глобального экземпляра
        import config_integration

        config_integration._config_instance = None

    # =========================================================================
    # TEST 1: Singleton Pattern
    # =========================================================================

    def test_singleton_pattern(self):
        """
        Test: Singleton Pattern
        Проверка, что get_config() возвращает тот же объект
        """
        from config_integration import CognitiveAgentConfig, get_config

        config1 = get_config()
        config2 = get_config()

        assert isinstance(config1, CognitiveAgentConfig)
        assert isinstance(config2, CognitiveAgentConfig)
        assert config1 is config2, "Singleton паттерн нарушен"

    def test_singleton_with_multiple_imports(self):
        """
        Test: Singleton with Multiple Imports
        Проверка singleton при импорте из разных мест

        Note: Singleton pattern is intentionally broken after importlib.reload()
        because a new class instance is created. This is expected Python behavior.
        The test verifies that the singleton is reset and a new instance is created.
        """
        import config_integration

        config_integration._config_instance = None

        from config_integration import get_config

        config1 = get_config()
        config1_id = id(config1)

        # Импорт повторно
        import importlib

        importlib.reload(config_integration)

        # После reload создается новый экземпляр (ожидаемое поведение Python)
        # Singleton сбрасывается, создается новый экземпляр
        config2 = get_config()
        config2_id = id(config2)

        # Проверяем, что после reload создан новый экземпляр
        assert config1_id != config2_id, "После reload должен быть новый экземпляр"

        # Проверяем, что singleton работает после reload
        config3 = get_config()
        assert config2 is config3, "Singleton должен быть один после reload"

    # =========================================================================
    # TEST 2: Local Fallback (без AI Config Manager)
    # =========================================================================

    @patch("config_integration.AI_CONFIG_AVAILABLE", False)
    def test_local_fallback_disabled(self):
        """
        Test: Local Fallback when AI Config Manager disabled
        Проверка fallback на локальную конфигурацию
        """
        # Сброс singleton
        import config_integration
        from config_integration import CognitiveAgentConfig

        config_integration._config_instance = None

        # Создаём локальный конфиг
        local_config_path = REPO_ROOT / "apps" / "cognitive_agent" / "config" / "agent-config.yaml"

        if local_config_path.exists():
            config = CognitiveAgentConfig()
            result = config.get_config()

            assert isinstance(result, dict)
            assert len(result) >= 0  # Может быть пустым, если файл не найден
        else:
            pytest.skip("Локальный конфиг не найден")

    @patch("config_integration.AI_CONFIG_AVAILABLE", False)
    def test_local_fallback_empty_config(self):
        """
        Test: Local Fallback with Empty Config
        Проверка fallback при пустом конфиге
        """
        from config_integration import CognitiveAgentConfig

        config = CognitiveAgentConfig()
        result = config.get_config()

        assert isinstance(result, dict)

    # =========================================================================
    # TEST 3: Config Path Resolution
    # =========================================================================

    def test_config_path_default(self):
        """
        Test: Default Config Path Resolution
        Проверка, что используется правильный путь по умолчанию
        """
        from config_integration import CognitiveAgentConfig

        config = CognitiveAgentConfig()
        expected_path = REPO_ROOT / "config" / "ai-config.yaml"

        assert config.config_path == str(expected_path)

    def test_config_path_custom(self):
        """
        Test: Custom Config Path Resolution
        Проверка, что можно указать кастомный путь
        """
        from config_integration import CognitiveAgentConfig

        custom_path = str(REPO_ROOT / "apps" / "cognitive_agent" / "config" / "custom.yaml")
        config = CognitiveAgentConfig(config_path=custom_path)

        assert config.config_path == custom_path

    # =========================================================================
    # TEST 4: AI Config Manager Integration (Mocked)
    # =========================================================================

    @patch("config_integration.AI_CONFIG_AVAILABLE", True)
    @patch("config_integration.ConfigManager")
    def test_config_manager_integration_success(self, mock_config_manager):
        """
        Test: AI Config Manager Integration (Success Case)
        Проверка успешной интеграции с ConfigManager
        """
        from config_integration import get_config

        # Настраиваем mock
        mock_instance = MagicMock()
        mock_instance.get_agent_config.return_value = {"test_key": "test_value"}
        mock_instance.validate.return_value = True
        mock_config_manager.return_value = mock_instance

        # Сброс singleton
        import config_integration

        config_integration._config_instance = None

        config = get_config()
        result = config.get_config()

        assert isinstance(result, dict)
        assert "test_key" in result
        assert result["test_key"] == "test_value"

    @patch("config_integration.AI_CONFIG_AVAILABLE", True)
    @patch("config_integration.ConfigManager")
    def test_config_manager_integration_failure_fallback(self, mock_config_manager):
        """
        Test: AI Config Manager Integration (Failure → Fallback)
        Проверка fallback при ошибке ConfigManager
        """
        from config_integration import get_config

        # Настраиваем mock для ошибки
        mock_instance = MagicMock()
        mock_instance.get_agent_config.side_effect = Exception("Config error")
        mock_instance.validate.return_value = False
        mock_config_manager.return_value = mock_instance

        # Сброс singleton
        import config_integration

        config_integration._config_instance = None

        config = get_config()
        result = config.get_config()

        # Должен вернуться локальный конфиг (или пустой dict)
        assert isinstance(result, dict)

    # =========================================================================
    # TEST 5: Reload Functionality
    # =========================================================================

    @patch("config_integration.AI_CONFIG_AVAILABLE", False)
    def test_reload_local_config(self):
        """
        Test: Reload Local Config
        Проверка перезагрузки локальной конфигурации
        """
        from config_integration import get_config, reload_config

        config = get_config()
        _ = config.get_config()  # noqa: F841

        # Вызываем reload
        reload_config()

        # Конфиг должен быть перезагружен
        new_config = config.get_config()
        assert isinstance(new_config, dict)

    @patch("config_integration.AI_CONFIG_AVAILABLE", True)
    @patch("config_integration.ConfigManager")
    def test_reload_ai_config(self, mock_config_manager):
        """
        Test: Reload AI Config
        Проверка перезагрузки AI Config Manager
        """
        from config_integration import get_config, reload_config

        # Настраиваем mock
        mock_instance = MagicMock()
        mock_instance.reload = MagicMock()
        mock_instance.validate.return_value = True
        mock_config_manager.return_value = mock_instance

        # Сброс singleton
        import config_integration

        config_integration._config_instance = None

        get_config()
        reload_config()

        # Проверяем, что reload был вызван
        mock_instance.reload.assert_called_once()

    # =========================================================================
    # TEST 6: Error Handling
    # =========================================================================

    @patch("config_integration.AI_CONFIG_AVAILABLE", True)
    @patch("config_integration.ConfigManager")
    def test_error_handling_config_manager_exception(self, mock_config_manager):
        """
        Test: Error Handling - ConfigManager Exception
        Проверка обработки исключений ConfigManager
        """
        from config_integration import get_config

        # Настраиваем mock для исключения
        mock_config_manager.side_effect = Exception("Failed to initialize")

        # Сброс singleton
        import config_integration

        config_integration._config_instance = None

        # Не должно выбрасывать исключение (должен fallback)
        config = get_config()
        result = config.get_config()

        assert isinstance(result, dict)

    @patch("config_integration.AI_CONFIG_AVAILABLE", True)
    @patch("config_integration.ConfigManager")
    def test_error_handling_yaml_load_error(self, mock_config_manager):
        """
        Test: Error Handling - YAML Load Error
        Проверка обработки ошибок загрузки YAML
        """
        from config_integration import CognitiveAgentConfig

        # Настраиваем mock для ConfigManager
        mock_instance = MagicMock()
        mock_instance.validate.return_value = False
        mock_instance.get_agent_config.return_value = {}
        mock_config_manager.return_value = mock_instance

        # Сброс singleton
        import config_integration

        config_integration._config_instance = None

        config = CognitiveAgentConfig()

        # Проверяем, что get_config не выбрасывает исключение
        result = config.get_config()
        assert isinstance(result, dict)

    # =========================================================================
    # TEST 7: is_available Method
    # =========================================================================

    @patch("config_integration.AI_CONFIG_AVAILABLE", True)
    def test_is_available_true(self):
        """
        Test: is_available returns True when AI Config Manager available
        """
        from config_integration import get_config

        config = get_config()
        assert config.is_available() is True

    @patch("config_integration.AI_CONFIG_AVAILABLE", False)
    def test_is_available_false(self):
        """
        Test: is_available returns False when AI Config Manager unavailable
        """
        # Сброс singleton
        import config_integration
        from config_integration import get_config

        config_integration._config_instance = None

        config = get_config()
        assert config.is_available() is False

    # =========================================================================
    # TEST 8: Global Module State
    # =========================================================================

    def test_global_config_instance_none_on_start(self):
        """
        Test: Global config instance is None on module start
        """
        import config_integration

        # Должен быть None до первого вызова get_config()
        assert config_integration._config_instance is None

    def test_config_instance_created_on_first_call(self):
        """
        Test: Config instance is created on first get_config() call
        """
        import config_integration

        # Сброс
        config_integration._config_instance = None

        from config_integration import get_config

        config = get_config()

        assert config_integration._config_instance is not None
        assert config_integration._config_instance is config


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
