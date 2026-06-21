#!/usr/bin/env python3
"""
Простая проверка состояния окружения
"""

import sys
from pathlib import Path

print("🔍 Проверка состояния окружения...")
print(f"Python executable: {sys.executable}")
print(f"Python path: {sys.path[0]}")

# Проверяем, активировано ли виртуальное окружение
is_venv = "venv" in sys.executable or ".venv" in sys.executable
print(f"Virtual environment active: {is_venv}")

# Проверяем наличие ключевых пакетов
try:
    import fastapi

    print(f"✅ FastAPI установлен: {fastapi.__version__}")
except ImportError:
    print("❌ FastAPI не установлен")

try:
    import yaml

    print("✅ PyYAML установлен")
except ImportError:
    print("❌ PyYAML не установлен")

try:
    import requests

    print("✅ Requests установлен")
except ImportError:
    print("❌ Requests не установлен")

# Проверяем структуру проекта
repo_root = Path(__file__).parent.parent
print(f"\n📁 Проверка структуры проекта в: {repo_root}")

dirs_to_check = ["agents/cognitive_agent", "apps", "src", "config"]

for dir_path in dirs_to_check:
    full_path = repo_root / dir_path
    if full_path.exists():
        print(f"✅ {dir_path}: существует")
    else:
        print(f"❌ {dir_path}: НЕ СУЩЕСТВУЕТ")

# Проверяем конфигурацию агента
agent_config = repo_root / "agents" / "cognitive_agent" / "config" / "guardrails.yaml"
if agent_config.exists():
    print("✅ Конфигурация агента: существует")
else:
    print("❌ Конфигурация агента: НЕ СУЩЕСТВУЕТ")

print("\n✅ Проверка завершена")
