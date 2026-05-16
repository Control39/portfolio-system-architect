"""
Тесты для Pydantic моделей валидации.
"""

import pytest
from pydantic import ValidationError

from src.validators import AgentConfig, AIConfig, ResourceConfig, ResourceType, SecretsConfig


class TestAgentConfig:
    """Тесты для AgentConfig."""

    def test_valid_agent_config(self):
        """Валидная конфигурация агента."""
        config = AgentConfig(model="gpt-4", temperature=0.7, max_tokens=2048, resources=["tool1", "tool2"])

        assert config.model == "gpt-4"
        assert config.temperature == 0.7
        assert config.max_tokens == 2048
        assert len(config.resources) == 2

    def test_default_values(self):
        """Значения по умолчанию."""
        config = AgentConfig(model="gpt-3.5")

        assert config.temperature == 0.7
        assert config.max_tokens == 2048
        assert config.timeout == 30
        assert config.retry_count == 3

    def test_temperature_validation_min(self):
        """Валидация температуры (минимум)."""
        with pytest.raises(ValidationError):
            AgentConfig(model="gpt-4", temperature=-0.1)

    def test_temperature_validation_max(self):
        """Валидация температуры (максимум)."""
        with pytest.raises(ValidationError):
            AgentConfig(model="gpt-4", temperature=2.1)

    def test_max_tokens_validation(self):
        """Валидация max_tokens."""
        with pytest.raises(ValidationError):
            AgentConfig(model="gpt-4", max_tokens=0)

    def test_optional_resources(self):
        """Опциональные ресурсы."""
        config = AgentConfig(model="gpt-4", resources=None)
        assert config.resources is None


class TestResourceConfig:
    """Тесты для ResourceConfig."""

    def test_valid_resource_config(self):
        """Валидная конфигурация ресурса."""
        config = ResourceConfig(name="test-resource", type=ResourceType.TOOL, enabled=True, config={"key": "value"})

        assert config.name == "test-resource"
        assert config.type == ResourceType.TOOL
        assert config.enabled is True

    def test_resource_type_tool(self):
        """Тип ресурса TOOL."""
        config = ResourceConfig(name="tool1", type=ResourceType.TOOL)
        assert config.type == ResourceType.TOOL

    def test_resource_type_model(self):
        """Тип ресурса MODEL."""
        config = ResourceConfig(name="model1", type=ResourceType.MODEL)
        assert config.type == ResourceType.MODEL

    def test_resource_type_api(self):
        """Тип ресурса API."""
        config = ResourceConfig(name="api1", type=ResourceType.API)
        assert config.type == ResourceType.API

    def test_empty_config_dict(self):
        """Пустой словарь конфигурации."""
        config = ResourceConfig(name="test", type=ResourceType.TOOL)
        assert config.config == {}
        assert config.metadata == {}


class TestSecretsConfig:
    """Тесты для SecretsConfig."""

    def test_valid_secrets_config(self):
        """Валидная конфигурация секретов."""
        config = SecretsConfig(api_keys={"openai": "key123"}, database_urls={"primary": "postgres://..."})

        assert config.api_keys["openai"] == "key123"
        assert config.database_urls["primary"] == "postgres://..."

    def test_mask_secrets(self):
        """Маскирование секретов."""
        config = SecretsConfig(
            api_keys={"openai": "secret123", "azure": "secret456"},
            database_urls={"primary": "postgres://user:pass@localhost/db"},
            custom={"jwt": "jwt_secret"},
        )

        masked = config.mask_secrets()

        assert masked["api_keys"]["openai"] == "***"
        assert masked["api_keys"]["azure"] == "***"
        assert masked["database_urls"]["primary"] == "***"
        assert masked["custom"]["jwt"] == "***"


class TestAIConfig:
    """Тесты для AIConfig."""

    def test_valid_ai_config(self):
        """Валидная конфигурация AI-системы."""
        config = AIConfig(
            agents={
                "agent1": AgentConfig(model="gpt-4", temperature=0.7),
                "agent2": AgentConfig(model="claude-3", temperature=0.5),
            },
            resources={"resource1": ResourceConfig(name="res1", type=ResourceType.TOOL)},
            version="1.0.0",
        )

        assert len(config.agents) == 2
        assert len(config.resources) == 1
        assert config.version == "1.0.0"

    def test_empty_config(self):
        """Пустая конфигурация."""
        config = AIConfig()

        assert config.agents == {}
        assert config.resources == {}
        assert config.version == "1.0.0"

    def test_unique_resource_names(self):
        """Уникальность имён ресурсов."""
        with pytest.raises(ValidationError):
            AIConfig(
                resources={
                    "key1": ResourceConfig(name="duplicate", type=ResourceType.TOOL),
                    "key2": ResourceConfig(name="duplicate", type=ResourceType.MODEL),
                }
            )

    def test_default_version(self):
        """Версия по умолчанию."""
        config = AIConfig()
        assert config.version == "1.0.0"
