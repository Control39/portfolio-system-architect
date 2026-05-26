"""
E2E Тесты для Infra Orchestrator

Service: apps/infra_orchestrator (Python/FastAPI)
Port: 8200
Endpoints: /health, /api/v1/services, /api/v1/services/{name}/deploy
"""

import pytest
import requests


@pytest.mark.e2e
class TestInfraOrchestrator:
    """Тесты Infra Orchestrator API"""

    BASE_URL = "http://localhost:8000"

    def test_service_info(self):
        """Проверяет, что сервис отвечает на root endpoint"""
        response = requests.get(f"{self.BASE_URL}/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "Infra-Orchestrator"
        assert data["status"] == "running"

    def test_health_check(self):
        """Проверяет health check endpoint"""
        response = requests.get(f"{self.BASE_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "infra-orchestrator"

    def test_list_services(self):
        """Проверяет список сервисов"""
        response = requests.get(f"{self.BASE_URL}/api/v1/services")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_deploy_service(self):
        """Проверяет деплой сервиса"""
        payload = {
            "service_name": "test-service",
            "version": "latest",
            "replicas": 1
        }
        response = requests.post(
            f"{self.BASE_URL}/api/v1/services/test-service/deploy",
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "test-service"
        assert data["status"] == "running"
        assert data["health"] == "healthy"

    def test_scale_service(self):
        """Проверяет масштабирование сервиса"""
        payload = {"service_name": "test-service", "replicas": 3}
        response = requests.post(
            f"{self.BASE_URL}/api/v1/services/test-service/scale",
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        assert data["replicas"] == 3
        assert data["service"] == "test-service"

    def test_restart_service(self):
        """Проверяет перезапуск сервиса"""
        response = requests.post(f"{self.BASE_URL}/api/v1/services/test-service/restart")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "test-service"
        assert data["status"] == "restarting"
