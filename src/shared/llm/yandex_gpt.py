"""
Модуль для работы с Yandex GPT API через LangChain.
Поддерживает OpenAI-совместимый интерфейс Yandex Cloud AI.
"""

import logging
import os
from typing import Any, Dict, List, Optional

try:
    from langchain.callbacks.base import BaseCallbackHandler
except ImportError:
    # Для совместимости с новыми версиями langchain
    from langchain_core.callbacks import BaseCallbackHandler
try:
    from langchain.schema import AIMessage, HumanMessage, SystemMessage
except ImportError:
    # Для совместимости с новыми версиями langchain
    from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import Field
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


class YandexGPTConfig(BaseSettings):
    """Конфигурация Yandex GPT"""

    api_key: str = Field(
        default=os.getenv("YANDEX_GPT_API_KEY", ""),
        description="API ключ Yandex Cloud AI",
    )
    base_url: str = Field(
        default=os.getenv("YANDEX_GPT_BASE_URL", "https://ai.api.cloud.yandex.net/v1"),
        description="Базовый URL API Yandex Cloud AI",
    )
    model: str = Field(
        default=os.getenv("YANDEX_GPT_MODEL", "gpt://b1g8ug48iu3bb3gv8iom/yandexgpt/latest"),
        description="Идентификатор модели Yandex GPT",
    )
    temperature: float = Field(default=0.7, description="Температура для генерации (0.0-1.0)")
    max_tokens: int = Field(default=2000, description="Максимальное количество токенов в ответе")
    timeout: int = Field(default=30, description="Таймаут запроса в секундах")
    max_retries: int = Field(default=3, description="Максимальное количество повторных попыток")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class YandexGPTClient:
    """Клиент для работы с Yandex GPT через LangChain"""

    def __init__(
        self,
        config: Optional[YandexGPTConfig] = None,
        callbacks: Optional[List[BaseCallbackHandler]] = None,
    ):
        """
        Инициализация клиента Yandex GPT.

        Args:
            config: Конфигурация Yandex GPT
            callbacks: Коллбэки для обработки событий
        """
        self.config = config or YandexGPTConfig()
        self.callbacks = callbacks or []
        self._client = None

    @property
    def client(self) -> ChatOpenAI:
        """Ленивая инициализация клиента LangChain"""
        if self._client is None:
            self._client = ChatOpenAI(
                openai_api_key=self.config.api_key,
                openai_api_base=self.config.base_url,
                model_name=self.config.model,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                timeout=self.config.timeout,
                max_retries=self.config.max_retries,
                callbacks=self.callbacks,
                streaming=False,  # Yandex GPT может не поддерживать streaming
            )
        return self._client

    async def generate(
        self, prompt: str, system_message: str = "Ты полезный AI-ассистент.", **kwargs
    ) -> str:
        """
        Генерация текста с использованием Yandex GPT.

        Args:
            prompt: Пользовательский промпт
            system_message: Системное сообщение для контекста
            **kwargs: Дополнительные параметры для клиента

        Returns:
            Сгенерированный текст
        """
        try:
            messages = [
                SystemMessage(content=system_message),
                HumanMessage(content=prompt),
            ]

            response = await self.client.agenerate([messages], **kwargs)
            return response.generations[0][0].text

        except Exception as e:
            logger.error(f"Ошибка при генерации с Yandex GPT: {e}")
            raise

    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Чат с историей сообщений.

        Args:
            messages: Список сообщений в формате
                [{"role": "user/system/assistant", "content": "..."}]
            **kwargs: Дополнительные параметры

        Returns:
            Ответ модели
        """
        try:
            langchain_messages = []
            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")

                if role == "system":
                    langchain_messages.append(SystemMessage(content=content))
                elif role == "user":
                    langchain_messages.append(HumanMessage(content=content))
                elif role == "assistant":
                    langchain_messages.append(AIMessage(content=content))

            response = await self.client.agenerate([langchain_messages], **kwargs)
            return response.generations[0][0].text

        except Exception as e:
            logger.error(f"Ошибка в чате с Yandex GPT: {e}")
            raise

    def get_config(self) -> Dict[str, Any]:
        """Получить текущую конфигурацию"""
        return self.config.dict()


# Фабричные функции для удобства
def create_yandex_gpt_client(
    config: Optional[YandexGPTConfig] = None,
    callbacks: Optional[List[BaseCallbackHandler]] = None,
) -> YandexGPTClient:
    """Создать клиент Yandex GPT"""
    return YandexGPTClient(config=config, callbacks=callbacks)


async def generate_with_yandex_gpt(
    prompt: str,
    system_message: str = "Ты полезный AI-ассистент.",
    config: Optional[YandexGPTConfig] = None,
) -> str:
    """Упрощенная функция для генерации текста"""
    client = create_yandex_gpt_client(config)
    return await client.generate(prompt, system_message)


# Пример использования
if __name__ == "__main__":
    import asyncio

    async def example():
        """Пример использования модуля"""
        print("Тестирование подключения к Yandex GPT...")

        try:
            # Создаем клиент с конфигурацией по умолчанию
            client = create_yandex_gpt_client()

            # Тестовый запрос
            response = await client.generate(
                prompt="Привет! Как дела?",
                system_message="Ты дружелюбный AI-ассистент.",
            )

            print(f"Ответ Yandex GPT: {response}")
            print("Подключение успешно!")

        except Exception as e:
            print(f"Ошибка подключения: {e}")
            print("Проверьте настройки в .env файле:")
            print("  YANDEX_GPT_API_KEY=ваш_api_ключ")
            print("  YANDEX_GPT_BASE_URL=https://ai.api.cloud.yandex.net/v1")
            print("  YANDEX_GPT_MODEL=gpt://b1g8ug48iu3bb3gv8iom/yandexgpt/latest")

    asyncio.run(example())
