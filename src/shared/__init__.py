"""Shared - общие модули и утилиты проекта.

Содержит общие компоненты, используемые различными модулями системы:
- LLM интеграции
- Pydantic схемы
- Утилиты и хелперы
"""

__version__ = "0.1.0"
__all__ = ["llm", "pydantic", "schemas"]

# Реэкспорт основных компонентов
try:
    from .llm.yandex_gpt import YandexGPTClient
    __all__.append("YandexGPTClient")
except ImportError:
    pass
