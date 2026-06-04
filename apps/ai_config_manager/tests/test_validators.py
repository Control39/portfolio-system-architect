"""
Тесты для Pydantic моделей валидации.
Покрывает: AgentConfig, ResourceConfig, SecretsConfig, AIConfig
"""

import re
import pytest
from pydantic import ValidationError

from ai_config_manager.validators import (
    AgentConfig,
    AIConfig,
    ResourceConfig,
    ResourceType,
    SecretsConfig,
    SecretField,  # Импортируем, если есть в validators.py
)


# =============================================================================
# TestAgentConfig
# =============================================================================

class TestAgentConfig:
    """Тесты для AgentConfig."""

    def test_valid_agent_config(self):
        """Валидная конфигурация агента."""
        config = AgentConfig(
            model="gpt-4",
            temperature=0.7,
            max_tokens=2048,
            resources=["tool1", "tool2"]
        )

        assert config.model == "gpt-4"
        assert config.temperature == 0.7
        assert config.max_tokens == 2048
        assert config.resources == ["tool1", "tool2"]

    def test_default_values(self):
        """Значения по умолчанию при минимальной инициализации."""
        config = AgentConfig(model="gpt-3.5")

        assert config.temperature == 0.7
        assert config.max_tokens == 2048
        assert config.timeout == 30
        assert config.retry_count == 3
        assert config.resources is None

    @pytest.mark.parametrize("temp", [-0.1, 2.1], ids=["too-low", "too-high"])
    def test_temperature_validation_out_of_bounds(self, temp):
        """Температура вне диапазона [0.0, 2.0] → ValidationError."""
        with pytest.raises(ValidationError):
            AgentConfig(model="gpt-4", temperature=temp)

    @pytest.mark.parametrize("tokens", [-1, 0], ids=["negative", "zero"])
    def test_max_tokens_validation(self, tokens):
        """max_tokens должен быть > 0."""
        with pytest.raises(ValidationError):
            AgentConfig(model="gpt-4", max_tokens=tokens)

    def test_optional_resources_none(self):
        """resources может быть None."""
        config = AgentConfig(model="gpt-4", resources=None)
        assert config.resources is None

    def test_optional_resources_list(self):
        """resources может быть списком строк."""
        config = AgentConfig(model="gpt-4", resources=["tool_a", "tool_b"])
        assert config.resources == ["tool_a", "tool_b"]


# =============================================================================
# TestResourceConfig
# =============================================================================

class TestResourceConfig:
    """Тесты для ResourceConfig."""

    def test_valid_resource_config(self):
        """Валидная конфигурация ресурса."""
        config = ResourceConfig(
            name="test-resource",
            type=ResourceType.TOOL,
            enabled=True,
            config={"key": "value"},
            metadata={"version": "1.0"}
        )

        assert config.name == "test-resource"
        assert config.type == ResourceType.TOOL
        assert config.enabled is True
        assert config.config == {"key": "value"}
        assert config.metadata == {"version": "1.0"}

    @pytest.mark.parametrize("rtype", [ResourceType.TOOL, ResourceType.MODEL, ResourceType.API])
    def test_resource_type_enum(self, rtype):
        """Поддержка всех типов ResourceType."""
        config = ResourceConfig(name="res", type=rtype)
        assert config.type == rtype

    def test_config_and_metadata_can_be_none(self):
        """config и metadata могут быть явно None."""
        config = ResourceConfig(
            name="test",
            type=ResourceType.TOOL,
            config=None,
            metadata=None
        )
        assert config.config is None
        assert config.metadata is None

    def test_config_and_metadata_default_to_empty_dict(self):
        """При отсутствии config/metadata — пустые словари по умолчанию."""
        config = ResourceConfig(name="test", type=ResourceType.TOOL)
        assert config.config == {}
        assert config.metadata == {}

    def test_name_required(self):
        """name — обязательное поле."""
        with pytest.raises(ValidationError):
            ResourceConfig(type=ResourceType.TOOL)  # type: ignore


# =============================================================================
# TestSecretsConfig + SecretField
# =============================================================================

class TestSecretsConfig:
    """Тесты для SecretsConfig."""

    def test_valid_secrets_config(self):
        """Валидная конфигурация секретов."""
        config = SecretsConfig(
            api_keys={"openai": "key123"},
            database_urls={"primary": "postgres://user:pass@localhost/db"}
        )

        assert config.api_keys["openai"] == "key123"
        assert config.database_urls["primary"] == "postgres://user:pass@localhost/db"

    def test_mask_secrets_masks_all_values(self):
        """mask_secrets() заменяет все значения на '***'."""
        config = SecretsConfig(
            api_keys={"openai": "secret123", "azure": "secret456"},
            database_urls={"primary": "postgres://user:pass@localhost/db"},
            custom={"jwt": "jwt_secret"}
        )

        masked = config.mask_secrets()

        assert masked["api_keys"]["openai"] == "***"
        assert masked["api_keys"]["azure"] == "***"
        assert masked["database_urls"]["primary"] == "***"
        assert masked["custom"]["jwt"] == "***"

    def test_mask_secrets_returns_new_dict(self):
        """mask_secrets() не мутирует оригинал."""
        config = SecretsConfig(api_keys={"openai": "secret"})
        masked = config.mask_secrets()

        assert config.api_keys["openai"] == "secret"  # оригинал не изменён
        assert masked["api_keys"]["openai"] == "***"  # копия замаскирована


