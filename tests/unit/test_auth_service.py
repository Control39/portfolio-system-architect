import os
import sys

import pytest

# Настройка пути к проекту
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

# Установка секрета для JWT
os.environ["JWT_SECRET"] = "test-secret-key-for-unit-tests"

from fastapi.testclient import TestClient

from apps.auth_service.main import app

client = TestClient(app)


@pytest.fixture
def demo_token():
    """Фикстура для получения валидного access token."""
    response = client.post(
        "/auth/token",
        json={"username": "test_user", "password": "test_pass"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["expires_in"] == 24 * 3600
    token = data["access_token"]
    # Проверка формата JWT: header.payload.signature
    assert len(token.split(".")) == 3
    return token


@pytest.fixture
def any_user_token():
    """Фикстура для пользователя user1."""
    response = client.post(
        "/auth/token",
        json={"username": "user1", "password": "pass"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    return data["access_token"]


# === Тесты ===


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "auth-service"


def test_login_demo(demo_token):
    # Фикстура уже проверила логин, но можно дополнительно убедиться
    assert isinstance(demo_token, str)


def test_login_any(any_user_token):
    assert isinstance(any_user_token, str)


def test_login_invalid():
    response = client.post("/auth/token", json={"username": "", "password": ""})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


def test_verify_token(demo_token):
    response = client.post(
        "/auth/verify",
        headers={"Authorization": f"Bearer {demo_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True
    assert data["username"] == "test_user"
    assert data["role"] == "user"


def test_verify_invalid_token():
    response = client.post(
        "/auth/verify",
        headers={"Authorization": "Bearer invalid-token"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "Auth Service"
