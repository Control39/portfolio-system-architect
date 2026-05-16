"""
Тесты для ConfigManager.
"""

import pytest
import yaml

from src.config_manager import ConfigManager


class TestConfigManager:
    """Тесты для ConfigManager."""

    @pytest.fixture
    def temp_config_file(self, tmp_path):
        """Создание временного файла конфигурации."""
        config_data = {
            "agents": {"test-agent": {"model": "gpt-4", "temperature": 0.7, "max_tokens": 1024}},
            "resources": {
                "test-resource": {"name": "test-resource", "type": "tool", "enabled": True, "config": {"key": "value"}}
            },
            "version": "1.0.0",
        }

        config_file = tmp_path / "config.yaml"
        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        return str(config_file)

    def test_load_valid_config(self, temp_config_file):
        """Загрузка валидной конфигурации."""
        config_manager = ConfigManager(temp_config_file, auto_reload=False)
        config = config_manager.get_config()

        assert config is not None
        assert "test-agent" in config.agents
        assert config.agents["test-agent"].model == "gpt-4"
        assert config.agents["test-agent"].temperature == 0.7
        assert len(config.resources) == 1

    def test_load_nonexistent_file(self):
        """Загрузка несуществующего файла."""
        with pytest.raises(FileNotFoundError):
            ConfigManager("/nonexistent/path/config.yaml", auto_reload=False)

    def test_get_agent_config(self, temp_config_file):
        """Получение конфигурации агента."""
        config_manager = ConfigManager(temp_config_file, auto_reload=False)
        agent_config = config_manager.get_agent_config("test-agent")

        assert agent_config.model == "gpt-4"
        assert agent_config.temperature == 0.7

    def test_get_agent_config_not_found(self, temp_config_file):
        """Получение несуществующего агента."""
        config_manager = ConfigManager(temp_config_file, auto_reload=False)
        with pytest.raises(KeyError, match="Агент не найден: nonexistent"):
            config_manager.get_agent_config("nonexistent")

    def test_get_resource_config(self, temp_config_file):
        """Получение конфигурации ресурса."""
        config_manager = ConfigManager(temp_config_file, auto_reload=False)
        resource_config = config_manager.get_resource_config("test-resource")

        assert resource_config.name == "test-resource"
        assert resource_config.enabled is True

    def test_hot_reload(self, temp_config_file):
        """Динамическая перезагрузка конфигурации."""
        config_manager = ConfigManager(temp_config_file, auto_reload=False)

        # Изменяем файл
        with open(temp_config_file) as f:
            data = yaml.safe_load(f)

        data["agents"]["test-agent"]["temperature"] = 0.9
        with open(temp_config_file, "w") as f:
            yaml.dump(data, f)

        # Перезагружаем
        config_manager.reload()
        config = config_manager.get_config()

        assert config.agents["test-agent"].temperature == 0.9

    def test_update_agent_config(self, temp_config_file):
        """Обновление конфигурации агента в памяти."""
        config_manager = ConfigManager(temp_config_file, auto_reload=False)

        config_manager.update_agent_config("test-agent", {"temperature": 0.95, "max_tokens": 2048})
        agent_config = config_manager.get_agent_config("test-agent")

        assert agent_config.temperature == 0.95
        assert agent_config.max_tokens == 2048

    def test_validate_valid_config(self, temp_config_file):
        """Проверка валидности конфигурации."""
        config_manager = ConfigManager(temp_config_file, auto_reload=False)
        assert config_manager.validate() is True

    def test_context_manager(self, temp_config_file):
        """Использование как контекстного менеджера."""
        with ConfigManager(temp_config_file, auto_reload=True) as config_manager:
            config = config_manager.get_config()
            assert config is not None
        # После выхода из контекста наблюдение должно быть остановлено
        assert config_manager._observer is None
