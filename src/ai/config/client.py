"""Единый клиент для работы с AI Config Manager."""

import os
from pathlib import Path
from typing import Any, Optional

from .config_manager import ConfigManager


class AIConfigClient:
    """Единый клиент для всех сервисов (singleton)."""

    _instance: Optional["AIConfigClient"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized"):
            return
        self._initialized = True

        repo_root = Path(__file__).parent.parent.parent.parent
        config_path = os.getenv("AI_CONFIG_PATH", str(repo_root / "config" / "ai-config.yaml"))
        self._config_manager = ConfigManager(config_path=config_path)

    def get_config(self) -> dict[str, Any]:
        return self._config_manager.get_config()

    def get_section(self, section: str) -> dict[str, Any]:
        return self._config_manager.get_section(section)

    def reload(self) -> None:
        self._config_manager.reload()

    @property
    def config_manager(self) -> ConfigManager:
        return self._config_manager


config_client = AIConfigClient()
