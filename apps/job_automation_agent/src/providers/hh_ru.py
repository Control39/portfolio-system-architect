"""
Интеграция с hh.ru API

Документация: https://api.hh.ru
"""

import asyncio
from typing import Any

import requests

from ..utils.security import sanitize_error_message

ALLOWED_HOSTS = {
    "api.hh.ru",
    "hh.ru",
}


class HHruProvider:
    """Провайдер вакансий с hh.ru"""

    def __init__(self):
        self.base_url = "https://api.hh.ru"
        self.area_moscow = "1"  # Москва
        self.area_spb = "2"  # Санкт-Петербург
        self.area_russia = "113"  # Россия

    async def search(self, query: str, area: str = "113", per_page: int = 20, pages: int = 1) -> list[dict[str, Any]]:
        """
        Поиск вакансий на hh.ru

        Args:
            query: Строка поиска (например, "Python разработчик")
            area: ID региона (1=Москва, 2=СПб, 113=Россия)
            per_page: Количество вакансий на странице (макс. 100)
            pages: Количество страниц для поиска

        Returns:
            Список вакансий
        """
        all_vacancies = []

        for page in range(pages):
            url = f"{self.base_url}/vacancies"
            params = {"text": query, "area": area, "per_page": per_page, "page": page}

            headers = {
                "User-Agent": "JobAutomationAgent/1.0 (ekaterina.kudelya@example.com)",
                "Accept": "application/json",
            }

            # Примечание: Для полноценной работы нужна регистрация приложения на https://dev.hh.ru/
            # Публичный API работает без токена, но с ограничениями

            try:
                response = requests.get(url, params=params, headers=headers, timeout=30)
                response.raise_for_status()
                data = response.json()

                vacancies = data.get("items", [])
                all_vacancies.extend(self._parse_vacancies(vacancies))

                if len(vacancies) < per_page:
                    break  # Больше вакансий нет

            except requests.RequestException as e:
                safe_message = sanitize_error_message(e, url)
                print(f"❌ Ошибка запроса к hh.ru: {safe_message}")
                break

        return all_vacancies

    def _parse_vacancies(self, vacancies: list[dict]) -> list[dict[str, Any]]:
        """Парсинг вакансий из ответа hh.ru"""
        parsed = []

        for v in vacancies:
            salary = v.get("salary")
            salary_str = None
            if salary:
                salary_from = salary.get("from")
                salary_to = salary.get("to")
                currency = salary.get("currency", "RUB")

                if salary_from and salary_to:
                    salary_str = f"{salary_from:,} - {salary_to:,} {currency}"
                elif salary_from:
                    salary_str = f"от {salary_from:,} {currency}"
                elif salary_to:
                    salary_str = f"до {salary_to:,} {currency}"

            parsed.append(
                {
                    "id": v.get("id"),
                    "name": v.get("name"),
                    "employer": v.get("employer", {}).get("name", "Не указано"),
                    "salary": salary_str,
                    "url": v.get("alternate_url"),
                    "description_url": v.get("alternate_url"),  # Ссылка на описание
                    "experience": v.get("experience", {}).get("name"),
                    "employment": v.get("employment", {}).get("name"),
                    "schedule": v.get("schedule", {}).get("name"),
                    "address": v.get("address", {}).get("region", {}).get("name") if v.get("address") else None,
                    "requirements": v.get("snippet", {}).get("requirement", "")[:200],  # Первые 200 символов
                    "source": "hh.ru",
                }
            )

        return parsed

    def get_areas(self) -> dict[str, str]:
        """Получить список регионов"""
        return {
            "1": "Москва",
            "2": "Санкт-Петербург",
            "113": "Россия",
            "84": "Новосибирск",
            "87": "Екатеринбург",
            "40": "Казань",
            "53": "Нижний Новгород",
            "12": "Самара",
            "11": "Уфа",
            "14": "Челябинск",
        }


async def search_hh_ru(query: str, area: str = "113", per_page: int = 20, pages: int = 1) -> list[dict[str, Any]]:
    """Удобная функция для поиска на hh.ru"""
    provider = HHruProvider()
    return await provider.search(query, area, per_page, pages)


if __name__ == "__main__":
    # Тестовый запуск
    async def test():
        results = await search_hh_ru("Python", pages=1)
        print(f"🔍 Найдено вакансий: {len(results)}")

        for i, v in enumerate(results[:5], 1):
            print(f"\n{i}. {v['name']} @ {v['employer']}")
            print(f"   Зарплата: {v['salary'] or 'Не указана'}")
            print(f"   Опыт: {v['experience'] or 'Не указано'}")
            print(f"   URL: {v['url']}")

    asyncio.run(test())
