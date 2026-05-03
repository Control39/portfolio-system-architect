from typing import Dict, List

import requests


async def search_hh_ru(query: str, area: str = "1") -> List[Dict]:
    """Парсер hh.ru API."""
    url = f"https://api.hh.ru/vacancies?text={query}&area={area}&per_page=10"
    try:
        response = requests.get(url, timeout=10)
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
    except Exception as e:
        print(f"Error fetching vacancies: {e}")
        return []
