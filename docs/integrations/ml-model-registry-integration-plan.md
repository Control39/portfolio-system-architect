# План интеграции ML Model Registry с Portfolio Organizer

## Цель
Интегрировать компонент ML Model Registry в основную экосистему портфолио, чтобы зарегистрированные модели отображались как проекты/артефакты в Portfolio Organizer и могли быть рекомендованы на основе метрик.

## Текущее состояние
- ML Model Registry — это отдельный компонент с базовым API (FastAPI) и классом ModelRegistry.
- Portfolio Organizer — демонстрационный API, который показывает примеры проектов.
- Оба компонента находятся в одной монолитной структуре (папка `components/`), но не связаны.

## Шаги интеграции

### 1. Расширение API ML Model Registry
Добавить эндпоинты для получения данных в формате, совместимом с Portfolio Organizer.

**Команды:**
```bash
# Перейти в папку компонента
cd apps/ml-model-registry

# Создать новый файл эндпоинтов
touch apps/ml-model-registry/src/api/portfolio_integration.py

# Редактировать main.py для подключения новых маршрутов
```

**Содержимое `portfolio_integration.py`:**
```python
from fastapi import APIRouter
from ..core.model_registry import ModelRegistry

router = APIRouter(prefix="/portfolio", tags=["portfolio"])
registry = ModelRegistry()

@router.get("/models")
async def get_models_for_portfolio():
    """Возвращает список моделей в формате, ожидаемом Portfolio Organizer."""
    models = registry.list_models()
    formatted = []
    for model_id in models:
        data = registry.get_model(model_id)
        formatted.append({
            "id": model_id,
            "name": data.get("name", model_id),
            "type": "ml_model",
            "metrics": data.get("metrics", {}),
            "version": data.get("version", "1.0"),
            "description": data.get("description", ""),
            "created_at": data.get("created_at", ""),
            "tags": data.get("tags", [])
        })
    return {"models": formatted}
```

**Обновить `main.py`:**
```python
from fastapi import FastAPI
from .api.portfolio_integration import router as portfolio_router

app = FastAPI(title="ML Model Registry API", version="0.1.0")
app.include_router(portfolio_router)

@app.get("/")
async def root():
    return {"message": "ML Model Registry API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 2. Добавление эндпоинта в Portfolio Organizer
Создать эндпоинт, который запрашивает данные из ML Model Registry и объединяет их с существующими проектами.

**Команды:**
```bash
cd apps/portfolio_organizer

# Создать файл интеграции
touch apps/portfolio_organizer/src/integration/ml_model_registry.py

# Обновить основной API
```

**Содержимое `ml_model_registry.py`:**
```python
import httpx
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/integrations", tags=["integrations"])
ML_REGISTRY_URL = "http://localhost:8000/portfolio/models"

@router.get("/ml-models")
async def get_ml_models():
    """Получает модели из ML Model Registry."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(ML_REGISTRY_URL, timeout=5.0)
            response.raise_for_status()
            return response.json()
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"ML Registry unavailable: {e}")
```

**Обновить `src/api/main.py` Portfolio Organizer, чтобы включить этот роутер.**

### 3. Обновление документации
Добавить описание интеграции в `ARCHITECTURE.md` и `component_versions_map.md`.

**Команды:**
```bash
# Обновить ARCHITECTURE.md (уже сделано)
# Обновить component_versions_map.md (уже сделано)

# Создать краткий гайд по интеграции
touch docs/integrations/ml-model-registry.md
```

### 4. Запуск тестов
Убедиться, что изменения не ломают существующие тесты.

**Команды:**
```bash
# В ML Model Registry
cd apps/ml-model-registry
python -m pytest tests/ -v

# В Portfolio Organizer
cd apps/portfolio_organizer
python -m pytest tests/ -v
```

### 5. Запуск сервисов для проверки
**Команды:**
```bash
# В одном терминале запустить ML Model Registry
cd apps/ml-model-registry
uvicorn apps.ml-model-registry.src.api.main:app --reload --port 8000

# В другом терминале запустить Portfolio Organizer
cd apps/portfolio_organizer
uvicorn apps.portfolio_organizer.src.api.main:app --reload --port 8001

# Проверить эндпоинты
curl http://localhost:8000/portfolio/models
curl http://localhost:8001/integrations/ml-models
```

### 6. Коммит изменений
**Команды:**
```bash
# Добавить все изменения
git add .

# Коммит
git commit -m "feat: integrate ML Model Registry with Portfolio Organizer"

# Пуш (если нужно)
git push origin main
```

## Дополнительные улучшения (опционально)
- Добавить кэширование запросов к ML Registry.
- Реализовать рекомендации на основе метрик (например, модели с accuracy > 90% помечаются как "recommended").
- Создать дашборд в Portfolio Organizer для визуализации моделей.

## Примечания
- Все файлы должны быть написаны в сдержанном тоне, без пафоса.
- Код должен соответствовать существующим стандартам проекта.
- Интеграция должна быть минимально инвазивной.
