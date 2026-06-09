"""
Unit Tests for Cognitive Agent FastAPI Endpoints

Цель: Покрытие 85%+ для endpoints.py
"""

import pytest
import sys
from pathlib import Path

# Добавляем корень проекта в PATH
REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Добавляем путь к cognitive_agent src
COGNITIVE_SRC = REPO_ROOT / "apps" / "cognitive_agent" / "src"
if str(COGNITIVE_SRC) not in sys.path:
    sys.path.insert(0, str(COGNITIVE_SRC))

from fastapi.testclient import TestClient


# Import app
sys.path.insert(0, str(COGNITIVE_SRC / "api"))
from endpoints import app


# Create test client
client = TestClient(app)


class TestEndpoints:
    """Unit tests for Cognitive Agent FastAPI endpoints"""

    # =========================================================================
    # TEST 1: Health Endpoints
    # =========================================================================

    def test_health_endpoint(self):
        """
        Test: GET /health
        Проверка health check endpoint
        """
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_status_endpoint(self):
        """
        Test: GET /api/v1/status
        Проверка альтернативного health check endpoint
        """
        response = client.get("/api/v1/status")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "cognitive-agent"
        assert data["version"] == "0.1.0"

    def test_root_endpoint(self):
        """
        Test: GET /
        Проверка root endpoint с версией API
        """
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Cognitive Agent API"
        assert data["version"] == "0.1.0"

    # =========================================================================
    # TEST 2: Scan Endpoint
    # =========================================================================

    def test_scan_endpoint_success(self):
        """
        Test: POST /api/v1/scan (Success)
        Проверка успешного запроса сканирования
        """
        request_data = {"project_path": "/path/to/project", "mode": "full"}

        response = client.post("/api/v1/scan", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "pending"
        assert "files_found" in data
        assert "languages_detected" in data
        assert "Сканирование начато для" in data["message"]

    def test_scan_endpoint_validation_error(self):
        """
        Test: POST /api/v1/scan (Validation Error)
        Проверка обработки невалидных данных
        """
        request_data = {
            # project_path отсутствует - должно вызвать 422
            "mode": "full"
        }

        response = client.post("/api/v1/scan", json=request_data)

        assert response.status_code == 422

    def test_scan_endpoint_missing_field(self):
        """
        Test: POST /api/v1/scan (Missing project_path)
        Проверка обработки отсутствующего обязательного поля
        """
        request_data = {}

        response = client.post("/api/v1/scan", json=request_data)

        assert response.status_code == 422

    # =========================================================================
    # TEST 3: Plan Endpoint
    # =========================================================================

    def test_plan_endpoint_success(self):
        """
        Test: POST /api/v1/plan (Success)
        Проверка успешного запроса планирования
        """
        request_data = {"goals": "Улучшить производительность", "project_path": "."}

        response = client.post("/api/v1/plan", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert "tasks" in data
        assert isinstance(data["tasks"], list)
        assert "estimated_duration" in data
        assert "Планирование начато для целей" in data["message"]

    def test_plan_endpoint_validation_error(self):
        """
        Test: POST /api/v1/plan (Validation Error)
        Проверка обработки невалидных данных
        """
        request_data = {
            # goals отсутствует - должно вызвать 422
            "project_path": "."
        }

        response = client.post("/api/v1/plan", json=request_data)

        assert response.status_code == 422

    def test_plan_endpoint_empty_goals(self):
        """
        Test: POST /api/v1/plan (Empty goals)
        Проверка обработки пустых целей
        """
        request_data = {"goals": "", "project_path": "."}

        response = client.post("/api/v1/plan", json=request_data)

        # Должен пройти валидацию (пустая строка допустима)
        assert response.status_code == 200

    # =========================================================================
    # TEST 4: Execute Endpoint
    # =========================================================================

    def test_execute_endpoint_success(self):
        """
        Test: POST /api/v1/execute (Success)
        Проверка успешного запроса выполнения задачи
        """
        response = client.post(
            "/api/v1/execute", params={"task_id": "task_123", "skill_name": "scanner"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "pending"
        assert data["task_id"] == "task_123"
        assert data["skill_name"] == "scanner"
        assert "Выполнение задачи" in data["message"]

    def test_execute_endpoint_missing_task_id(self):
        """
        Test: POST /api/v1/execute (Missing task_id)
        Проверка обработки отсутствующего task_id
        """
        response = client.post("/api/v1/execute", params={"skill_name": "scanner"})

        # FastAPI вернёт 422 если task_id обязательный
        assert response.status_code == 422

    def test_execute_endpoint_missing_skill_name(self):
        """
        Test: POST /api/v1/execute (Missing skill_name)
        Проверка обработки отсутствующего skill_name
        """
        response = client.post("/api/v1/execute", params={"task_id": "task_123"})

        # FastAPI вернёт 422 если skill_name обязательный
        assert response.status_code == 422

    # =========================================================================
    # TEST 5: Metrics Endpoint
    # =========================================================================

    def test_metrics_endpoint(self):
        """
        Test: GET /api/v1/metrics
        Проверка получения метрик обучения
        """
        response = client.get("/api/v1/metrics")

        assert response.status_code == 200
        data = response.json()
        assert "total_tasks" in data
        assert "successful_tasks" in data
        assert "efficiency_score" in data

    def test_metrics_endpoint_structure(self):
        """
        Test: GET /api/v1/metrics (Structure)
        Проверка структуры ответа метрик
        """
        response = client.get("/api/v1/metrics")

        data = response.json()

        assert isinstance(data["total_tasks"], int)
        assert isinstance(data["successful_tasks"], int)
        assert isinstance(data["efficiency_score"], float)

    # =========================================================================
    # TEST 6: Skills Endpoint
    # =========================================================================

    def test_skills_endpoint(self):
        """
        Test: GET /api/v1/skills
        Проверка получения списка навыков
        """
        response = client.get("/api/v1/skills")

        assert response.status_code == 200
        data = response.json()
        assert "skills" in data
        assert isinstance(data["skills"], list)

    def test_skills_endpoint_structure(self):
        """
        Test: GET /api/v1/skills (Structure)
        Проверка структуры списка навыков
        """
        response = client.get("/api/v1/skills")

        data = response.json()
        skills = data["skills"]

        assert len(skills) >= 1  # Должен быть хотя бы один навык

        # Проверяем структуру первого навыка
        first_skill = skills[0]
        assert "name" in first_skill
        assert "description" in first_skill

    # =========================================================================
    # TEST 7: Error Handling
    # =========================================================================

    def test_error_handling_404(self):
        """
        Test: 404 Error Handling
        Проверка обработки несуществующего endpoint
        """
        response = client.get("/nonexistent")

        assert response.status_code == 404

    def test_error_handling_405_method_not_allowed(self):
        """
        Test: 405 Method Not Allowed
        Проверка обработки неподдерживаемого HTTP метода
        """
        response = client.put("/health")

        assert response.status_code == 405

    def test_error_handling_422_invalid_json(self):
        """
        Test: 422 Invalid JSON
        Проверка обработки невалидного JSON
        """
        response = client.post(
            "/api/v1/scan", content="invalid json", headers={"Content-Type": "application/json"}
        )

        assert response.status_code == 422

    # =========================================================================
    # TEST 8: Response Models
    # =========================================================================

    def test_scan_response_model(self):
        """
        Test: Scan Response Model Validation
        Проверка соответствия ответа модели ScanResponse
        """
        request_data = {"project_path": "/path/to/project", "mode": "full"}

        response = client.post("/api/v1/scan", json=request_data)

        assert response.status_code == 200
        data = response.json()

        # Проверка полей модели ScanResponse
        assert "status" in data
        assert "files_found" in data
        assert "languages_detected" in data
        assert "message" in data

    def test_plan_response_model(self):
        """
        Test: Plan Response Model Validation
        Проверка соответствия ответа модели PlanResponse
        """
        request_data = {"goals": "Улучшить производительность", "project_path": "."}

        response = client.post("/api/v1/plan", json=request_data)

        assert response.status_code == 200
        data = response.json()

        # Проверка полей модели PlanResponse
        assert "tasks" in data
        assert "estimated_duration" in data
        assert "message" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
