"""Конфигурация для тестов"""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def test_client():
    """Создание тестового клиента"""
    from tools.dev_tools.server import app

    # Создаем тестовый клиент
    return TestClient(app)


@pytest.fixture
def sample_messages():
    """Пример сообщений для теста"""
    return [
        {"role": "system", "content": "Ты полезный помощник."},
        {"role": "user", "content": "Привет! Как дела?"},
    ]


@pytest.fixture
def sample_config_codette():
    """Конфигурация для Codette"""
    return {
        "active_provider": "codette",
        "codette": {
            "model": "codette:7b",
            "temperature": 0.7,
        },
        "gigachat": {
            "model": "GigaChat-Pro",
            "api_key": "test_key",
        },
    }


@pytest.fixture
def sample_config_gigachat():
    """Конфигурация для GigaChat"""
    return {
        "active_provider": "gigachat",
        "codette": {
            "model": "codette:7b",
            "temperature": 0.7,
        },
        "gigachat": {
            "model": "GigaChat-Pro",
            "api_key": "test_key",
        },
    }
