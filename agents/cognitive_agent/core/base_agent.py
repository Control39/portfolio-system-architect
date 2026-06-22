"""Core module for cognitive agent base classes."""

from pathlib import Path


def get_repo_root() -> Path:
    """Получить корень репозитория"""
    return Path(__file__).parent.parent.parent


def get_agent_data_dir() -> Path:
    """Получить директорию для runtime данных агента"""
    agent_data_dir = get_repo_root() / ".agent_data"
    agent_data_dir.mkdir(parents=True, exist_ok=True)
    return agent_data_dir
