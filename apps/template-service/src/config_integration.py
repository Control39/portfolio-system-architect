"""Интеграция с AI Config Manager для Template Service"""

import sys
from pathlib import Path
from typing import Any

# Добавляем корень проекта в PATH
REPO_ROOT = Path(__file__).parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


class TemplateConfig:
    """Конфигурация Template Service"""

    def __init__(self, config_path: str | None = None):
        """
        Инициализация конфигурации

        Args:
            config_path: Путь к файлу конфигурации (по умолчанию: config/ai-config.yaml)
        """
        self.config_path = config_path or str(REPO_ROOT / "config" / "ai-config.yaml")
        self._config: dict[str, Any] = {}
        self._load_config()

    def _load_config(self) -> None:
        """Загрузка конфигурации"""
        import yaml

        if Path(self.config_path).exists():
            with open(self.config_path, encoding="utf-8") as f:
                full_config = yaml.safe_load(f)
                self._config = full_config.get("services", {}).get("template-service", {})
        else:
            self._config = {}

    def get_config(self) -> dict[str, Any]:
        """Получить конфигурацию"""
        return self._config

    def reload(self) -> None:
        """Перезагрузить конфигурацию"""
        self._load_config()


# Singleton
_config_instance: TemplateConfig | None = None


def get_config() -> TemplateConfig:
    """Получить глобальный экземпляр конфигурации"""
    global _config_instance
    if _config_instance is None:
        _config_instance = TemplateConfig()
    return _config_instance
