"""
Career Development API entry point for uvicorn.
"""

import sys
from pathlib import Path

# Добавляем корень проекта в PATH
REPO_ROOT = Path(__file__).parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Интеграция с AI Config Manager
try:
    from apps.career_development.src.config_integration import get_config

    AI_CONFIG_AVAILABLE = True
    config_manager = get_config()
    career_config = config_manager.get_config()
    print("✅ Career Development: использован AI Config Manager")
except Exception as e:
    AI_CONFIG_AVAILABLE = False
    print(f"⚠️  Career Development: AI Config Manager недоступен ({e}), используется локальный конфиг")
    career_config = {}

# Добавляем путь к корню проекта (src уже в /app/src благодаря Dockerfile)

from api.app import app

__all__ = ["app"]
