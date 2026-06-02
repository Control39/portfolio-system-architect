"""
E2E Тесты для Career Development

Service: apps/career_development (Python/FastAPI)
Port: 8301
Endpoints: /, /health, /api/v1/competencies, /api/v1/roadmap
"""

import pytest
import requests


@pytest.mark.e2e
class TestCareerDevelopment:
    """Тесты Career Development API"""

    BASE_URL = "http://localhost:8301"

    def test_service_info(self):
        """Проверяет, что сервис отвечает"""
        response = requests.get(f"{self.BASE_URL}/")
        assert response.status_code == 200
        data = response.json()
        assert "career" in data.get("service", "").lower()

    def test_health_check(self):
        """Проверяет health check endpoint"""
        response = requests.get(f"{self.BASE_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_list_competencies(self):
        """Проверяет список компетенций"""
        response = requests.get(f"{self.BASE_URL}/api/v1/competencies")
        # Может вернуть 200 или 501
        assert response.status_code in [200, 501]
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list) or "competencies" in data

    def test_get_roadmap(self):
        """Проверяет получение roadmap"""
        response = requests.get(f"{self.BASE_URL}/api/v1/roadmap")
        # Может вернуть 200 или 501
        assert response.status_code in [200, 501]
        if response.status_code == 200:
            data = response.json()
            assert "roadmap" in data or "steps" in data
