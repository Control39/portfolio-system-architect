"""
Реальные тесты для portfolio_organizer (FastAPI)

Service Tier: BUSINESS
Purpose: Unit и functional тесты реальной бизнес-логики

Test Coverage:
- API endpoints (projects, recommendations, portfolio analysis)
- ITCompassAPI integration
- NotificationService
- ML Model Registry integration endpoints
- Error handling и валидация
"""

import os
from datetime import datetime

import pytest
from fastapi.testclient import TestClient


# Устанавливаем SECRET_KEY ДО импорта приложения
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only"

# Импортируем реальное приложение
import sys


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from apps.portfolio_organizer.src.api.reasoning_api import SAMPLE_PROJECTS, router


# Создаем тестовый клиент FastAPI
@pytest.fixture
def client():
    """FastAPI test client"""
    from fastapi import FastAPI

    app = FastAPI()
    app.include_router(router)
    # Подключаем также ML Model Registry router
    from apps.portfolio_organizer.src.api.ml_model_registry_integration import router as ml_router

    app.include_router(ml_router)
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def sample_project():
    """Sample project for testing"""
    return {
        "id": 999,
        "name": "Test Project",
        "description": "Test description",
        "status": "in-progress",
        "progress": 30,
        "deadline": "2026-12-31",
        "technologies": ["Python", "FastAPI"],
        "team_size": 5,
        "budget": 50000,
    }


# ============================================================================
# TESTS: Project API
# ============================================================================


class TestProjectAPI:
    """Тесты для Project API endpoints"""

    def test_get_projects_returns_list(self, client):
        """Test: Получить список всех проектов"""
        response = client.get("/api/projects")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert "id" in data[0]
        assert "name" in data[0]

    def test_get_existing_project(self, client):
        """Test: Получить существующий проект по ID"""
        response = client.get("/api/projects/1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["name"] == "E-commerce Platform"

    def test_get_nonexistent_project(self, client):
        """Test: Получить несуществующий проект возвращает 404"""
        response = client.get("/api/projects/9999")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    def test_get_project_recommendations(self, client):
        """Test: Получить рекомендации для проекта"""
        response = client.get("/api/projects/1/recommendations")
        assert response.status_code == 200
        data = response.json()
        assert "project_id" in data
        assert "suggestions" in data
        assert isinstance(data["suggestions"], list)

    def test_recommendations_for_incomplete_project(self, client):
        """Test: Рекомендации для незавершенного проекта"""
        response = client.get("/api/projects/1/recommendations")
        assert response.status_code == 200
        data = response.json()
        # Проект в процессе, прогресс 75%
        assert data["project_id"] == 1

    def test_generate_recommendations_logic(self, sample_project):
        """Test: Логика генерации рекомендаций"""
        from apps.portfolio_organizer.src.api.reasoning_api import generate_recommendations

        recommendations = generate_recommendations(sample_project)
        assert recommendations["project_id"] == 999
        assert "suggestions" in recommendations
        # Прогресс < 50%, должно быть предупреждение
        warning_found = any(s.get("type") == "warning" for s in recommendations["suggestions"])
        assert warning_found, "Должно быть предупреждение о прогрессе < 50%"


# ============================================================================
# TESTS: Portfolio Analysis
# ============================================================================


class TestPortfolioAnalysis:
    """Тесты для анализа портфолио"""

    def test_portfolio_analysis_returns_summary(self, client):
        """Test: Анализ портфолио возвращает сводку"""
        response = client.get("/api/portfolio/analysis")
        assert response.status_code == 200
        data = response.json()
        assert "total_projects" in data
        assert "completed_projects" in data
        assert "in_progress_projects" in data
        assert "pending_projects" in data
        assert "total_budget" in data

    def test_portfolio_analysis_calculates_totals(self, client):
        """Test: Анализ корректно считает итоги"""
        response = client.get("/api/portfolio/analysis")
        assert response.status_code == 200
        data = response.json()
        assert data["total_projects"] == len(SAMPLE_PROJECTS)
        assert data["total_budget"] == sum(p["budget"] for p in SAMPLE_PROJECTS)

    def test_portfolio_analysis_technologies(self, client):
        """Test: Анализ возвращает уникальные технологии"""
        response = client.get("/api/portfolio/analysis")
        assert response.status_code == 200
        data = response.json()
        assert "technologies" in data
        assert isinstance(data["technologies"], list)
        # Python должен быть в списке
        assert "Python" in data["technologies"]


# ============================================================================
# TESTS: Health Endpoints
# ============================================================================


class TestHealthEndpoints:
    """Тесты для health check endpoints"""

    def test_health_endpoint(self, client):
        """Test: /api/health возвращает healthy"""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data

    def test_health_endpoint_has_timestamp(self, client):
        """Test: Health ответ содержит timestamp"""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert "timestamp" in data
        # Проверка, что timestamp в формате ISO
        datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))

    def test_ready_endpoint(self, client):
        """Test: /api/ready endpoint работает"""
        response = client.get("/api/ready")
        assert response.status_code == 200

    def test_live_endpoint(self, client):
        """Test: /api/live endpoint работает"""
        response = client.get("/api/live")
        assert response.status_code == 200


