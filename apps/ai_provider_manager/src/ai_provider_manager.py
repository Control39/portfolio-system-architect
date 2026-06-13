#!/usr/bin/env python3
"""
AI Provider Manager - Автоматическое переключение между GigaChat и Ollama

Primary: GigaChat (облако)
Fallback: Ollama (локальные модели)

Использует стратегию:
1. Пробуем GigaChat
2. При ошибке пробуем Ollama
3. При успехе Ollama - помечаем GigaChat как "temporarily unavailable"
4. Периодически пробуем восстановить GigaChat
"""

import json
import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any

import requests

logger = logging.getLogger(__name__)


class ProviderStatus(Enum):
    """Статус провайдера"""

    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    DEGRADED = "degraded"


@dataclass
class ProviderConfig:
    """Конфигурация провайдера"""

    name: str
    enabled: bool = True
    priority: int = 1
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    status: ProviderStatus = ProviderStatus.AVAILABLE
    last_error: str | None = None
    error_count: int = 0
    last_success: float | None = None


class AIProviderManager:
    """
    Управляет AI провайдерами с автоматическим переключением

    Пример использования:
    ```python
    manager = AIProviderManager()
    response = manager.chat("Привет!")
    ```
    """

    def __init__(self, config_path: str = "config/ai-config.yaml"):
        self.config_path = config_path
        self.providers: dict[str, ProviderConfig] = {}
        self.current_provider: str | None = None
        self.fallback_chain: list[str] = []

        # Инициализация провайдеров
        self._init_providers()

    def _init_providers(self):
        """Инициализация провайдеров из конфигурации"""

        # GigaChat (Primary)
        self.providers["gigachat"] = ProviderConfig(
            name="GigaChat", enabled=True, priority=1, timeout=30, max_retries=3, retry_delay=1.0
        )

        # Ollama (Fallback)
        self.providers["ollama"] = ProviderConfig(
            name="Ollama", enabled=True, priority=2, timeout=60, max_retries=3, retry_delay=2.0
        )

        # Сортируем по приоритету
        self.fallback_chain = sorted(
            [k for k, v in self.providers.items() if v.enabled],
            key=lambda x: self.providers[x].priority,
        )

        logger.info(f"AI Providers initialized: {self.fallback_chain}")

    def get_active_provider(self) -> str | None:
        """Получить активный провайдер"""
        if self.current_provider and self.providers.get(self.current_provider):
            return self.current_provider

        # Если нет активного, выбираем первый доступный
        for provider_name in self.fallback_chain:
            provider = self.providers[provider_name]
            if provider.status == ProviderStatus.AVAILABLE:
                return provider_name

        return None

    def set_provider_status(self, provider: str, status: ProviderStatus, error: str | None = None):
        """Установить статус провайдера"""
        if provider not in self.providers:
            return

        self.providers[provider].status = status
        self.providers[provider].last_error = error

        if status == ProviderStatus.AVAILABLE:
            self.providers[provider].error_count = 0
            self.providers[provider].last_success = time.time()
            self.current_provider = provider
        else:
            self.providers[provider].error_count += 1
            logger.warning(f"{provider} marked as {status.value}: {error}")

    def try_provider(self, provider_name: str) -> bool:
        """Попробовать подключить провайдер"""
        provider = self.providers.get(provider_name)
        if not provider or not provider.enabled:
            return False

        try:
            if provider_name == "gigachat":
                return self._test_gigachat()
            elif provider_name == "ollama":
                return self._test_ollama()
        except Exception as e:
            logger.error(f"Error testing {provider_name}: {e}")

        return False

    def _test_gigachat(self) -> bool:
        """Проверить доступность GigaChat"""
        try:
            # Проверяем Health API
            response = requests.get("https://gigachat.devices.sberbank.ru/api/v1/health", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.debug(f"GigaChat health check failed: {e}")
            return False

    def _test_ollama(self) -> bool:
        """Проверить доступность Ollama"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.debug(f"Ollama health check failed: {e}")
            return False

    def chat(self, messages: list[dict[str, str]], temperature: float = 0.7) -> str | None:
        """
        Отправить сообщение в AI с автоматическим переключением провайдеров

        Args:
            messages: Список сообщений в формате [{"role": "user", "content": "..."}]
            temperature: Температура генерации (0.0-2.0)

        Returns:
            Ответ от AI или None если все провайдеры недоступны
        """
        # Пробуем провайдеры по очереди
        for provider_name in self.fallback_chain:
            provider = self.providers[provider_name]

            # Проверяем статус
            if provider.status == ProviderStatus.UNAVAILABLE:
                # Пробуем восстановить
                if self.try_provider(provider_name):
                    self.set_provider_status(provider_name, ProviderStatus.AVAILABLE)
                else:
                    continue

            logger.info(f"Trying provider: {provider_name}")

            try:
                if provider_name == "gigachat":
                    response = self._chat_gigachat(messages, temperature)
                elif provider_name == "ollama":
                    response = self._chat_ollama(messages, temperature)
                else:
                    continue

                if response:
                    # Успех!
                    self.set_provider_status(provider_name, ProviderStatus.AVAILABLE)
                    return response

            except Exception as e:
                logger.error(f"Error with {provider_name}: {e}")
                self.set_provider_status(provider_name, ProviderStatus.UNAVAILABLE, str(e))
                continue

        logger.error("All AI providers unavailable")
        return None

    def _chat_gigachat(self, messages: list[dict[str, str]], temperature: float) -> str | None:
        """Отправить сообщение в GigaChat"""
        from apps.ai_config_manager.src.config_manager import ConfigManager

        config = ConfigManager()
        token = config.get_gigachat_token()

        if not token:
            raise ValueError("GigaChat token not found")

        url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-User-ID": "cognitive-agent",
        }

        payload = {
            "model": "GigaChat-Latest",
            "messages": messages,
            "temperature": temperature,
            "max_tokens": 8192,
        }

        response = requests.post(url, json=payload, headers=headers, timeout=30)

        if response.status_code != 200:
            raise Exception(f"GigaChat API error: {response.status_code} - {response.text}")

        result = response.json()
        return result["choices"][0]["message"]["content"]

    def _chat_ollama(self, messages: list[dict[str, str]], temperature: float) -> str | None:
        """Отправить сообщение в Ollama"""
        # Получаем список доступных моделей
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code != 200:
                raise Exception("Ollama not available")

            models = response.json().get("models", [])
            if not models:
                raise Exception("No models available in Ollama")

            # Используем первую доступную модель
            model_name = models[0]["name"]
            logger.info(f"Using Ollama model: {model_name}")

        except Exception as e:
            logger.error(f"Error getting Ollama models: {e}")
            raise

        url = "http://localhost:11434/api/chat"

        payload = {
            "model": model_name,
            "messages": messages,
            "temperature": temperature,
            "stream": False,
        }

        response = requests.post(url, json=payload, timeout=60)

        if response.status_code != 200:
            raise Exception(f"Ollama API error: {response.status_code} - {response.text}")

        result = response.json()
        return result["message"]["content"]

    def get_status(self) -> dict[str, Any]:
        """Получить статус всех провайдеров"""
        return {
            provider: {
                "name": config.name,
                "enabled": config.enabled,
                "status": config.status.value,
                "priority": config.priority,
                "error_count": config.error_count,
                "last_error": config.last_error,
                "last_success": config.last_success,
            }
            for provider, config in self.providers.items()
        }


# Глобальный экземпляр
_provider_manager: AIProviderManager | None = None


def get_provider_manager() -> AIProviderManager:
    """Получить глобальный экземпляр AIProviderManager"""
    global _provider_manager
    if _provider_manager is None:
        _provider_manager = AIProviderManager()
    return _provider_manager


def chat_with_fallback(messages: list[dict[str, str]], temperature: float = 0.7) -> str | None:
    """Удобная функция для чата с автоматическим fallback"""
    manager = get_provider_manager()
    return manager.chat(messages, temperature)


if __name__ == "__main__":
    # Тест
    manager = AIProviderManager()

    print("📊 AI Providers Status:")
    print(json.dumps(manager.get_status(), indent=2, ensure_ascii=False))

    print("\n🧪 Testing chat...")
    response = manager.chat([{"role": "user", "content": "Привет! Как дела?"}])
    if response:
        print(f"✅ Response: {response[:100]}...")
    else:
        print("❌ No response from any provider")
