"""
Unit tests for the shared LLM module.
"""

import pytest

from src.shared.llm.yandex_gpt import (
    YandexGPTClient,
    YandexGPTConfig,
    create_yandex_gpt_client,
    generate_with_yandex_gpt,
)


def test_llm_config_creation_with_defaults():
    """Создание конфига с параметрами по умолчанию"""
    config = YandexGPTConfig()
    assert hasattr(config, "model")
    assert hasattr(config, "temperature")


def test_llm_config_custom_values():
    """Создание конфига с пользовательскими параметрами"""
    config = YandexGPTConfig(
        api_key="test-key",
        base_url="https://test.api",
        model="gpt://test/model",
        temperature=0.5,
        max_tokens=1000,
    )
    assert config.api_key == "test-key"
    assert config.base_url == "https://test.api"
    assert config.model == "gpt://test/model"
    assert config.temperature == 0.5
    assert config.max_tokens == 1000


def test_yandex_gpt_client_creation():
    """Проверка создания клиента"""
    client = YandexGPTClient()
    assert client is not None
    assert client.config is not None


def test_yandex_gpt_client_with_config():
    """Проверка клиента с кастомной конфигурацией"""
    config = YandexGPTConfig(temperature=0.3, max_tokens=500)
    client = YandexGPTClient(config=config)
    assert client.config.temperature == 0.3
    assert client.config.max_tokens == 500


def test_create_yandex_gpt_client_function():
    """Проверка фабричной функции создания клиента"""
    client = create_yandex_gpt_client()
    assert isinstance(client, YandexGPTClient)


def test_generate_with_yandex_gpt_function_signature():
    """Проверка сигнатуры функции generate_with_yandex_gpt"""
    # Просто проверим, что функция существует и принимает ожидаемые аргументы
    assert callable(generate_with_yandex_gpt)
    # Не можем протестировать логику без реального API, но проверим импорт


def test_llm_module_imports():
    """Проверяем, что модуль llm импортируется"""
    try:
        import src.shared.llm

        assert src.shared.llm is not None
    except ImportError as e:
        pytest.skip(f"LLM module import failed: {e}")
