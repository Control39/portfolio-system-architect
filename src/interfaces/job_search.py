"""
Интерфейс для поиска вакансий (Job Search)

Этот интерфейс определяет контракт, который должны выполнять
все реализации поиска вакансий (cognitive_agent, external API, и т.д.).

Принципы:
- Абстракция не зависит от деталей реализации
- Легкая замена одной реализации на другую
- Тестируемость через mock-объекты
"""

from abc import ABC, abstractmethod
from typing import Any


class IJobSearch(ABC):
    """Абстрактный интерфейс для поиска вакансий."""

    @abstractmethod
    def search(self, query: str, **kwargs: Any) -> list[dict[str, Any]]:
        """
        Поиск вакансий по запросу.

        Аргументы:
            query: Строка запроса (например, "Python Developer")
            **kwargs: Дополнительные параметры (локация, опыт, зарплата и т.д.)

        Возвращает:
            Список словарей с данными вакансий. Каждый словарь содержит:
            - title: Название вакансии
            - company: Название компании
            - location: Локация
            - salary: Зарплата (опционально)
            - url: Ссылка на вакансию
            - description: Описание (опционально)
            - posted_at: Дата публикации (опционально)

        Пример:
            >>> search_engine = CognitiveJobSearch()
            >>> results = search_engine.search("Python Developer", location="Москва")
            >>> for job in results:
            ...     print(f"{job['title']} at {job['company']}")
        """
        pass

    @abstractmethod
    def get_details(self, job_id: str) -> dict[str, Any]:
        """
        Получение подробной информации о вакансии.

        Аргументы:
            job_id: Уникальный идентификатор вакансии

        Возвращает:
            Словарь с полной информацией о вакансии

        Пример:
            >>> search_engine = CognitiveJobSearch()
            >>> details = search_engine.get_details("hh-12345")
            >>> print(details['description'])
        """
        pass
