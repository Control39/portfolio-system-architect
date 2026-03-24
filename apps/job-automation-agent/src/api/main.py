from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import os
import asyncio
from ..core.orchestrator import run_core_agent
from ..agents.job_search import search_hh_ru
from apps.career-development.src.src.core.db import get_db  # Shared DB

app = FastAPI(title=\"Job Automation Agent API\", version=\"0.1.0\")

class AgentTask(BaseModel):
    task: str
    context: Dict[str, Any] = {}

@app.get(\"/\")
async def root():
    return {\"message\": \"Job Automation Agent running. Core + Search/Resume ready.\"}

@app.post(\"/core/run\")
async def execute_agent(task: AgentTask):
    \"\"\"Запуск Core Agent (orchestrator).\"\"\" 
    result = await run_core_agent(task.task, task.context)
    return result

@app.get(\"/jobs/search/{query}\")
async def search_jobs(query: str):
    \"\"\"Job Search Agent endpoint.\"\"\" 
    vacancies = await search_hh_ru(query)
    return {\"vacancies\": vacancies}

@app.post(\"/resume/generate\")
async def gen_resume(job: Dict[str, str]):
    \"\"\"Resume Agent.\"\"\" 
    # Stub profile from career DB (integrate later)
    profile = {\"skills\": [\"Python\", \"FastAPI\", \"PostgreSQL\"], \"name\": \"Architect\"}
    from ..agents.resume import generate_resume
    resume_md = await generate_resume(profile, job)
    return {\"resume\": resume_md}

if __name__ == \"__main__\":
    import uvicorn
    port = int(os.getenv(\"PORT\", 8001))
    uvicorn.run(\"main:app\", host=\"0.0.0.0\", port=port, reload=True)

