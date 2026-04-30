"""
Cloud Reason - модуль облачных вычислений и интеграций.

Содержит инструменты для работы с облачными провайдерами,
оркестрации контейнеров и управления инфраструктурой.
"""

__version__ = "0.1.0"
__all__ = ["configs", "core", "utils", "main"]

# Реэкспорт основных компонентов
from .configs.loader import COMPONENT_CONFIG, load_component_config
from .main import run_server

__all__ += ["COMPONENT_CONFIG", "load_component_config", "run_server"]
