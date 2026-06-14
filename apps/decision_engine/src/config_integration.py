# apps/decision_engine/src/config_integration.py
"""
Configuration integration module for decision engine.

Этот файл заменяет старый `config_integration.py` в корне `apps/`,
чтобы он попадал в контейнер по пути /app/src/config_integration.py
"""

import os
from typing import Any

_config: dict[str, Any] = {
    "initialized": True,
    "version": "1.0.0",
    "environment": os.getenv("ENVIRONMENT", "test"),
    "decision_engine": {
        "model": "gpt-4",
        "temperature": 0.7,
        "max_tokens": 2048,
    },
}


def get_config() -> dict[str, Any]:
    """Return global configuration dictionary."""
    return _config.copy()


def reload_config() -> None:
    """Reload configuration from environment."""
    global _config
    _config = {
        "initialized": True,
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "test"),
        "decision_engine": {
            "model": "gpt-4",
            "temperature": 0.7,
            "max_tokens": 2048,
        },
    }


def is_available() -> bool:
    """Check if configuration system is available."""
    return True


def get_config_singleton() -> dict[str, Any]:
    """Alias for backward compatibility."""
    return get_config()
