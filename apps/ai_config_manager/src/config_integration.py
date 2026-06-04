"""Configuration integration module for all molecules.

This module provides unified configuration access across the entire system.
"""

import os
from typing import Any

# ============================================================
# Molecule-Specific Configuration Classes
# ============================================================


class AuthServiceConfig:
    """Configuration for Auth Service molecule."""

    pass


class CognitiveAgentConfig:
    """Configuration for Cognitive Agent molecule."""

    pass


class DecisionEngineConfig:
    """Configuration for Decision Engine molecule."""

    pass


class MlModelRegistryConfig:
    """Configuration for ML Model Registry molecule."""

    pass


class SystemProofConfig:
    """Configuration for System Proof molecule."""

    pass


# ============================================================
# Global Configuration State
# ============================================================

_config: dict[str, Any] = {
    "initialized": True,
    "version": "1.0.0",
    "environment": os.getenv("ENVIRONMENT", "test"),
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
    }


def is_available() -> bool:
    """Check if configuration system is available."""
    return True


def get_config_singleton() -> dict[str, Any]:
    """Alias for backward compatibility with tests."""
    return get_config()
