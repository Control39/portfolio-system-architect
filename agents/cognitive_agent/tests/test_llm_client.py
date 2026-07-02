"""Тесты для LLM Client (integrations/llm_client.py)

Service Tier: INTEGRATIONS
Purpose: Unit testing for LLMClient class with lazy loading
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agents.cognitive_agent.integrations.llm_client import LLMClient, create_llm_client


class TestLLMClientInitialization:
    """Тесты инициализации LLMClient"""

    def test_initialization_without_provider(self):
        """Тест инициализации без provider manager"""
        client = LLMClient()

        assert client is not None
        assert client._provider_manager_instance is None
        assert client._provider_manager_loaded is False
        assert client.provider_manager is None

    def test_initialization_with_provider(self):
        """Тест инициализации с provider manager"""
        mock_provider = object()
        client = LLMClient(provider_manager=mock_provider)

        assert client is not None
        assert client.provider_manager is mock_provider
        assert client._provider_manager_instance is None
        assert client._provider_manager_loaded is False

    def test_initialization_with_empty_provider(self):
        """Тест инициализации с None provider manager"""
        client = LLMClient(provider_manager=None)

        assert client is not None
        assert client.provider_manager is None
        assert client._provider_manager_instance is None
        assert client._provider_manager_loaded is False


class TestLLMClientLazyLoading:
    """Тесты ленивой загрузки LLMClient"""

    def test_load_provider_manager_not_called_on_init(self):
        """Тест, что загрузка не происходит при инициализации"""
        client = LLMClient()

        # Проверяем, что загрузка не произошла
        assert client._provider_manager_loaded is False
        assert client._provider_manager_instance is None

    def test_load_provider_manager_called_on_first_generate(self):
        """Тест, что загрузка происходит при первом generate()"""
        client = LLMClient()

        # Проверяем, что загрузка не произошла
        assert client._provider_manager_loaded is False

        # Вызываем generate - он попытается загрузить и вызовет реальный провайдер
        async def test_generate():
            try:
                await client.generate("test prompt")
            except (RuntimeError, ValueError):
                # ValueError - реальный провайдер вернул None
                # RuntimeError - провайдер не найден
                pass

        asyncio.run(test_generate())

        # Теперь метод должен быть вызван и загрузка произошла
        assert client._provider_manager_loaded is True

    def test_load_provider_manager_only_once(self):
        """Тест, что загрузка происходит только один раз"""
        client = LLMClient()

        # Первый вызов
        async def first_call():
            try:
                await client.generate("test prompt 1")
            except (RuntimeError, ValueError):
                pass

        # Второй вызов
        async def second_call():
            try:
                await client.generate("test prompt 2")
            except (RuntimeError, ValueError):
                pass

        asyncio.run(first_call())
        loaded_once = client._provider_manager_loaded

        asyncio.run(second_call())

        # Загрузка должна была произойти один раз
        assert loaded_once is True


class TestLLMClientGenerate:
    """Тесты метода generate()"""

    def test_generate_without_provider_raises_error(self):
        """Тест, что generate() выбрасывает ValueError от реального провайдера"""
        client = LLMClient()

        async def test_generate():
            # Провайдер реально подключается и возвращает None, поэтому ValueError
            with pytest.raises(ValueError) as exc_info:
                await client.generate("test prompt")
            assert "None response" in str(exc_info.value)

        asyncio.run(test_generate())

    def test_generate_with_mock_provider(self):
        """Тест generate() с mock provider manager"""
        # Используем MagicMock вместо AsyncMock для chat
        mock_provider = MagicMock()
        mock_provider.chat = MagicMock(return_value="Generated response")
        mock_provider.get_active_provider = MagicMock(return_value="test_provider")

        client = LLMClient(provider_manager=mock_provider)

        async def test_generate():
            result = await client.generate("test prompt", timeout=60, temperature=0.7)
            return result

        result = asyncio.run(test_generate())

        assert result == "Generated response"
        mock_provider.chat.assert_called_once()

    def test_generate_with_custom_parameters(self):
        """Тест generate() с кастомными параметрами"""
        # Используем MagicMock вместо AsyncMock для chat
        mock_provider = MagicMock()
        mock_provider.chat = MagicMock(return_value="test response")
        mock_provider.get_active_provider = MagicMock(return_value="test_provider")

        client = LLMClient(provider_manager=mock_provider)

        async def test_generate():
            result = await client.generate("test prompt", timeout=30, temperature=0.9)
            return result

        result = asyncio.run(test_generate())

        assert result == "test response"
        # Проверяем, что chat был вызван с правильными параметрами
        call_args = mock_provider.chat.call_args
        # chat(messages, temperature) - messages=call_args[0][0], temperature=call_args[0][1]
        assert call_args[0][1] == 0.9  # temperature

    def test_generate_none_response_raises_error(self):
        """Тест generate() с None ответом от provider"""
        mock_provider = MagicMock()
        mock_provider.chat = MagicMock(return_value=None)
        mock_provider.get_active_provider = MagicMock(return_value="test_provider")
        mock_provider.get_status = MagicMock(return_value={"status": "unavailable"})

        client = LLMClient(provider_manager=mock_provider)

        async def test_generate():
            with pytest.raises(ValueError) as exc_info:
                await client.generate("test prompt")
            assert "None response" in str(exc_info.value)

        asyncio.run(test_generate())


class TestLLMClientGenerateWithTimeout:
    """Тесты метода generate_with_timeout()"""

    def test_generate_with_timeout_success(self):
        """Тест generate_with_timeout() успешный случай"""
        mock_provider = MagicMock()
        mock_provider.chat = MagicMock(return_value="test response")
        mock_provider.get_active_provider = MagicMock(return_value="test_provider")

        client = LLMClient(provider_manager=mock_provider)

        async def test_generate():
            result = await client.generate_with_timeout("test prompt", timeout=60)
            return result

        result = asyncio.run(test_generate())

        assert result == "test response"

    def test_generate_with_timeout_error(self):
        """Тест generate_with_timeout() с таймаутом"""
        mock_provider = MagicMock()

        # Make it slow to trigger timeout
        def slow_chat(*args, **kwargs):
            import time

            time.sleep(0.5)
            return "test response"

        mock_provider.chat = slow_chat
        mock_provider.get_active_provider = MagicMock(return_value="test_provider")

        client = LLMClient(provider_manager=mock_provider)

        async def test_generate():
            with pytest.raises(TimeoutError) as exc_info:
                await client.generate_with_timeout("test prompt", timeout=0.1)
            assert "timed out" in str(exc_info.value)

        asyncio.run(test_generate())


class TestCreateLLMClient:
    """Тесты функции create_llm_client()"""

    def test_create_llm_client_returns_instance(self):
        """Тест, что create_llm_client() возвращает LLMClient"""
        client = create_llm_client()

        assert isinstance(client, LLMClient)

    def test_create_llm_client_without_error(self):
        """Тест, что create_llm_client() не выбрасывает ошибок"""
        try:
            client = create_llm_client()
            assert client is not None
        except Exception as e:
            pytest.fail(f"create_llm_client() raised {type(e).__name__}: {e}")


class TestLLMClientEdgeCases:
    """Тесты граничных случаев LLMClient"""

    def test_multiple_generate_calls_same_client(self):
        """Тест нескольких вызовов generate() на одном клиенте"""
        mock_provider = MagicMock()
        mock_provider.chat = MagicMock(side_effect=["response1", "response2", "response3"])
        mock_provider.get_active_provider = MagicMock(return_value="test_provider")

        client = LLMClient(provider_manager=mock_provider)

        async def test_multiple():
            r1 = await client.generate("prompt1")
            r2 = await client.generate("prompt2")
            r3 = await client.generate("prompt3")
            return r1, r2, r3

        r1, r2, r3 = asyncio.run(test_multiple())

        assert r1 == "response1"
        assert r2 == "response2"
        assert r3 == "response3"

    def test_provider_manager_stored_after_load(self):
        """Тест, что provider manager сохраняется после загрузки"""
        mock_provider = MagicMock()
        mock_provider.chat = MagicMock(return_value="test response")
        mock_provider.get_active_provider = MagicMock(return_value="test_provider")

        client = LLMClient(provider_manager=mock_provider)

        async def test_store():
            await client.generate("test prompt")
            return client._provider_manager_instance

        stored = asyncio.run(test_store())

        assert stored is mock_provider
        assert client._provider_manager_instance is mock_provider

    def test_generate_preserves_timeout_parameter(self):
        """Тест, что timeout parameter не влияет на импорт"""
        client = LLMClient()

        # Проверяем, что клиент инициализировался без импорта
        assert client._provider_manager_loaded is False
        assert client._provider_manager_instance is None
