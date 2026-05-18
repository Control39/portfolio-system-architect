"""
API для анализа и рекомендаций по проектам портфолио (FastAPI)
"""

from datetime import datetime, timezone
from typing import Any, TypedDict

from fastapi import APIRouter, HTTPException


class Project(TypedDict, total=False):
    """Тип для проекта портфолио"""

    id: int
    name: str
    description: str
    status: str
    progress: int
    deadline: str
    technologies: list[str]
    team_size: int
    budget: int


router = APIRouter(prefix="/api", tags=["portfolio-reasoning"])

# Демонстрационные данные проектов
SAMPLE_PROJECTS: list[Project] = [
    {
        "id": 1,
        "name": "E-commerce Platform",
        "description": "Платформа для онлайн-торговли с полным набором функций",
        "status": "in-progress",
        "progress": 75,
        "deadline": "2026-03-15",
        "technologies": ["Python", "Django", "PostgreSQL", "React"],
        "team_size": 8,
        "budget": 150000,
    },
    {
        "id": 2,
        "name": "Mobile Banking App",
        "description": "Мобильное приложение для банковских операций",
        "status": "pending",
        "progress": 0,
        "deadline": "2026-04-30",
        "technologies": ["Swift", "Kotlin", "Node.js", "MongoDB"],
        "team_size": 6,
        "budget": 120000,
    },
    {
        "id": 3,
        "name": "Data Analytics Dashboard",
        "description": "Панель для визуализации и анализа бизнес-данных",
        "status": "completed",
        "progress": 100,
        "deadline": "2026-01-20",
        "technologies": ["Python", "Pandas", "D3.js", "PostgreSQL"],
        "team_size": 4,
        "budget": 80000,
    },
]


@router.get("/projects")
async def get_projects() -> list[Project]:
    """Получение списка всех проектов"""
    return SAMPLE_PROJECTS


@router.get("/projects/{project_id}")
async def get_project(project_id: int) -> Project:
    """Получение информации о конкретном проекте"""
    project = next((p for p in SAMPLE_PROJECTS if p["id"] == project_id), None)
    if project:
        return project
    raise HTTPException(status_code=404, detail="Project not found")


@router.get("/projects/{project_id}/recommendations")
async def get_recommendations(project_id: int) -> dict[str, Any]:
    """Получение рекомендаций для проекта"""
    project = next((p for p in SAMPLE_PROJECTS if p["id"] == project_id), None)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Генерируем демонстрационные рекомендации
    return generate_recommendations(project)


def analyze_portfolio() -> dict[str, Any]:
    """Анализ всего портфолио"""
    technologies_set: set[str] = set()
    for p in SAMPLE_PROJECTS:
        techs = p.get("technologies")
        if isinstance(techs, list):
            for tech in techs:
                if isinstance(tech, str):
                    technologies_set.add(tech)

    completed = [p for p in SAMPLE_PROJECTS if p.get("status") == "completed"]
    in_progress = [p for p in SAMPLE_PROJECTS if p.get("status") == "in-progress"]
    pending = [p for p in SAMPLE_PROJECTS if p.get("status") == "pending"]
    total_budget = sum(p.get("budget", 0) for p in SAMPLE_PROJECTS)
    team_sizes = [p.get("team_size", 0) or 0 for p in SAMPLE_PROJECTS]

    return {
        "total_projects": len(SAMPLE_PROJECTS),
        "completed_projects": len(completed),
        "in_progress_projects": len(in_progress),
        "pending_projects": len(pending),
        "total_budget": total_budget,
        "average_team_size": sum(team_sizes) / len(team_sizes) if team_sizes else 0,
        "technologies": sorted(technologies_set),
    }


def generate_recommendations(project: Project) -> dict[str, Any]:
    """Генерация рекомендаций для проекта"""
    from datetime import datetime, timezone

    suggestions: list[dict[str, str]] = []

    # Рекомендации на основе статуса
    if project.get("status") == "in-progress":
        progress = project.get("progress", 0) or 0
        if progress < 50:
            suggestions.append(
                {
                    "type": "warning",
                    "message": "Прогресс проекта ниже 50%. Рассмотрите возможность пересмотра плана или увеличения ресурсов.",
                }
            )
        elif progress > 80:
            suggestions.append(
                {
                    "type": "info",
                    "message": "Проект близок к завершению. Начните планирование постпроектного анализа.",
                }
            )

    # Рекомендации на основе дедлайна
    deadline_str = project.get("deadline")
    if deadline_str:
        try:
            deadline = datetime.strptime(deadline_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            days_until_deadline = (deadline - datetime.now(timezone.utc)).days

            if days_until_deadline < 30 and project.get("status") != "completed":
                suggestions.append(
                    {
                        "type": "urgent",
                        "message": f"До дедлайна осталось {days_until_deadline} дней. Приоритизируйте критически важные задачи.",
                    }
                )
        except ValueError:
            pass

    # Рекомендации на основе технологий
    technologies = project.get("technologies") or []
    team_size = project.get("team_size") or 0
    if "Python" in technologies and team_size > 5:
        suggestions.append(
            {
                "type": "info",
                "message": "Для Python проектов с большой командой рассмотрите использование дополнительных инструментов для управления зависимостями.",
            }
        )

    # Рекомендации на основе бюджета
    budget = project.get("budget") or 0
    if budget > 100000:
        suggestions.append(
            {
                "type": "info",
                "message": "Проект с крупным бюджетом. Рассмотрите возможность внедрения дополнительных метрик отслеживания ROI.",
            }
        )

    return {
        "project_id": project.get("id"),
        "project_name": project.get("name"),
        "suggestions": suggestions,
    }


@router.get("/health")
@router.get("/ready")
@router.get("/live")
async def health_check() -> dict[str, Any]:
    """Проверка состояния API - поддерживает /health, /ready, /live endpoints"""
    return {
        "service": "Portfolio Organizer Reasoning API",
        "status": "healthy",
        "version": "0.1.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "checks": {"api": {"status": "ok"}},
    }
