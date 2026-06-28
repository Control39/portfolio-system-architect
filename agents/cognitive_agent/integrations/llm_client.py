#!/usr/bin/env python3
"""
LLM Client Wrapper для AI Provider Manager

Оборачивает AIProviderManager в интерфейс, совместимый с TestGenerator
"""

import asyncio
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


class LLMClient:
    """
    LLM Client wrapper для AI Provider Manager

    Использует chat_with_fallback для генерации ответов
    """

    def __init__(self, provider_manager=None):
        """
        Инициализация LLM Client

        Args:
            provider_manager: AIProviderManager экземпляр (опционально)
        """
        self.provider_manager = provider_manager
        self._provider_manager_instance = None

    async def generate(self, prompt: str, timeout: int = 60, temperature: float = 0.7) -> str:
        """
        Генерация ответа от LLM

        Args:
            prompt: Пользовательский запрос
            timeout: Таймаут в секундах
            temperature: Температура для генерации

        Returns:
            Сгенерированный текст
        """
        import time
        from apps.ai_provider_manager.src.ai_provider_manager import get_provider_manager

        start_time = time.time()

        # Получить provider manager
        if self.provider_manager:
            pm = self.provider_manager
        else:
            if self._provider_manager_instance is None:
                self._provider_manager_instance = get_provider_manager()
            pm = self._provider_manager_instance

        logger.info(f"🔄 Calling LLM provider: {pm.get_active_provider()}")

        # Форматировать сообщения
        messages = [
            {"role": "system", "content": "Ты — эксперт по Python и pytest. Генерируй качественные тесты."},
            {"role": "user", "content": prompt},
        ]

        try:
            # Вызвать chat_with_fallback
            response = await asyncio.to_thread(
                pm.chat,
                messages,
                temperature,
            )

            if response is None:
                logger.error("❌ LLM returned None - providers may be unavailable")
                logger.info(f"📊 Provider status: {pm.get_status()}")
                raise ValueError("LLM returned None response - providers may be unavailable")

            execution_time = time.time() - start_time
            logger.info(
                f"✅ LLM response generated in {execution_time:.2f}s",
                response_length=len(response),
                provider=pm.get_active_provider(),
            )

            return response

        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            raise

    async def generate_with_timeout(self, prompt: str, timeout: int = 60) -> str:
        """
        Генерация с таймаутом

        Args:
            prompt: Пользовательский запрос
            timeout: Таймаут в секундах

        Returns:
            Сгенерированный текст
        """
        try:
            return await asyncio.wait_for(
                self.generate(prompt),
                timeout=timeout,
            )
        except asyncio.TimeoutError:
            raise TimeoutError(f"LLM generation timed out after {timeout}s")


def create_llm_client() -> LLMClient:
    """
    Создать LLM Client экземпляр

    Returns:
        LLMClient: Инициализированный клиент
    """
    logger.info("🤖 Creating LLM client for AI Provider Manager")
    return LLMClient()
