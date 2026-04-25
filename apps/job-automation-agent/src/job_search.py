


async def search_hh_ru(query: str, area: str = "1") -> list[dict]:
    """Парсер hh.ru API."""
    url = f"https://api.hh.ru/vacancies?text={query}&area={area}&per_page=10"


