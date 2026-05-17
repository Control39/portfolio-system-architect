"""
Infrastructure Orchestrator API entry point for uvicorn.
"""

import os
import sys
from pathlib import Path

# Добавляем корень проекта в PATH
REPO_ROOT = Path(__file__).parent.parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Интеграция с AI Config Manager
try:
    from apps.infra_orchestrator.src.config_integration import get_config
    AI_CONFIG_AVAILABLE = True
    config_manager = get_config()
    io_config = config_manager.get_config()
    print("✅ Infra Orchestrator: использован AI Config Manager")
except Exception as e:
    AI_CONFIG_AVAILABLE = False
    print(f"⚠️  Infra Orchestrator: AI Config Manager недоступен ({e}), используется локальный конфиг")
    io_config = {}

# Импортируем приложение
from src.api.app import app


__all__ = ["app"]
