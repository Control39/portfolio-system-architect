"""
Template Service — Entry Point

Шаблон для создания новых микросервисов.
FastAPI приложение с базовой структурой.
"""

import sys
from pathlib import Path

# Добавляем корень проекта в PATH
REPO_ROOT = Path(__file__).parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Интеграция с AI Config Manager
try:
    from apps.template_service.src.config_integration import get_config

    AI_CONFIG_AVAILABLE = True
    config_manager = get_config()
    template_config = config_manager.get_config()
    print("✅ Template Service: использован AI Config Manager")
except Exception as e:
    AI_CONFIG_AVAILABLE = False
    print(f"⚠️  Template Service: AI Config Manager недоступен ({e}), используется локальный конфиг")
    template_config = {}

from fastapi import FastAPI

app = FastAPI(
    title="Template Service",
    description="Шаблон для создания новых микросервисов",
    version="1.0.0",
    docs_url="/docs",
)


@app.get("/")
async def root():
    return {
        "service": "Template Service",
        "version": "1.0.0",
        "description": "Используйте этот шаблон для создания новых микросервисов",
        "endpoints": {
            "GET /health": "Health check",
        },
    }


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "template-service"}


if __name__ == "__main__":
    import uvicorn

    port = 8005
    if template_config:
        port = template_config.get("template_service", {}).get("port", 8005)

    uvicorn.run(app, host="0.0.0.0", port=port)
