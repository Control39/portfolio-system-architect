"""
Portfolio Organizer — Entry Point

Автоматический сбор доказательств компетенций и картирование навыков.
FastAPI приложение для управления портфолио.
"""

import os
import sys
from pathlib import Path

# Добавляем корень проекта в PATH
REPO_ROOT = Path(__file__).parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Интеграция с AI Config Manager
try:
    from apps.portfolio_organizer.src.config_integration import get_config
    AI_CONFIG_AVAILABLE = True
    config_manager = get_config()
    po_config = config_manager.get_config()
    print("✅ Portfolio Organizer: использован AI Config Manager")
except Exception as e:
    AI_CONFIG_AVAILABLE = False
    print(f"⚠️  Portfolio Organizer: AI Config Manager недоступен ({e}), используется локальный конфиг")
    po_config = {}

from fastapi import FastAPI

app = FastAPI(
    title="Portfolio Organizer",
    description="Автоматический сбор доказательств компетенций",
    version="1.0.0",
    docs_url="/docs",
)


@app.get("/")
async def root():
    return {
        "service": "Portfolio Organizer",
        "version": "1.0.0",
        "endpoints": {
            "GET /portfolio": "Получить портфолио",
            "POST /portfolio/evidence": "Добавить доказательство",
            "GET /portfolio/analysis": "Анализ портфолио",
            "GET /health": "Health check",
        },
    }


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "portfolio-organizer"}


if __name__ == "__main__":
    import uvicorn
    
    port = 8004
    if po_config:
        port = po_config.get('portfolio_organizer', {}).get('port', 8004)
    
    uvicorn.run(app, host="0.0.0.0", port=port)
