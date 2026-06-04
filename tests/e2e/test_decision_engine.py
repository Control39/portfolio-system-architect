"""
E2E Тесты для Decision Engine

Service: apps/decision_engine (Python/FastAPI)
Port: 8001
Endpoints: /, /health, /api/v1/reason
"""

import pytest
import requests


@pytest.mark.e2e
class TestDecisionEngine:
    """Тесты Decision Engine API"""

    BASE_URL = "http://localhost:8001"

    def test_service_info(self):
        """Проверяет, что сервис отвечает на root endpoint"""
        response = requests.get(f"{self.BASE_URL}/")
        assert response.status_code == 200
        data = response.json()
        assert (
            "decision" in data.get("service", "").lower()
            or "engine" in data.get("service", "").lower()
        )

    def test_health_check(self):
        """Проверяет health check endpoint"""
        response = requests.get(f"{self.BASE_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_reasoning_endpoint(self):
        """Проверяет endpoint для AI reasoning"""
        payload = {
            "question": "Какой технолог выбрать для микросервиса?",
            "context": {
                "requirements": ["масштабируемость", "производительность"],
                "constraints": ["бюджет", "время"],
            },
        }
        response = requests.post(f"{self.BASE_URL}/api/v1/reason", json=payload, timeout=30)
        # Может вернуть 200 или 501 (если не реализован)
        assert response.status_code in [200, 501]
        if response.status_code == 200:
            data = response.json()
            assert "answer" in data or "reasoning" in data
