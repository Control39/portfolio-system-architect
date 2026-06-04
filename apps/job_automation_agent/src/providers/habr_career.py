"""
Интеграция с Habr Career API

Документация: https://habr.com/ru/company/habr/blog/435060/
"""

import asyncio
from typing import List, Dict, Any
import requests

ALLOWED_HOSTS = {
    "career.habr.com",
    "api.habr.com",
}


class HabrCareerProvider:
    """Провайдер вакансий с Habr Career"""

    def __init__(self):
        self.base_url = "https://career.habr.com"
        self.api_url = "https://api.habr.com/v1/jobs"

    async def search(self, query: str, per_page: int = 20, page: int = 0) -> List[Dict[str, Any]]:
        """
        Поиск вакансий на Habr Career

        Args:
            query: Строка поиска
            per_page: Количество вакансий на странице
            page: Номер страницы

        Returns:
            Список вакансий
        """
        # Используем публичный API (без ключа, ограниченный)
        url = f"{self.base_url}/search.json"
        params = {"q": query, "page": page, "per_page": per_page}

        headers = {"User-Agent": "JobAutomationAgent/1.0", "Accept": "application/json"}

        try:
            response = requests.get(url, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()

            vacancies = data.get("vacancies", [])
            return self._parse_vacancies(vacancies)

        except requests.RequestException as e:
            print(f"❌ Ошибка запроса к Habr Career: {e}")
            return []

        except Exception as e:
            print(f"❌ Ошибка парсинга: {e}")
            return []

    def _parse_vacancies(self, vacancies: List[Dict]) -> List[Dict[str, Any]]:
        """Парсинг вакансий из ответа Habr Career"""
        parsed = []

        for v in vacancies:
            parsed.append(
                {
                    "id": v.get("id"),
                    "name": v.get("name"),
                    "employer": v.get("company", {}).get("name", "Не указано"),
                    "salary": v.get("salary_formatted"),
                    "url": f"https://career.habr.com/vacancies/{v.get('id')}",
                    "experience": v.get("experience", {}).get("name"),
                    "employment": v.get("employment", {}).get("name"),
                    "schedule": v.get("schedule", {}).get("name"),
                    "address": v.get("city", {}).get("name"),
                    "requirements": v.get("description", "")[:200],
                    "source": "habr_career",
                }
            )

        return parsed


async def search_habr_career(query: str, per_page: int = 20) -> List[Dict[str, Any]]:
    """Удобная функция для поиска на Habr Career"""
    provider = HabrCareerProvider()
    return await provider.search(query, per_page)


if __name__ == "__main__":
    # Тестовый запуск
    async def test():
        results = await search_habr_career("архитектор системный")
        print(f"🔍 Найдено вакансий: {len(results)}")

        for i, v in enumerate(results[:5], 1):
            print(f"\n{i}. {v['name']} @ {v['employer']}")
            print(f"   Зарплата: {v['salary'] or 'Не указана'}")
            print(f"   URL: {v['url']}")

    asyncio.run(test())
