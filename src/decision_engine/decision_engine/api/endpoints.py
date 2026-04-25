# components/decision-engine/api/endpoints.py
import os
import sys
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Импортируем общие модули
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
from src.common.health_check import init_health_checks

app = FastAPI(title="Decision Engine API")

class ReasonRequest(BaseModel):
    repo: str
    query: str = ""

# Инициализируем health-check эндпоинты
init_health_checks(app, service_name="decision-engine", version="1.0.0")

@app.get("/")
async def root():
    return {
        "service": "Decision Engine API",
        "version": "1.0.0",
        "endpoints": {
            "POST /reason": "Analyze code repository and answer question",
            "GET /health": "Health check",
            "GET /ready": "Readiness probe",
            "GET /live": "Liveness probe",
        }
    }

@app.post("/reason")
async def reason(request: ReasonRequest):
    # Stub reasoning logic
    return {"reasoning": f"Analyzed {request.repo}: {request.query}", "confidence": 0.95}

