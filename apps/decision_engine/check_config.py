#!/usr/bin/env python3
"""Проверка загрузки конфигурации decision_engine"""

import sys
from pathlib import Path

# Добавляем корень проекта в PATH
REPO_ROOT = Path(__file__).parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from apps.decision_engine.src.config_integration import get_config

config = get_config()
print(f"AI Config Manager доступен: {config.is_available()}")
print(f"Получена конфигурация: {bool(config.get_config())}")
print(f"Ключи конфигурации: {list(config.get_config().keys()) if config.get_config() else 'Пусто'}")
