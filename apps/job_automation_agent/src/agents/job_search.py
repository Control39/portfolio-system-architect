"""Job search agent с использованием централизованной SSRF-защиты."""

# Импорт функций из родительского пакета для обратной совместимости
from .job_search import search_hh_ru as _search_hh_ru

# Переименовываем для совместимости
search_hh_ru = _search_hh_ru

ALLOWED_HOSTS = {
    "localhost",
    "127.0.0.1",
    "api.hh.ru",
    "career.habr.com",
}
