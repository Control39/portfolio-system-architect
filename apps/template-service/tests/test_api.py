"""Тесты для Template Service API"""

import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_root():
    """Тест root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "Template Service"
    assert data["version"] == "1.0.0"


def test_health():
    """Тест health check"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "template-service"


def test_docs():
    """Тест доступности Swagger UI"""
    response = client.get("/docs")
    assert response.status_code == 200


class TestTemplateService:
    """Тесты функциональности Template Service"""

    def test_service_info(self):
        """Тест информации о сервисе"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "endpoints" in data
        assert "GET /health" in data["endpoints"]

    def test_response_format(self):
        """Тест формата ответа"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "status" in data
        assert "service" in data
