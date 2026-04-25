"""
Конфигурационный модуль проекта.

Содержит загрузчики конфигурации, утилиты для работы с настройками
и глобальные константы конфигурации.
"""

__all__ = []

# Реэкспорт для обратной совместимости
try:
    from ..decision_engine.decision_engine.configs.loader import COMPONENT_CONFIG
    __all__.append('COMPONENT_CONFIG')
except ImportError:
    # Fallback конфигурация
    COMPONENT_CONFIG = {
        "automation": {
            "scripts": [
                {
                    "name": "run_api",
                    "command": "uvicorn api.endpoints:app --host 0.0.0.0 --port 8000 --reload"
                }
            ]
        }
    }
    __all__.append('COMPONENT_CONFIG')