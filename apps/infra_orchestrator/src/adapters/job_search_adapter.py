"""
Адаптер для поиска вакансий через Cognitive Agent

Реализация интерфейса IJobSearch, которая делает HTTP-запросы
к сервису cognitive-agent вместо прямого импорта кода.

Преимущества:
- job_automation_agent не зависит от реализации cognitive_agent
- Легко заменить на другой источник вакансий (hh.ru API, LinkedIn API)
- Можно добавить retry, timeout, circuit breaker
- Тестируется через mock
"""

import logging
from typing import Any

import httpx

from src.interfaces.job_search import IJobSearch

logger = logging.getLogger(__name__)


class CognitiveJobSearch(IJobSearch):
    """Реализация поиска вакансий через Cognitive Agent API."""

    def __init__(
        self,
        base_url: str | None = None,
        timeout: float = 30.0,
        max_retries: int = 3,
    ):
        """
        Инициализация адаптера.

        Аргументы:
            base_url: Базовый URL сервиса cognitive-agent
                     По умолчанию берется из окружения или дефолтный
            timeout: Таймаут запроса в секундах
            max_retries: Максимальное количество попыток при ошибке
        """
        self.base_url = base_url or "http://cognitive-agent:8006"
        self.timeout = timeout
        self.max_retries = max_retries
        self._client = httpx.AsyncClient(timeout=timeout)

    async def search(self, query: str, **kwargs: Any) -> list[dict[str, Any]]:
        """
        Поиск вакансий через Cognitive Agent API.

        Аргументы:
            query: Строка запроса
            **kwargs: Дополнительные параметры (location, experience, salary_min, salary_max)

        Возвращает:
            Список вакансий в формате:
            [
                {
                    "title": "Python Developer",
                    "company": "TechCorp",
                    "location": "Москва",
                    "salary": "от 150 000 ₽",
                    "url": "https://hh.ru/vacancy/12345",
                    "description": "...",
                    "posted_at": "2026-05-18"
                }
            ]
        """
        url = f"{self.base_url}/api/v1/jobs/search"
        params = {"query": query, **kwargs}

        logger.info(f"Поиск вакансий: query='{query}', params={kwargs}")

        for attempt in range(self.max_retries):
            try:
                response = await self._client.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                # Нормализация ответа (адаптация под наш интерфейс)
                vacancies = data.get("vacancies", [])
                normalized = [self._normalize_job(job) for job in vacancies]

                logger.info(f"Найдено {len(normalized)} вакансий")
                return normalized

            except httpx.TimeoutException:
                logger.warning(f"Таймаут при поиске (попытка {attempt + 1}/{self.max_retries})")
                if attempt == self.max_retries - 1:
                    raise

            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP ошибка при поиске: {e}")
                if e.response.status_code >= 500 and attempt < self.max_retries - 1:
                    continue
                raise

            except Exception as e:
                logger.error(f"Неожиданная ошибка при поиске: {e}")
                raise

        return []

    async def get_details(self, job_id: str) -> dict[str, Any]:
        """
        Получение подробной информации о вакансии.

        Аргументы:
            job_id: Уникальный идентификатор вакансии

        Возвращает:
            Полная информация о вакансии
        """
        url = f"{self.base_url}/api/v1/jobs/{job_id}"

        logger.info(f"Получение деталей вакансии: job_id={job_id}")

        response = await self._client.get(url)
        response.raise_for_status()

        return self._normalize_job(response.json())

    def _normalize_job(self, job: dict[str, Any]) -> dict[str, Any]:
        """
        Нормализация данных вакансии к единому формату.

        Преобразует разные форматы ответов в стандартный вид.
        """
        return {
            "job_id": job.get("id", job.get("job_id", "")),
            "title": job.get("title", job.get("name", "Не указано")),
            "company": job.get("company", job.get("employer", "Не указано")),
            "location": job.get("location", job.get("city", "Не указано")),
            "salary": job.get("salary", job.get("payment", "Не указано")),
            "url": job.get("url", job.get("link", "")),
            "description": job.get("description", job.get("content", "")),
            "posted_at": job.get("posted_at", job.get("created_at", "")),
            "skills": job.get("skills", job.get("requirements", [])),
            "source": job.get("source", "cognitive-agent"),
        }

    async def close(self):
        """Закрытие HTTP-клиента."""
        await self._client.aclose()

    async def __aenter__(self):
        """Асинхронный контекстный менеджер: вход."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Асинхронный контекстный менеджер: выход."""
        await self.close()


# Синхронная обёртка для случаев, когда асинхронный код недоступен
class CognitiveJobSearchSync:
    """Синхронная версия адаптера для использования в синхронном коде."""

    def __init__(self, base_url: str | None = None, timeout: float = 30.0):
        self._async_adapter = CognitiveJobSearch(base_url=base_url, timeout=timeout)

    def search(self, query: str, **kwargs: Any) -> list[dict[str, Any]]:
        """Синхронный поиск вакансий."""
        import asyncio

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(self._async_adapter.search(query, **kwargs))

    def get_details(self, job_id: str) -> dict[str, Any]:
        """Синхронное получение деталей вакансии."""
        import asyncio

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(self._async_adapter.get_details(job_id))
