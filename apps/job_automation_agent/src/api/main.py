import logging
import os
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings

# Системное логирование
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("job-automation-agent")


# Центральная конфигурация (без sys.path)
class Settings(BaseSettings):
    port: int = Field(default=8001, alias="PORT")
    timeout: int = Field(default=60, alias="AGENT_TIMEOUT")
    service_name: str = "job-automation-agent"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

app = FastAPI(
    title=f"{settings.service_name.upper()} API",
    version="0.1.0",
    description="Job Automation Agent with Core Orchestrator & Search/Resume capabilities",
)

# Абсолютные импорты (требуют корректной PYTHONPATH или пакетной установки)
try:
    from apps.job_automation_agent.apps.cognitive_agent.job_search import search_hh_ru
    from apps.job_automation_agent.apps.cognitive_agent.resume import generate_resume
    from apps.job_automation_agent.core.orchestrator import run_core_agent
    from src.common.async_helpers import fetch_with_timeout
    from src.common.health_check import init_health_checks
except ImportError as e:
    logger.error(f"Import failed. Ensure PYTHONPATH includes project root. Error: {e}")
    raise

init_health_checks(app, service_name=settings.service_name, version="0.1.0")


class AgentTask(BaseModel):
    task: str
    context: dict[str, Any] = Field(default_factory=dict)


class JobSearchParams(BaseModel):
    query: str


class ResumePayload(BaseModel):
    job: dict[str, Any] = Field(..., description="Job description/data")
    profile: dict[str, Any] = Field(default_factory=dict)


@app.get("/")
async def root():
    return {
        "message": "Job Automation Agent running.",
        "version": "0.1.0",
        "status": "healthy" if getattr(app.state, "health_check_enabled", False) else "initializing",
    }


@app.post("/core/run")
async def execute_agent(task: AgentTask):
    logger.info(f"Executing agent task: {task.task[:50]}...")
    try:
        result = await fetch_with_timeout(run_core_agent(task.task, task.context), timeout=settings.timeout)
        return {"status": "success", "result": result}
    except Exception as e:
        logger.error(f"Agent execution failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Core agent execution failed") from e


@app.post("/jobs/search")
async def search_jobs(params: JobSearchParams):
    logger.info(f"Searching jobs for: {params.query}")
    try:
        vacancies = await search_hh_ru(params.query)
        return {"query": params.query, "count": len(vacancies), "vacancies": vacancies}
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail="Job search failed") from e


@app.post("/resume/generate")
async def gen_resume(payload: ResumePayload):
    logger.info("Generating resume")
    try:
        profile = payload.profile or {"skills": ["Python", "FastAPI"], "name": "Architect"}
        resume_md = await generate_resume(profile, payload.job)
        return {"status": "success", "resume": resume_md}
    except Exception as e:
        logger.error(f"Resume generation failed: {e}")
        raise HTTPException(status_code=500, detail="Resume generation failed") from e


if __name__ == "__main__":
    import uvicorn

    # reload=False для продакшена/контейнеров
    uvicorn.run("main:app", host="0.0.0.0", port=settings.port, reload=False)  # nosec B104
