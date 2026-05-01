"""
Unit tests for the configuration module.

Tests the config.loader module and its fallback mechanisms.
"""

import os
import sys
import warnings
from unittest.mock import patch

# Добавляем путь к src для импорта модулей
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def test_component_config_import_from_decision_engine():
    """
    Test that COMPONENT_CONFIG is correctly imported from decision_engine.configs.loader
    when the module is available.
    """
    # Создаем мок для модуля decision_engine.configs.loader
    mock_loader_module = type(sys)("decision_engine.configs.loader")
    mock_loader_module.COMPONENT_CONFIG = {"test": "value"}
    mock_loader_module.load_component_config = lambda: {"test": "value"}

    # Патчим sys.modules, чтобы вставить наш мок
    with patch.dict(sys.modules, {"decision_engine.configs.loader": mock_loader_module}):
        # Удаляем кэшированный модуль src.config.loader, если он есть
        if "src.config.loader" in sys.modules:
            del sys.modules["src.config.loader"]
        # Импортируем модуль
        from src.config.loader import COMPONENT_CONFIG

        # Проверяем, что конфиг взят из мока, а не из fallback
        assert COMPONENT_CONFIG == {"test": "value"}
        # Проверяем, что конфиг не является fallback-конфигом
        assert COMPONENT_CONFIG != {
            "automation": {
                "scripts": [
                    {
                        "name": "run_api",
                        "command": "uvicorn api.endpoints:app --host 0.0.0.0 --port 8000 --reload",
                    }
                ]
            }
        }


def test_component_config_fallback_when_decision_engine_missing():
    """
    Test that a fallback COMPONENT_CONFIG is created
    when decision_engine.configs.loader is not available.
    """
    # Удаляем decision_engine.configs.loader из sys.modules, если он там есть
    if "decision_engine.configs.loader" in sys.modules:
        del sys.modules["decision_engine.configs.loader"]

    # Удаляем src.config.loader из sys.modules, чтобы гарантировать повторный импорт
    if "src.config.loader" in sys.modules:
        del sys.modules["src.config.loader"]

    # Подавляем предупреждения, чтобы не засорять вывод
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        # Импортируем модуль
        from src.config.loader import COMPONENT_CONFIG

        # Проверяем, что используется fallback-конфиг
        assert COMPONENT_CONFIG == {
            "automation": {
                "scripts": [
                    {
                        "name": "run_api",
                        "command": "uvicorn api.endpoints:app --host 0.0.0.0 --port 8000 --reload",
                    }
                ]
            }
        }


def test_load_component_config_fallback():
    """
    Test that the load_component_config function returns the fallback configuration.
    """
    # Удаляем decision_engine.configs.loader из sys.modules
    if "decision_engine.configs.loader" in sys.modules:
        del sys.modules["decision_engine.configs.loader"]

    # Удаляем src.config.loader из sys.modules
    if "src.config.loader" in sys.modules:
        del sys.modules["src.config.loader"]

    # Подавляем предупреждения
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        # Импортируем функцию
        from src.config.loader import load_component_config

        # Вызываем функцию и проверяем результат
        config = load_component_config()
        assert config == {
            "automation": {
                "scripts": [
                    {
                        "name": "run_api",
                        "command": "uvicorn api.endpoints:app --host 0.0.0.0 --port 8000 --reload",
                    }
                ]
            }
        }
