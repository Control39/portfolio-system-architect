# components/cognitive-agent/api/endpoints.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import sys
from pathlib import Path

# Добавляем путь к корню проекта для импорта атомов
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.ai import GigaMCPBridge, GigaChainSettings
from src.shared.models import ScanRequest, ScanResponse, PlanRequest, PlanResponse

app = FastAPI(title="Cognitive Agent API", version="0.1.0")


# --- Endpoints ---
@app.get("/api/v1/status")
async def status():
    """Health check endpoint for Docker healthcheck"""
    return {"status": "healthy", "service": "cognitive-agent", "version": "0.1.0"}


@app.get("/health")
async def health():
    """Alternative health endpoint"""
    return {"status": "healthy"}


@app.get("/")
async def root():
    return {"message": "Cognitive Agent API", "version": "0.1.0"}


@app.post("/api/v1/scan", response_model=ScanResponse)
async def scan_project(request: ScanRequest):
    """Запустить сканирование проекта"""
    try:
        # TODO: Интегрировать scanner_main.py
        return ScanResponse(
            status="pending",
            files_found=0,
            languages_detected=[],
            message=f"Сканирование начато для: {request.project_path}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/plan", response_model=PlanResponse)
async def plan_tasks(request: PlanRequest):
    """Создать план задач"""
    try:
        # TODO: Интегрировать planner_main.py + AI
        return PlanResponse(
            tasks=[],
            estimated_duration=0,
            message=f"Планирование начато для целей: {request.goals}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/execute")
async def execute_task(task_id: str, skill_name: str):
    """Выполнить задачу через skill"""
    try:
        # TODO: Интегрировать выполнение skills
        return {
            "status": "pending",
            "task_id": task_id,
            "skill_name": skill_name,
            "message": f"Выполнение задачи: {task_id} через {skill_name}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/metrics")
async def get_metrics():
    """Получить метрики обучения"""
    try:
        # TODO: Интегрировать learning_main.py
        return {
            "total_tasks": 0,
            "successful_tasks": 0,
            "efficiency_score": 0.0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/skills")
async def list_skills():
    """Получить список доступных навыков"""
    # TODO: Сканировать scripts/ папку
    return {
        "skills": [
            {"name": "scanner", "description": "Сканирование проекта"},
            {"name": "planner", "description": "Планирование задач"},
            {"name": "learning", "description": "Сбор метрик"}
        ]
    }
