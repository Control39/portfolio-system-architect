from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import json
import os
import sys

# Добавляем путь для импорта общих модулей
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")))
from src.common.health_check import init_health_checks

app = FastAPI(title="Career Development System API", version="1.0.0")

# Инициализируем health-check
init_health_checks(app, service_name="career-development", version="1.0.0")

# Путь к файлу профиля (пример)
PROFILE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "user_profile.json")
)


@app.get("/")
async def root():
    return {
        "message": "Career Development System API is running",
        "version": "1.0.0",
        "endpoints": {
            "GET /health": "Health check",
            "GET /ready": "Readiness probe",
            "GET /live": "Liveness probe",
            "GET /profile": "Get user profile",
        }
    }


@app.get("/profile")
async def get_profile():
    """Вернуть JSON‑профиль пользователя."""
    if not os.path.exists(PROFILE_PATH):
        raise HTTPException(status_code=404, detail="Profile not found")
    with open(PROFILE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


# ------------------- Пример простых моделей -------------------
class GoalCreate(BaseModel):
    title: str
    description: Optional[str] = None
    target_date: Optional[str] = None  # ISO‑date


@app.post("/goals")
async def create_goal(goal: GoalCreate):
    """Создаёт новую цель в профиле."""
    if not os.path.exists(PROFILE_PATH):
        raise HTTPException(status_code=404, detail="Profile not found")
    with open(PROFILE_PATH, "r", encoding="utf-8") as f:
        profile = json.load(f)

    profile.setdefault("goals", []).append(goal.dict())
    with open(PROFILE_PATH, "w", encoding="utf-8") as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)

    return {"status": "created", "goal": goal}


@app.patch("/markers/{marker_id}")
async def update_marker(marker_id: str, status: str):
    """Обновление статуса маркера (not_started, in_progress, completed)."""
    if not os.path.exists(PROFILE_PATH):
        raise HTTPException(status_code=404, detail="Profile not found")
    with open(PROFILE_PATH, "r", encoding="utf-8") as f:
        profile = json.load(f)

    # поиск маркера
    for skill in profile.get("skills", []):
        for marker in skill.get("markers", []):
            if marker["id"] == marker_id:
                marker["status"] = status
                break

    with open(PROFILE_PATH, "w", encoding="utf-8") as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)

    return {"status": "updated", "marker_id": marker_id, "new_status": status}


@app.get("/evidence/export")
async def export_evidence():
    """Сгенерировать пакет доказательств. Для демо – просто возвращаем путь к файлу."""
    # В реальном проекте сюда будет логика сборки PDF/MD.
    return {"export_path": "/path/to/evidence_package.zip"}


