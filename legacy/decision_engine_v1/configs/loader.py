# src/decision_engine/configs/loader.py
from pathlib import Path

import yaml


def load_component_config():
    """Загружает конфигурацию компонента из component-config.yaml в корне проекта."""
    project_root = Path(__file__).parent.parent.parent
    config_path = project_root / "component-config.yaml"

    if not config_path.exists():
        raise FileNotFoundError(f"Файл конфигурации не найден: {config_path}")

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        return config
    except yaml.YAMLError as e:
        # FIX B904: явно указываем причину исключения
        raise ValueError(f"Ошибка парсинга YAML: {e}") from e


# Глобальная переменная конфигурации
COMPONENT_CONFIG = load_component_config()
