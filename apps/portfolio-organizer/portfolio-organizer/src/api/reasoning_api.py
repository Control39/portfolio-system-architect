"""
API для анализа и рекомендаций по проектам портфолио
"""

from flask import Flask, jsonify, request
from flask_wtf.csrf import CSRFProtect
from typing import Dict, List, Any
import json
import os

app = Flask(__name__)

app.secret_key = os.environ.get('SECRET_KEY')
if not app.secret_key:
    raise ValueError('SECRET_KEY environment variable not set!')
csrf = CSRFProtect(app)

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


@app.route("/api/projects", methods=["GET"])
def get_projects():
    """Получение списка всех проектов"""
    return jsonify(SAMPLE_PROJECTS)


@app.route("/api/projects/<int:project_id>", methods=["GET"])
def get_project(project_id):
    """Получение информации о конкретном проекте"""
    project = next((p for p in SAMPLE_PROJECTS if p["id"] == project_id), None)
    if project:
        return jsonify(project)
    else:
        return jsonify({"error": "Project not found"}), 404


@app.route("/api/projects/<int:project_id>/recommendations", methods=["GET"])
def get_recommendations(project_id):
    """Получение рекомендаций для проекта"""
    project = next((p for p in SAMPLE_PROJECTS if p["id"] == project_id), None)
    if not project:
        return jsonify({"error": "Project not found"}), 404

    # Генерируем демонстрационные рекомендации
    recommendations = generate_recommendations(project)
    return jsonify(recommendations)


@app.route("/api/portfolio/analysis", methods=["GET"])
def portfolio_analysis():
    """Анализ всего портфолио"""
    analysis = {
        "total_projects": len(SAMPLE_PROJECTS),
        "completed_projects": len(
            [p for p in SAMPLE_PROJECTS if p["status"] == "completed"]
        ),
        "in_progress_projects": len(
            [p for p in SAMPLE_PROJECTS if p["status"] == "in-progress"]
        ),
        "pending_projects": len(
            [p for p in SAMPLE_PROJECTS if p["status"] == "pending"]
        ),
        "total_budget": sum(p["budget"] for p in SAMPLE_PROJECTS),
        "average_team_size": sum(p["team_size"] for p in SAMPLE_PROJECTS)
        / len(SAMPLE_PROJECTS),
        "technologies": list(
            set(tech for p in SAMPLE_PROJECTS for tech in p["technologies"])
        ),
    }

    return jsonify(analysis)


def generate_recommendations(project: Dict[str, Any]) -> Dict[str, Any]:
    """Генерация рекомендаций для проекта"""
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
    from datetime import datetime

    deadline = datetime.strptime(project["deadline"], "%Y-%m-%d")
    days_until_deadline = (deadline - datetime.now()).days

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


@app.route("/api/health", methods=["GET"])
def health_check():
    """Проверка состояния API"""
    return jsonify(
        {"status": "healthy", "service": "Portfolio Organizer Reasoning API"}
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=os.environ.get('FLASK_DEBUG', 'False').lower() == 'true')
