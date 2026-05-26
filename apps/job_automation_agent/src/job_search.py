"""Job search с использованием централизованной SSRF-защиты."""

import asyncio
import os
from typing import List, Dict, Any

from .utils.security import is_safe_url, sanitize_error_message

# Импортируем провайдеры
from .providers.hh_ru import HHruProvider, search_hh_ru
from .providers.habr_career import HabrCareerProvider, search_habr_career

ALLOWED_HOSTS = {
    "localhost",
    "127.0.0.1",
    "api.hh.ru",
    "career.habr.com",
}


async def search_all_jobs(
    query: str,
    enable_hh: bool = True,
    enable_habr: bool = True,
    area: str = "113"  # Россия
) -> List[Dict[str, Any]]:
    """
    Объединённый поиск по всем источникам
    
    Args:
        query: Строка поиска (например, "Python архитектор системное мышление")
        enable_hh: Включить hh.ru
        enable_habr: Включить Habr Career
        area: Регион для hh.ru (113=Россия)
    
    Returns:
        Список вакансий со всех источников
    """
    results = []
    
    if enable_hh:
        print(f"🔍 Поиск на hh.ru...")
        hh_results = await search_hh_ru(query, area=area, pages=2)
        results.extend(hh_results)
        print(f"   Найдено: {len(hh_results)} вакансий")
    
    if enable_habr:
        print(f"🔍 Поиск на Habr Career...")
        habr_results = await search_habr_career(query)
        results.extend(habr_results)
        print(f"   Найдено: {len(habr_results)} вакансий")
    
    return results


if __name__ == "__main__":
    # Тестовый запуск
    results = asyncio.run(search_all_jobs("Python"))
    print(f"Найдено вакансий: {len(results)}")
    for v in results[:3]:
        print(f"- {v['name']} ({v['employer']})")
