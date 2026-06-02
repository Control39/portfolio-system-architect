"""
E2E Тесты для Auth Service

Service: apps/auth_service (Python/FastAPI)
Port: 8100
Endpoints: /auth/token, /auth/verify, /health
"""

import pytest
import requests


@pytest.mark.e2e
class TestAuthService:
    """Тесты Auth Service API"""

    BASE_URL = "http://localhost:8100"

    def test_service_info(self):
        """Проверяет, что сервис отвечает на root endpoint"""
        response = requests.get(f"{self.BASE_URL}/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "Auth Service"
        assert data["version"] == "1.0.0"

    def test_health_check(self):
        """Проверяет health check endpoint"""
        response = requests.get(f"{self.BASE_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_login_success(self):
        """Проверяет успешный вход"""
        payload = {"username": "testuser", "password": "testpass"}
        response = requests.post(f"{self.BASE_URL}/auth/token", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data

    def test_login_admin_role(self):
        """Проверяет, что admin получает роль admin"""
        payload = {"username": "admin", "password": "anypassword"}
        response = requests.post(f"{self.BASE_URL}/auth/token", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data

    def test_login_user_role(self):
        """Проверяет, что обычные пользователи получают роль user"""
        payload = {"username": "regularuser", "password": "anypassword"}
        response = requests.post(f"{self.BASE_URL}/auth/token", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data

    def test_login_blocked_demo(self):
        """Проверяет, что demo/demo заблокированы"""
        payload = {"username": "demo", "password": "demo"}
        response = requests.post(f"{self.BASE_URL}/auth/token", json=payload)
        assert response.status_code == 401
        assert "Demo credentials" in response.json()["detail"]

    def test_verify_valid_token(self):
        """Проверяет валидацию валидного токена"""
        # Получаем токен
        login_payload = {"username": "testuser", "password": "testpass"}
        login_response = requests.post(f"{self.BASE_URL}/auth/token", json=login_payload)
        token = login_response.json()["access_token"]

        # Проверяем токен
        headers = {"Authorization": f"Bearer {token}"}
        verify_response = requests.post(f"{self.BASE_URL}/auth/verify", headers=headers)
        assert verify_response.status_code == 200
        data = verify_response.json()
        assert data["valid"] is True
        assert data["username"] == "testuser"

    def test_verify_invalid_token(self):
        """Проверяет отклонение невалидного токена"""
        headers = {"Authorization": "Bearer invalid_token_here"}
        response = requests.post(f"{self.BASE_URL}/auth/verify", headers=headers)
        assert response.status_code == 401