# ============================================================================
# TESTS: ITCompassAPI Integration
# ============================================================================


class TestITCompassAPI:
    """Тесты для интеграции с IT-Compass"""

    def test_it_compass_api_imports(self):
        """Test: ITCompassAPI может быть импортирован"""
        from apps.portfolio_organizer.src.core.ITCompassAPI import ITCompassAPI

        assert ITCompassAPI is not None

    def test_it_compass_get_competency_markers(self):
        """Test: Получение маркеров компетенций"""
        from apps.portfolio_organizer.src.core.ITCompassAPI import ITCompassAPI

        api = ITCompassAPI()
        result = api.get_competency_markers(["Python", "Docker"])
        assert isinstance(result, list)
        assert len(result) > 0
        assert "marker" in result[0]

    def test_it_compass_with_empty_skills(self):
        """Test: Маркеры с пустым списком навыков"""
        from apps.portfolio_organizer.src.core.ITCompassAPI import ITCompassAPI

        api = ITCompassAPI()
        result = api.get_competency_markers([])
        assert isinstance(result, list)


# ============================================================================
# TESTS: NotificationService
# ============================================================================


class TestNotificationService:
    """Тесты для сервиса уведомлений"""

    def test_notification_service_imports(self):
        """Test: NotificationService может быть импортирован"""
        from apps.portfolio_organizer.src.core.notification_service import (
            NotificationService,
        )

        assert NotificationService is not None

    def test_send_email_prints_message(self, capsys):
        """Test: Отправка email выводит сообщение"""
        from apps.portfolio_organizer.src.core.notification_service import (
            NotificationService,
        )

        service = NotificationService()
        service.send_email("Test message")
        captured = capsys.readouterr()
        assert "Email sent: Test message" in captured.out


# ============================================================================
# TESTS: ML Model Registry Integration
# ============================================================================


class TestMLModelRegistryIntegration:
    """Тесты для интеграции с ML Model Registry"""

    def test_ml_registry_router_imports(self):
        """Test: Router ML Model Registry импортируется"""
        from apps.portfolio_organizer.src.api.ml_model_registry_integration import router

        assert router is not None
        assert router.prefix == "/api/ml-model-registry"

    def test_list_models_endpoint(self, client):
        """Test: Список моделей"""
        response = client.get("/api/ml-model-registry/models")
        # Ожидаем 503 т.к. ML Model Registry не запущен, но endpoint должен быть доступен
        assert response.status_code in [200, 503]

    def test_get_model_endpoint(self, client):
        """Test: Получить модель по ID"""
        response = client.get("/api/ml-model-registry/models/test-model-123")
        # Ожидаем 503 т.к. ML Model Registry не запущен, но endpoint должен быть доступен
        assert response.status_code in [200, 400, 503]

    def test_get_model_invalid_id(self, client):
        """Test: Невалидный model_id возвращает 400"""
        response = client.get("/api/ml-model-registry/models/invalid model with spaces!")
        assert response.status_code == 400


# ============================================================================
# TESTS: Error Handling
# ============================================================================


class TestErrorHandling:
    """Тесты для обработки ошибок"""

    def test_project_not_found_error(self, client):
        """Test: Обработка ошибки проекта не найден"""
        response = client.get("/api/projects/9999")
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Project not found"

    def test_recommendations_for_nonexistent_project(self, client):
        """Test: Рекомендации для несуществующего проекта"""
        response = client.get("/api/projects/9999/recommendations")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
