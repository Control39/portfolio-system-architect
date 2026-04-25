"""Unit тесты для модуля health_check.
"""

import asyncio

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.common.health_check import (
    HealthCheckResponse,
    HealthCheckService,
    init_health_checks,
)


@pytest.fixture
def app():
    """Создать тестовое FastAPI приложение"""
    return FastAPI()


@pytest.fixture
def client(app):
    """Создать тестовый клиент"""
    return TestClient(app)


class TestHealthCheckService:
    """Тесты для HealthCheckService"""

    def test_service_initialization(self):
        """Тест инициализации сервиса"""
        service = HealthCheckService("test-service", version="1.0.0")
        assert service.service_name == "test-service"
        assert service.version == "1.0.0"
        assert len(service.checks) == 0

    def test_register_check(self):
        """Тест регистрации проверки"""
        service = HealthCheckService("test-service")

        async def dummy_check():
            return {"status": "ok"}

        service.register_check("test", dummy_check)
        assert "test" in service.checks

    @pytest.mark.asyncio
    async def test_get_health_no_checks(self):
        """Тест получения статуса без проверок"""
        service = HealthCheckService("test-service")
        result = await service.get_health()

        assert result.service == "test-service"
        assert result.status == "healthy"
        assert result.version == "1.0.0"

    @pytest.mark.asyncio
    async def test_get_health_with_passing_check(self):
        """Тест статуса с успешной проверкой"""
        service = HealthCheckService("test-service")

        async def passing_check():
            return {"status": "ok"}

        service.register_check("test", passing_check, required=True)
        result = await service.get_health()

        assert result.status == "healthy"
        assert result.checks["test"]["status"] == "ok"

    @pytest.mark.asyncio
    async def test_get_health_with_failing_required_check(self):
        """Тест статуса с необходимой проверкой которая исключение"""
        service = HealthCheckService("test-service")

        async def failing_check():
            return {"status": "error", "error": "Database unavailable"}

        service.register_check("database", failing_check, required=True)
        result = await service.get_health()

        assert result.status == "unhealthy"
        assert result.checks["database"]["status"] == "error"

    @pytest.mark.asyncio
    async def test_get_health_with_timeout(self):
        """Тест таймаута для долгой операции"""
        service = HealthCheckService("test-service")

        async def slow_check():
            await asyncio.sleep(10)  # Более длительно чем таймаут
            return {"status": "ok"}

        service.register_check("slow", slow_check, timeout=1, required=True)
        result = await service.get_health()

        assert result.status == "unhealthy"
        assert result.checks["slow"]["status"] == "timeout"

    @pytest.mark.asyncio
    async def test_get_health_response_model(self):
        """Тест моделирования ответа"""
        service = HealthCheckService("test-service", version="2.0.0")

        async def check():
            return {"status": "ok"}

        service.register_check("test", check)
        result = await service.get_health()

        assert isinstance(result, HealthCheckResponse)
        assert result.service == "test-service"
        assert result.version == "2.0.0"
        assert result.timestamp is not None


class TestInitHealthChecks:
    """Тесты для функции init_health_checks"""

    def test_init_health_checks_basic(self, app):
        """Тест инициализации базовых health-check эндпоинтов"""
        service = init_health_checks(app, "test-service")

        assert service is not None
        assert service.service_name == "test-service"

    def test_health_endpoints_registered(self, app, client):
        """Тест что endpoints зарегистрированы"""
        init_health_checks(app, "test-service")

        # Все три endpoint должны работать
        response_health = client.get("/health")
        response_ready = client.get("/ready")
        response_live = client.get("/live")

        assert response_health.status_code == 200
        assert response_ready.status_code == 200
        assert response_live.status_code == 200

    def test_health_response_format(self, app, client):
        """Тест формата ответа health endpoint"""
        init_health_checks(app, "test-service", version="1.0.0")
        response = client.get("/health")

        data = response.json()
        assert data["service"] == "test-service"
        assert data["status"] in ["healthy", "unhealthy", "degraded"]
        assert data["version"] == "1.0.0"
        assert "checks" in data
        assert "timestamp" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