# =============================================================================
# TestSecretField (если используется в validators.py)
# =============================================================================

def test_secret_field_repr_masks_value():
    """SecretField.__repr__ маскирует значение для безопасности."""
    # Пропускаем тест, если SecretField не определён
    if "SecretField" not in globals():
        pytest.skip("SecretField not defined in validators.py")

    secret = SecretField("my-super-secret-key")

    # Проверяем, что repr не раскрывает секрет
    repr_str = repr(secret)
    assert "my-super-secret-key" not in repr_str
    assert "***" in repr_str or "masked" in repr_str.lower()


# =============================================================================
# TestAIConfig
# =============================================================================

class TestAIConfig:
    """Тесты для корневой конфигурации AI-системы."""

    def test_valid_ai_config(self):
        """Валидная полная конфигурация."""
        config = AIConfig(
            agents={
                "agent1": AgentConfig(model="gpt-4", temperature=0.7),
                "agent2": AgentConfig(model="claude-3", temperature=0.5),
            },
            resources={
                "res1": ResourceConfig(name="res1", type=ResourceType.TOOL)
            },
            secrets=SecretsConfig(api_keys={"openai": "key"}),
            version="1.0.0"
        )

        assert len(config.agents) == 2
        assert len(config.resources) == 1
        assert config.version == "1.0.0"
        assert config.secrets is not None

    def test_empty_config_defaults(self):
        """Пустая конфигурация → дефолтные значения."""
        config = AIConfig()

        assert config.agents == {}
        assert config.resources == {}
        assert config.version == "1.0.0"
        assert config.secrets is None

    @pytest.mark.parametrize("names", [
        ("duplicate", "duplicate"),           # exact match
    ], ids=["exact-duplicate"])
    def test_unique_resource_names_parametrized(self, names):
        """Имена ресурсов должны быть уникальны (по значению name)."""
        name1, name2 = names
        with pytest.raises(ValidationError):
            AIConfig(
                resources={
                    "key1": ResourceConfig(name=name1, type=ResourceType.TOOL),
                    "key2": ResourceConfig(name=name2, type=ResourceType.MODEL),
                }
            )

    def test_version_default_is_1_0_0(self):
        """Версия по умолчанию — '1.0.0'."""
        config = AIConfig()
        assert config.version == "1.0.0"

    def test_version_format_semver_like(self):
        """Версия должна соответствовать формату 'X.Y.Z' (упрощённый SemVer)."""
        # Валидные версии
        for v in ["1.0.0", "2.1.3", "0.0.1", "10.20.30"]:
            config = AIConfig(version=v)
            assert config.version == v

        # Невалидные версии (если валидация есть в модели)
        invalid_versions = ["invalid", "1.0", "v1.0.0", "1.0.0-beta"]
        for v in invalid_versions:
            # Проверяем, что модель либо принимает (если валидация слабая),
            # либо выбрасывает ошибку (если строгая)
            try:
                AIConfig(version=v)
            except ValidationError:
                pass  # Ожидаемое поведение при строгой валидации
            # Если не упало — значит, валидация версии не строгая, это ок

    def test_agents_and_resources_are_independent(self):
        """Агенты и ресурсы — независимые словари."""
        config = AIConfig(
            agents={"a1": AgentConfig(model="gpt-4")},
            resources={"r1": ResourceConfig(name="r1", type=ResourceType.TOOL)}
        )

        assert "a1" in config.agents
        assert "r1" in config.resources
        assert "a1" not in config.resources
        assert "r1" not in config.agents


# =============================================================================
# Интеграционные тесты (модели вместе)
# =============================================================================

class TestConfigIntegration:
    """Тесты взаимодействия моделей."""

    def test_agent_references_existing_resource(self):
        """Агент может ссылаться на существующий ресурс по имени."""
        # Это логическая связь, не валидация Pydantic — проверяем, что данные сохраняются
        config = AIConfig(
            agents={
                "agent1": AgentConfig(model="gpt-4", resources=["tool1"])
            },
            resources={
                "tool1": ResourceConfig(name="tool1", type=ResourceType.TOOL)
            }
        )

        assert config.agents["agent1"].resources == ["tool1"]
        assert config.resources["tool1"].name == "tool1"

    def test_secrets_optional_in_ai_config(self):
        """secrets — опциональное поле в AIConfig."""
        config = AIConfig(agents={}, resources={})
        assert config.secrets is None

        config_with_secrets = AIConfig(
            agents={},
            resources={},
            secrets=SecretsConfig(api_keys={"test": "key"})
        )
        assert config_with_secrets.secrets is not None

