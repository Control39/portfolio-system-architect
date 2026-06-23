import os
import sys
from pathlib import Path
from typing import Any

# Добавляем корень проекта в PATH
REPO_ROOT = Path(__file__).parent.parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Интеграция с AI Config Manager
try:
    from apps.job_automation_agent.src.config_integration import get_config

    AI_CONFIG_AVAILABLE = True
    config_manager = get_config()
    job_agent_config = config_manager.get_config()
    print("✅ Job Automation Agent: использован AI Config Manager")
except Exception as e:
    AI_CONFIG_AVAILABLE = False
    print(f"⚠️  Job Automation Agent: AI Config Manager недоступен ({e}), используется локальный конфиг")
    job_agent_config = {}

from fastapi import FastAPI
from pydantic import BaseModel

from apps.infra_orchestrator.src.adapters.job_search_adapter import CognitiveJobSearch

# Добавляем путь для импорта общих модулей
from src.common.async_helpers import fetch_with_timeout
from src.common.health_check import init_health_checks

# ИМПОРТИРУЕМ ЧЕРЕЗ ИНТЕРФЕЙС, а не напрямую!
# Это архитектурное решение: зависимости внедряются, а не импортируются жёстко.
from src.interfaces.job_search import IJobSearch


# Внедрение зависимости (Dependency Injection)
def get_job_search_provider() -> IJobSearch:
    """
    Получение провайдера поиска вакансий.

    Возвращает:
        Экземпляр, реализующий интерфейс IJobSearch.

    Преимущество:
        Можно легко заменить реализацию без изменения кода этого модуля.
        Например: CognitiveJobSearch -> HHruJobSearch -> LinkedInJobSearch
    """
    base_url = os.getenv("COGNITIVE_AGENT_URL", "http://cognitive-agent:8006")
    return CognitiveJobSearch(base_url=base_url)


app = FastAPI(title="Job Automation Agent API", version="0.1.0")

# Инициализируем health-check
init_health_checks(app, service_name="job-automation-agent", version="0.1.0")

# Инициализация провайдера поиска (можно также лениво инициализировать в каждом запросе)
_job_search_provider: IJobSearch | None = None


def get_search_provider() -> IJobSearch:
    """Ленивая инициализация провайдера поиска."""
    global _job_search_provider
    if _job_search_provider is None:
        _job_search_provider = get_job_search_provider()
    return _job_search_provider


class AgentTask(BaseModel):
    task: str
    context: dict[str, Any] = {}


@app.get("/")
async def root():
    return {
        "message": "Job Automation Agent running. Core + Search/Resume ready via Dependency Injection.",
        "version": "0.1.0",
        "architecture": "Dependency Injection (IJobSearch interface)",
        "endpoints": {
            "GET /health": "Health check",
            "GET /ready": "Readiness probe",
            "GET /live": "Liveness probe",
            "POST /core/run": "Execute core agent",
            "GET /jobs/search/{query}": "Search jobs (via IJobSearch interface)",
            "POST /resume/generate": "Generate resume",
        },
    }


@app.post("/core/run")
async def execute_agent(task: AgentTask):
    """Запуск Core Agent (orchestrator)."""
    # Добавляем таймаут для длительных операций
    return await fetch_with_timeout(run_core_agent(task.task, task.context), timeout=60)


@app.get("/jobs/search/{query}")
async def search_jobs(query: str):
    """
    Поиск вакансий через интерфейс IJobSearch.

    Архитектурное преимущество:
    - job_automation_agent НЕ зависит от реализации cognitive_agent
    - Можно заменить CognitiveJobSearch на HHruJobSearch без изменения этого кода
    - Тестируется через mock IJobSearch
    """
    search_provider = get_search_provider()
    vacancies = await search_provider.search(query)
    return {"vacancies": vacancies, "source": "IJobSearch interface"}


@app.post("/resume/generate")
async def gen_resume(job: dict[str, str]):
    """Resume Agent."""
    # Stub profile from career DB (integrate later)
    profile = {"skills": ["Python", "FastAPI", "PostgreSQL"], "name": "Architect"}

    # TODO: Вынести генерацию резюме в отдельный сервис или использовать интерфейс
    # from src.interfaces.resume_generator import IResumeGenerator
    # resume_generator = get_resume_generator()
    # resume_md = await resume_generator.generate(profile, job)

    from .apps.cognitive_agent.resume import generate_resume

    resume_md = await generate_resume(profile, job)
    return {"resume": resume_md}


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8001))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
