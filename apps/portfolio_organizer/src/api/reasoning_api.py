"""
API для анализа и рекомендаций по проектам портфолио (FastAPI)
"""

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, HTTPException


router = APIRouter(prefix="/api", tags=["portfolio-reasoning"])

# Демонстрационные данные проектов
SAMPLE_PROJECTS = [
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
async def get_projects() -> list[dict[str, Any]]:
    """Получение списка всех проектов"""
    return SAMPLE_PROJECTS


@router.get("/projects/{project_id}")
async def get_project(project_id: int) -> dict[str, Any]:
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


@router.get("/portfolio/analysis")
async def portfolio_analysis() -> dict[str, Any]:
    """Анализ всего портфолио"""
    return {
        "total_projects": len(SAMPLE_PROJECTS),
        "completed_projects": len([p for p in SAMPLE_PROJECTS if p["status"] == "completed"]),
        "in_progress_projects": len([p for p in SAMPLE_PROJECTS if p["status"] == "in-progress"]),
        "pending_projects": len([p for p in SAMPLE_PROJECTS if p["status"] == "pending"]),
        "total_budget": sum(p["budget"] for p in SAMPLE_PROJECTS),
        "average_team_size": sum(p["team_size"] for p in SAMPLE_PROJECTS) / len(SAMPLE_PROJECTS),
        "technologies": list({tech for p in SAMPLE_PROJECTS for tech in p["technologies"]}),
    }


def generate_recommendations(project: dict[str, Any]) -> dict[str, Any]:
    """Генерация рекомендаций для проекта"""
    from datetime import datetime, timezone

    recommendations = {
        "project_id": project["id"],
        "project_name": project["name"],
        "suggestions": [],
    }

    # Рекомендации на основе статуса
    if project["status"] == "in-progress":
        if project["progress"] < 50:
            recommendations["suggestions"].append(
                {
                    "type": "warning",
                    "message": "Прогресс проекта ниже 50%. Рассмотрите возможность пересмотра плана или увеличения ресурсов.",
                }
            )
        elif project["progress"] > 80:
            recommendations["suggestions"].append(
                {
                    "type": "info",
                    "message": "Проект близок к завершению. Начните планирование постпроектного анализа.",
                }
            )

    # Рекомендации на основе дедлайна
    deadline = datetime.strptime(project["deadline"], "%Y-%m-%d").replace(tzinfo=timezone.utc)
    days_until_deadline = (deadline - datetime.now(timezone.utc)).days

    if days_until_deadline < 30 and project["status"] != "completed":
        recommendations["suggestions"].append(
            {
                "type": "urgent",
                "message": f"До дедлайна осталось {days_until_deadline} дней. Приоритизируйте критически важные задачи.",
            }
        )

    # Рекомендации на основе технологий
    if "Python" in project["technologies"] and project["team_size"] > 5:
        recommendations["suggestions"].append(
            {
                "type": "info",
                "message": "Для Python проектов с большой командой рассмотрите использование дополнительных инструментов для управления зависимостями.",
            }
        )

    # Рекомендации на основе бюджета
    if project["budget"] > 100000:
        recommendations["suggestions"].append(
            {
                "type": "info",
                "message": "Проект с крупным бюджетом. Рассмотрите возможность внедрения дополнительных метрик отслеживания ROI.",
            }
        )

    return recommendations


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
