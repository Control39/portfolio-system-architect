"""
Загрузчик конфигурации (обратная совместимость).

Этот модуль предоставляет обратную совместимость для импорта
`from .config.loader import COMPONENT_CONFIG`.
"""

import warnings
import sys
import os

# Добавляем путь для импорта decision_engine
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from decision_engine.decision_engine.configs.loader import COMPONENT_CONFIG
    from decision_engine.decision_engine.configs.loader import load_component_config
except ImportError:
    warnings.warn(
        "Не удалось импортировать decision_engine.decision_engine.configs.loader. "
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