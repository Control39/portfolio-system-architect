"""
Pydantic модели для валидации конфигураций AI-агентов.
"""

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ResourceType(str, Enum):
    """Типы ресурсов."""

    TOOL = "tool"
    MODEL = "model"
    API = "api"
    DATABASE = "database"
    STORAGE = "storage"


class AgentConfig(BaseModel):
    """Конфигурация AI-агента."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "model": "gpt-4",
                "temperature": 0.7,
                "max_tokens": 2048,
                "resources": ["code-analyzer", "test-runner"],
                "timeout": 30,
                "retry_count": 3,
            }
        }
    )

    model: str = Field(..., description="Модель ИИ (например, gpt-4)")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Температура генерации")
    max_tokens: int = Field(default=2048, gt=0, description="Максимальное количество токенов")
    resources: list[str] | None = Field(
        default=None, description="Список имён используемых ресурсов"
    )
    timeout: int = Field(default=30, gt=0, description="Таймаут запроса в секундах")
    retry_count: int = Field(default=3, ge=0, description="Количество повторных попыток")


class ResourceConfig(BaseModel):
    """Конфигурация ресурса."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "code-analyzer",
                "type": "tool",
                "enabled": True,
                "config": {"language": "python", "linting": True},
                "metadata": {"version": "1.0.0"},
            }
        }
    )

    name: str = Field(..., description="Уникальное имя ресурса")
    type: ResourceType = Field(..., description="Тип ресурса")
    enabled: bool = Field(default=True, description="Включён ли ресурс")
    config: dict[str, Any] = Field(default_factory=dict, description="Конфигурация ресурса")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Дополнительные метаданные")


class SecretsConfig(BaseModel):
    """Конфигурация секретов."""

    api_keys: dict[str, str] = Field(default_factory=dict, description="API ключи")
    database_urls: dict[str, str] = Field(default_factory=dict, description="URL баз данных")
    custom: dict[str, str] = Field(default_factory=dict, description="Пользовательские секреты")

    def mask_secrets(self) -> dict[str, Any]:
        """Возвращает конфиг с замаскированными секретами."""
        return {
            "api_keys": dict.fromkeys(self.api_keys.keys(), "***"),
            "database_urls": dict.fromkeys(self.database_urls.keys(), "***"),
            "custom": dict.fromkeys(self.custom.keys(), "***"),
        }


class AIConfig(BaseModel):
    """Главная конфигурация AI-системы."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "agents": {
                    "cognitive-agent": {"model": "gpt-4", "temperature": 0.7, "max_tokens": 2048}
                },
                "resources": {
                    "code-analyzer": {
                        "name": "code-analyzer",
                        "type": "tool",
                        "enabled": True,
                        "config": {"language": "python"},
                    }
                },
                "version": "1.0.0",
            }
        }
    )

    agents: dict[str, AgentConfig] = Field(default_factory=dict, description="Конфигурации агентов")
    resources: dict[str, ResourceConfig] = Field(
        default_factory=dict, description="Конфигурации ресурсов"
    )
    secrets: SecretsConfig | None = Field(default=None, description="Конфигурация секретов")
    version: str = Field(default="1.0.0", description="Версия конфигурации")

    @field_validator("resources")
    @classmethod
    def validate_resource_names(cls, v: dict[str, ResourceConfig]) -> dict[str, ResourceConfig]:
        """Проверка уникальности имён ресурсов."""
        names = [r.name for r in v.values()]
        if len(names) != len(set(names)):
            raise ValueError("Имена ресурсов должны быть уникальными")
        return v
