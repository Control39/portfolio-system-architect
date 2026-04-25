import requests
from typing import List, Dict
import asyncio

async def search_hh_ru(query: str, area: str = "1") -> List[Dict]:
    """Парсер hh.ru API."""
    url = f"https://api.hh.ru/vacancies?text={query}&area={area}&per_page

