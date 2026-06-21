#!/usr/bin/env python3
"""
Тесты для AI Provider Manager
"""

import unittest
from unittest.mock import patch

from apps.ai_provider_manager.src.ai_provider_manager import (
    AIProviderManager,
    ProviderConfig,
    ProviderStatus,
    chat_with_fallback,
)


class TestAIProviderManager(unittest.TestCase):
    """Тесты для AIProviderManager"""

    def setUp(self):
        """Настройка теста"""
        self.manager = AIProviderManager()

    def test_initialization(self):
        """Тест инициализации"""
        self.assertIn("gigachat", self.manager.providers)
        self.assertIn("ollama", self.manager.providers)
        self.assertEqual(len(self.manager.fallback_chain), 2)
        self.assertEqual(self.manager.providers["gigachat"].priority, 1)
        self.assertEqual(self.manager.providers["ollama"].priority, 2)

    def test_get_active_provider(self):
        """Тест получения активного провайдера"""
        # Устанавливаем статусы
        self.manager.set_provider_status("gigachat", ProviderStatus.AVAILABLE)
        active = self.manager.get_active_provider()
        self.assertEqual(active, "gigachat")

        # GigaChat недоступен, Ollama доступен
        self.manager.set_provider_status("gigachat", ProviderStatus.UNAVAILABLE)
        self.manager.set_provider_status("ollama", ProviderStatus.AVAILABLE)
        active = self.manager.get_active_provider()
        self.assertEqual(active, "ollama")

    def test_set_provider_status(self):
        """Тест установки статуса провайдера"""
        self.manager.set_provider_status("gigachat", ProviderStatus.UNAVAILABLE, "Test error")
        self.assertEqual(self.manager.providers["gigachat"].status, ProviderStatus.UNAVAILABLE)
        self.assertEqual(self.manager.providers["gigachat"].last_error, "Test error")
        self.assertGreater(self.manager.providers["gigachat"].error_count, 0)

    @patch("requests.get")
    def test_test_gigachat(self, mock_get):
        """Тест проверки доступности GigaChat"""
        # Успешная проверка
        mock_get.return_value.status_code = 200
        result = self.manager._test_gigachat()
        self.assertTrue(result)

        # Неуспешная проверка
        mock_get.return_value.status_code = 404
        result = self.manager._test_gigachat()
        self.assertFalse(result)

    @patch("requests.get")
    def test_test_ollama(self, mock_get):
        """Тест проверки доступности Ollama"""
        # Успешная проверка
        mock_get.return_value.status_code = 200
        result = self.manager._test_ollama()
        self.assertTrue(result)

        # Неуспешная проверка
        mock_get.return_value.status_code = 404
        result = self.manager._test_ollama()
        self.assertFalse(result)

    def test_get_status(self):
        """Тест получения статуса всех провайдеров"""
        status = self.manager.get_status()
        self.assertIn("gigachat", status)
        self.assertIn("ollama", status)
        self.assertEqual(status["gigachat"]["name"], "GigaChat")
        self.assertEqual(status["ollama"]["name"], "Ollama")

    @patch.object(AIProviderManager, "_chat_gigachat")
    def test_chat_with_gigachat_success(self, mock_chat):
        """Тест чата с GigaChat (успех)"""
        mock_chat.return_value = "Test response from GigaChat"
        self.manager.set_provider_status("gigachat", ProviderStatus.AVAILABLE)
        self.manager.set_provider_status("ollama", ProviderStatus.UNAVAILABLE)

        response = self.manager.chat([{"role": "user", "content": "Hello"}])
        self.assertEqual(response, "Test response from GigaChat")
        self.assertEqual(self.manager.providers["gigachat"].status, ProviderStatus.AVAILABLE)

    @patch.object(AIProviderManager, "_chat_ollama")
    def test_chat_with_ollama_fallback(self, mock_chat):
        """Тест чата с Ollama (fallback)"""
        mock_chat.return_value = "Test response from Ollama"
        self.manager.set_provider_status("gigachat", ProviderStatus.UNAVAILABLE)
        self.manager.set_provider_status("ollama", ProviderStatus.AVAILABLE)

        response = self.manager.chat([{"role": "user", "content": "Hello"}])
        self.assertEqual(response, "Test response from Ollama")
        self.assertEqual(self.manager.providers["ollama"].status, ProviderStatus.AVAILABLE)

    @patch.object(AIProviderManager, "_chat_gigachat")
    @patch.object(AIProviderManager, "_chat_ollama")
    def test_chat_all_unavailable(self, mock_ollama, mock_gigachat):
        """Тест когда все провайдеры недоступны"""
        mock_gigachat.side_effect = Exception("GigaChat error")
        mock_ollama.side_effect = Exception("Ollama error")

        response = self.manager.chat([{"role": "user", "content": "Hello"}])
        self.assertIsNone(response)

    @patch.object(AIProviderManager, "chat")
    def test_chat_with_fallback_function(self, mock_chat):
        """Тест функции chat_with_fallback"""
        mock_chat.return_value = "Global response"
        response = chat_with_fallback([{"role": "user", "content": "Hello"}])
        self.assertEqual(response, "Global response")


class TestProviderConfig(unittest.TestCase):
    """Тесты для ProviderConfig"""

    def test_provider_config_defaults(self):
        """Тест значений по умолчанию для ProviderConfig"""
        config = ProviderConfig(name="TestProvider")
        self.assertEqual(config.name, "TestProvider")
        self.assertTrue(config.enabled)
        self.assertEqual(config.priority, 1)
        self.assertEqual(config.timeout, 30)
        self.assertEqual(config.max_retries, 3)
        self.assertEqual(config.retry_delay, 1.0)
        self.assertEqual(config.status, ProviderStatus.AVAILABLE)
        self.assertIsNone(config.last_error)
        self.assertEqual(config.error_count, 0)
        self.assertIsNone(config.last_success)


if __name__ == "__main__":
    unittest.main()
