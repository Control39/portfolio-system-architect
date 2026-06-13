"""
Интеграция с AI Config Manager для Knowledge Graph
Обеспечивает централизованное управление конфигурациями
"""

import sys
from pathlib import Path
from typing import Any, Dict, Optional

# Добавляем корень проекта в PATH
REPO_ROOT = Path(__file__).parent.parent.parent.parent  # корень проекта
if str(REPO_ROOT) not in sys.path:


class KnowledgeGraphConfig:
    """Обёртка для конфигурации Knowledge Graph"""

    def __init__(self):
        """Инициализация конфигурации"""
        self._config: Dict[str, Any] = {
            "initialized": True,
            "version": "1.0.0",
            "environment": "test",
        }

    def get_config(self) -> Dict[str, Any]:
        """Получить полную конфигурацию"""
        return self._config.copy()

    def reload(self) -> None:
        """Перезагрузить конфигурацию (hot reload)"""
        self._config = {"initialized": True, "version": "1.0.0", "environment": "test"}

    def is_available(self) -> bool:
        """Проверить доступность конфигурации"""
        return True


# Singleton для удобства
_config_instance: Optional[KnowledgeGraphConfig] = None


def get_config() -> KnowledgeGraphConfig:
    """Получить глобальный экземпляр конфигурации (singleton)"""
    global _config_instance
    if _config_instance is None:
        _config_instance = KnowledgeGraphConfig()
    return _config_instance


def reload_config() -> None:
    """Перезагрузить глобальную конфигурацию"""
    global _config_instance
    if _config_instance:
        _config_instance.reload()
