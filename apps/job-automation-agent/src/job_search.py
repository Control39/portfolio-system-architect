import asyncio
from typing import Dict, List

import requests


async def search_hh_ru(query: str, area: str = "1") -> List[Dict]:
    """Парсер hh.ru API."""
    url = f"https://api.hh.ru/vacancies?text={query}&area={area}&per_page=10"
    headers = {"User-Agent": "JobAutomationAgent/1.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        vacancies = data.get("items", [])
        return [
            {
                "id": v.get("id"),
                "name": v.get("name"),
                "employer": v.get("employer", {}).get("name"),
                "salary": v.get("salary"),
                "url": v.get("alternate_url"),
            }
            for v in vacancies
        ]
    except requests.RequestException as e:
        print(f"Ошибка запроса к hh.ru: {e}")
        return []


async def search_habr_career(query: str) -> List[Dict]:
    """Поиск вакансий на Хабр Карьере (упрощённый)."""
    # Заглушка
    return [
        {
            "id": "1",
            "name": f"{query} разработчик",
            "employer": "Компания Х",
            "salary": "от 150 000 руб.",
            "url": "https://career.habr.com/vacancies/1",
        }
    ]


async def search_all_jobs(query: str) -> List[Dict]:
    """Объединённый поиск по всем источникам."""
    hh_results = await search_hh_ru(query)
    habr_results = await search_habr_career(query)
    return hh_results + habr_results


if __name__ == "__main__":
    # Тестовый запуск
    results = asyncio.run(search_all_jobs("Python"))
    print(f"Найдено вакансий: {len(results)}")
    for v in results[:3]:
        print(f"- {v['name']} ({v['employer']})")
