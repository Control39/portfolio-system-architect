"""
ML Model Registry — Entry Point

Регистр версионированных ML-моделей с A/B тестированием и метаданными.
FastAPI приложение для управления моделями.
"""

import sys
from pathlib import Path

# Добавляем корень проекта в PATH
REPO_ROOT = Path(__file__).parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Интеграция с AI Config Manager
try:
    from apps.ml_model_registry.src.config_integration import get_config

    AI_CONFIG_AVAILABLE = True
    config_manager = get_config()
    registry_config = config_manager.get_config()
    print("✅ ML Model Registry: использован AI Config Manager")
except Exception as e:
    AI_CONFIG_AVAILABLE = False
    print(f"⚠️  ML Model Registry: AI Config Manager недоступен ({e}), используется локальный конфиг")
    registry_config = {}

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="ML Model Registry",
    description="Регистр версионированных ML-моделей с A/B тестированием",
    version="1.0.0",
    docs_url="/docs",
)


class ModelMetadata(BaseModel):
    name: str
    version: str
    framework: str
    metrics: dict


@app.get("/")
async def root():
    return {
        "service": "ML Model Registry",
        "version": "1.0.0",
        "endpoints": {
            "POST /models": "Регистрация новой модели",
            "GET /models": "Список моделей",
            "GET /models/{name}/versions": "Версии модели",
            "POST /models/{name}/deploy": "Деплой модели",
            "GET /health": "Health check",
        },
    }


@app.post("/models")
async def register_model(metadata: ModelMetadata):
    """Регистрация новой модели"""
    # TODO: Реализовать сохранение в БД
    return {"status": "registered", "model": metadata.dict()}


@app.get("/models")
async def list_models():
    """Список всех моделей"""
    # TODO: Реализовать чтение из БД
    return {"models": []}


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "ml-model-registry"}


if __name__ == "__main__":
    import uvicorn

    port = 8003
    if registry_config:
        port = registry_config.get("ml_model_registry", {}).get("port", 8003)

    uvicorn.run(app, host="0.0.0.0", port=port)
