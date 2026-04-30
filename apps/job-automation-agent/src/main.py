import asyncio
import os
import sys
from typing import Any, Dict

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Добавляем путь для импорта общих модулей
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
from src.common.async_helpers import fetch_parallel, fetch_with_timeout
from src.common.health_check import init_health_checks

from ..agents.job_search import search_hh_ru
from ..core.orchestrator import run_core_agent

app = FastAPI(title="Job Automation Agent API", version="0.1.0")

# Инициализируем health-check
init_health_checks(app, service_name="job-automation-agent", version="0.1.0")

class AgentTask(BaseModel):
    task: str
    context: Dict[str, Any] = {}

@app.get("/")
async def root():
    return {
        "message": "Job Automation Agent running. Core + Search/Resume ready.",
        "version": "0.1.0",
        "endpoints": {
            "GET /health": "Health check",
            "GET /ready": "Readiness probe",
            "GET /live": "Liveness probe",
            "POST /core/run": "Execute core agent",
            "GET /jobs/search/{query}": "Search jobs",
            "POST /resume/generate": "Generate resume",
        }
    }

@app.post("/core/run")
async def execute_agent(task: AgentTask):
    """Запуск Core Agent (orchestrator)."""
    # Добавляем таймаут для длительных операций
    result = await fetch_with_timeout(
        run_core_agent(task.task, task.context),
        timeout=60
    )
    return result

@app.get("/jobs/search/{query}")
async def search_jobs(query: str):
    """Job Search Agent endpoint."""
    vacancies = await search_hh_ru(query)
    return {"vacancies": vacancies}

@app.post("/resume/generate")
async def gen_resume(job: Dict[str, str]):
    """Resume Agent."""
    # Stub profile from career DB (integrate later)
    profile = {"skills": ["Python", "FastAPI", "PostgreSQL"], "name": "Architect"}
    from ..agents.resume import generate_resume
    resume_md = await generate_resume(profile, job)
    return {"resume": resume_md}

if __name__ == \"__main__\":
    import uvicorn
    port = int(os.getenv(\"PORT\", 8001))
    uvicorn.run(\"main:app\", host=\"0.0.0.0\", port=port, reload=True)
