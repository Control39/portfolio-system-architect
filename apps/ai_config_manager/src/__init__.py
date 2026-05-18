"""
AI Config Manager - Централизованное управление конфигурациями AI-агентов.

Модуль предоставляет:
- ConfigManager: загрузка, валидация, hot reload конфигураций
- ResourcePool: управление пулом ресурсов (модели, API, инструменты)
- Security: маскирование секретов для безопасного логирования

Пример использования:
    from apps.ai_config_manager import ConfigManager, ResourcePool

    # Загрузка конфигурации
    config = ConfigManager('config/ai-config.yaml')

    # Получение конфигурации агента
    agent_config = config.get_agent_config('cognitive-agent')

    # Работа с ресурсами
    pool = ResourcePool()
    pool.register(config.get_resource_config('code-analyzer'))
    pool.connect('code-analyzer')
"""

from .config_manager import ConfigManager
from .resource_pool import ResourcePool
from .security import mask_dict, mask_sensitive, mask_string
from .validators import AgentConfig, AIConfig, ResourceConfig, ResourceType


__all__ = [
    "AIConfig",
    "AgentConfig",
    "ConfigManager",
    "ResourceConfig",
    "ResourcePool",
    "ResourceType",
    "mask_dict",
    "mask_sensitive",
    "mask_string",
]

__version__ = "1.0.0"
