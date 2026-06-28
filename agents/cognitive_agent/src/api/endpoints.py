# components/cognitive-agent/api/endpoints.py

from contextvars import ContextVar
from pathlib import Path

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
            from agents.cognitive_agent.src.autonomous_agent import AutonomousCognitiveAgent

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
    """Запустить сканирование проекта.

    Использует `scripts/scanner_main.py` (ProjectScanner).
    """
    try:
        from agents.cognitive_agent.scripts.scanner_main import ProjectScanner

        # Валидация пути: ограничиваем доступ в пределах репозитория c:/repo
        # (на проде это защищает от простых попыток path traversal)
        repo_root = Path(__file__).resolve().parents[3]
        project_root = (
            (repo_root / request.project_path).resolve()
            if not Path(request.project_path).is_absolute()
            else Path(request.project_path).resolve()
        )
        if repo_root not in project_root.parents and repo_root != project_root:
            raise HTTPException(status_code=400, detail="project_path must be inside repository")

        scanner = ProjectScanner()
        results = scanner.scan_project(str(project_root))

        languages = results.get("tech_stack", {}).get("languages", [])
        # files_found по текущей реализации сканера явно не возвращается — оцениваем косвенно
        files_found = 0
        files_found = len(results.get("dependencies", {}).get("python", []) or [])

        return ScanResponse(
            status="success",
            files_found=files_found,
            languages_detected=languages if isinstance(languages, list) else [],
            message=f"Сканирование завершено для: {project_root}",
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/plan", response_model=PlanResponse)
async def plan_tasks(request: PlanRequest):
    """Создать план задач.

    Использует `scripts/planner_main.py` (TaskPlanner).

    В этой реализации goals пока не используется для генерации плана (планировщик
    берет задачи из `apps/cognitive_agent/data/tasks.json` либо генерирует sample tasks).
    """
    try:
        from agents.cognitive_agent.scripts.planner_main import TaskPlanner

        planner = TaskPlanner()
        planner.load_tasks()
        tasks = planner.prioritize_tasks()

        # estimated_duration: суммарная оценка по минутам
        estimated_duration = 0.0
        for t in tasks or []:
            estimated_duration += float(t.get("estimated_duration", 0) or 0)

        return PlanResponse(
            tasks=tasks or [],
            estimated_duration=estimated_duration,
            message=f"Планирование завершено для целей: {request.goals}",
        )
    except HTTPException:
        raise
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
