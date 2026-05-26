"""
Модуль интеграции с AI Config Manager для ai_config_manager
"""

from typing import Dict, Optional
from pathlib import Path

# Попытка импорта AI Config Manager
try:
    from apps.ai_config_manager.src.config_manager import ConfigManager
    AI_CONFIG_AVAILABLE = True
except ImportError:
    AI_CONFIG_AVAILABLE = False
    ConfigManager = None


class AiConfigManagerConfig:
    """Конфигурация ai_config_manager"""
    
    def __init__(self):
        self.config_manager = ConfigManager() if AI_CONFIG_AVAILABLE else None
        self._config: Optional[Dict] = None
    
    def get_config(self) -> Dict:
        """Получить конфигурацию"""
        if self._config is None and self.config_manager:
            self._config = self.config_manager.get_service_config("ai_config_manager")
        return self._config or {}  # Экранирование фигурных скобок для f-string
    
    def is_available(self) -> bool:
        """Проверка доступности конфигурации"""
        return self._config is not None


# Singleton instance
_instance: Optional["AiConfigManagerConfig"] = None


def get_config() -> "AiConfigManagerConfig":
    """Получить singleton инстанс конфигурации"""
    global _instance
    if _instance is None:
        _instance = AiConfigManagerConfig()
    return _instance


def reload_config() -> None:
    """Перезагрузить конфигурацию (hot reload)"""
    global _instance
    if _instance:
        _instance._config = None
