"""
Загрузчик конфигурации (обратная совместимость).

Этот модуль предоставляет обратную совместимость для импорта
`from .config.loader import COMPONENT_CONFIG`.
"""

import warnings
import sys
import os

# Добавляем путь для импорта cloud_reason
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from cloud_reason.configs.loader import COMPONENT_CONFIG
    from cloud_reason.configs.loader import load_component_config
except ImportError:
    warnings.warn(
        "Не удалось импортировать cloud_reason.configs.loader. "
        "Используется fallback конфигурация.",
        ImportWarning
    )
    
    # Fallback конфигурация
    def load_component_config():
        """Заглушечная функция загрузки конфигурации."""
        return {
            "automation": {
                "scripts": [
                    {
                        "name": "run_api",
                        "command": "uvicorn api.endpoints:app --host 0.0.0.0 --port 8000 --reload"
                    }
                ]
            }
        }
    
    COMPONENT_CONFIG = load_component_config()

__all__ = ['COMPONENT_CONFIG', 'load_component_config']