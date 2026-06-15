# components/cognitive-agent/api/endpoints.py

from contextvars import ContextVar
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# ⭐ [БЕЗОПАСНОСТЬ] ContextVar для изоляции агента в многопоточной среде
_agent_context: ContextVar = ContextVar("agent_context", default=None)


# Добавляем путь к корню проекта для импорта атомов
# FIX: Определяем модели локально, так как src.shared.models не существует
class PlanRequest(BaseModel):
    goals: list[str]
    priority: str = "normal"


class PlanResponse(BaseModel):
    tasks: list[dict]
    estimated_duration: float
    message: str


class ScanRequest(BaseModel):
    project_path: str
    include_tests: bool = True


class ScanResponse(BaseModel):
    status: str
    files_found: int
    languages_detected: list[str]
    message: str


# ⭐ [БЕЗОПАСНОСТЬ] Получение изолированного экземпляра агента
def get_agent():
    """
    Получить или создать экземпляр агента для текущего запроса.
    Использует ContextVar для предотвращения race condition.
    """
    agent = _agent_context.get()
    if agent is None:
        # Создаём новый экземпляр для каждого запроса
        try:
            from agents.cognitive_agent.autonomous_agent import AutonomousCognitiveAgent

            agent = AutonomousCognitiveAgent()
            _agent_context.set(agent)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to initialize agent: {str(e)}")
    return agent


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
            message=f"Сканирование начато для: {request.project_path}",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/plan", response_model=PlanResponse)
async def plan_tasks(request: PlanRequest):
    """Создать план задач"""
    try:
        # TODO: Интегрировать planner_main.py + AI
        return PlanResponse(tasks=[], estimated_duration=0, message=f"Планирование начато для целей: {request.goals}")
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
            "message": f"Выполнение задачи: {task_id} через {skill_name}",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/metrics")
async def get_metrics():
    """Получить метрики обучения"""
    try:
        # TODO: Интегрировать learning_main.py
        return {"total_tasks": 0, "successful_tasks": 0, "efficiency_score": 0.0}
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
            {"name": "learning", "description": "Сбор метрик"},
        ]
    }
