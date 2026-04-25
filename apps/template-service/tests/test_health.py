"""
Тесты для health check endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_health_check():
    """Тест базового health check endpoint."""
    response = client.get("/health/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "template-service"
    assert "timestamp" in data
    assert data["version"] == "0.1.0"


def test_liveness_check():
    """Тест liveness check endpoint."""
    response = client.get("/health/live")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "alive"
    assert "timestamp" in data


@pytest.mark.asyncio
async def test_readiness_check_without_db():
    """
    Тест readiness check без реальной базы данных.

    Этот тест проверяет, что endpoint возвращает корректную структуру,
    даже если база данных недоступна.
    """
    response = client.get("/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "database" in data
    assert "timestamp" in data
