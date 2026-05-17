"""
Интеграция с AI Config Manager для Decision Engine
Обеспечивает централизованное управление конфигурациями
"""

import sys
from pathlib import Path
from typing import Any


# Добавляем корень проекта в PATH
REPO_ROOT = Path(__file__).parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

try:
    from apps.ai_config_manager.src.config_manager import ConfigManager

    AI_CONFIG_AVAILABLE = True
except ImportError:
    AI_CONFIG_AVAILABLE = False
    print("⚠️  AI Config Manager не доступен, используется локальная конфигурация")


class DecisionEngineConfig:
    """Обёртка для конфигурации Decision Engine через AI Config Manager"""

    def __init__(self, config_path: str | None = None):
        """
        Инициализация конфигурации

        Args:
            config_path: Путь к файлу конфигурации (по умолчанию: config/ai-config.yaml)
        """
        self.config_path = config_path or str(REPO_ROOT / "config" / "ai-config.yaml")
        self._config_manager: ConfigManager | None = None
        self._local_config: dict[str, Any] | None = None

        if AI_CONFIG_AVAILABLE:
            self._init_config_manager()
        else:
            self._load_local_config()

    def _init_config_manager(self) -> None:
        """Инициализация ConfigManager"""
        try:
            self._config_manager = ConfigManager(config_path=self.config_path)
            if not self._config_manager.validate():
                print("⚠️  Конфигурация не валидна, используется fallback")
                self._load_local_config()
        except Exception as e:
            print(f"⚠️  Ошибка инициализации ConfigManager: {e}")
            self._load_local_config()

    def _load_local_config(self) -> None:
        """Загрузка локальной конфигурации (fallback)"""
        import yaml

        local_config_path = REPO_ROOT / "apps" / "decision_engine" / "config" / "config.yaml"

        if local_config_path.exists():
            with open(local_config_path, encoding="utf-8") as f:
                self._local_config = yaml.safe_load(f)
        else:
            self._local_config = {}

    def get_config(self) -> dict[str, Any]:
        """Получить полную конфигурацию"""
        if self._config_manager:
            try:
                return self._config_manager.get_agent_config("decision_engine")
            except Exception:
                return self._local_config or {}
        return self._local_config or {}

    def reload(self) -> None:
        """Перезагрузить конфигурацию (hot reload)"""
        if self._config_manager:
            self._config_manager.reload()
        else:
            self._load_local_config()

    def is_available(self) -> bool:
        """Проверить доступность AI Config Manager"""
        return AI_CONFIG_AVAILABLE and self._config_manager is not None


# Singleton для удобства
_config_instance: DecisionEngineConfig | None = None


def get_config() -> DecisionEngineConfig:
    """Получить глобальный экземпляр конфигурации"""
    global _config_instance
    if _config_instance is None:
        _config_instance = DecisionEngineConfig()
    return _config_instance


def reload_config() -> None:
    """Перезагрузить глобальную конфигурацию"""
    global _config_instance
    if _config_instance:
        _config_instance.reload()
