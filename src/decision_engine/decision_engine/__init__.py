"""
Cloud Reason - модуль облачных вычислений и интеграций.

Содержит инструменты для работы с облачными провайдерами,
оркестрации контейнеров и управления инфраструктурой.
"""

__version__ = "0.1.0"
__all__ = ["configs", "core", "utils", "main", "__version__"]

# Реэкспорт основных компонентов
try:
    from .configs.loader import COMPONENT_CONFIG, load_component_config
except ImportError:
    # Fallback конфигурация
    COMPONENT_CONFIG = {
        "automation": {
            "scripts": [
                {
                    "name": "run_api",
                    "command": "uvicorn api.endpoints:app --host 0.0.0.0 --port 8000 --reload",
                }
            ]
        }
    }

    def load_component_config():
        return COMPONENT_CONFIG


from .main import run_server

__all__ += ["COMPONENT_CONFIG", "load_component_config", "run_server"]
