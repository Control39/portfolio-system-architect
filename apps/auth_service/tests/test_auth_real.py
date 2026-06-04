"""
Реальные тесты для auth_service (не шаблоны!)

Покрытие:
- JWT token creation
- Token verification
- Role-based access
- Error handling
"""

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import jwt
import pytest


# Добавляем корень проекта в PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent / ".." / ".." / ".."))

from apps.auth_service.main import (
    JWT_ALGORITHM,
    JWT_EXPIRATION_HOURS,
    JWT_SECRET,
    app,
    create_token,
    verify_token,
)


class TestJWTTokenCreation:
    """Тесты создания JWT токенов"""

    def test_create_token_with_username(self):
        """Создание токена для обычного пользователя"""
        token_data = create_token("testuser", "user")

        assert "access_token" in token_data
        assert token_data["token_type"] == "bearer"
        assert token_data["expires_in"] == JWT_EXPIRATION_HOURS * 3600

        # Декодируем токен для проверки payload
        decoded = jwt.decode(token_data["access_token"], JWT_SECRET, algorithms=[JWT_ALGORITHM])
        assert decoded["username"] == "testuser"
        assert decoded["role"] == "user"
        assert "iat" in decoded
        assert "exp" in decoded

    def test_create_token_with_admin_role(self):
        """Создание токена для администратора"""
        token_data = create_token("admin", "admin")

        decoded = jwt.decode(token_data["access_token"], JWT_SECRET, algorithms=[JWT_ALGORITHM])
        assert decoded["username"] == "admin"
        assert decoded["role"] == "admin"

    def test_token_expiration_is_correct(self):
        """Проверка срока действия токена"""
        token_data = create_token("testuser", "user")
        decoded = jwt.decode(token_data["access_token"], JWT_SECRET, algorithms=[JWT_ALGORITHM])

        exp_time = datetime.fromtimestamp(decoded["exp"], tz=timezone.utc)
        iat_time = datetime.fromtimestamp(decoded["iat"], tz=timezone.utc)

        diff = exp_time - iat_time
        assert diff == timedelta(hours=JWT_EXPIRATION_HOURS)

    def test_token_is_valid_jwt_format(self):
        """Проверка, что токен валидный JWT"""
        token_data = create_token("testuser", "user")

        # Не должно выбрасывать исключения
        decoded = jwt.decode(token_data["access_token"], JWT_SECRET, algorithms=[JWT_ALGORITHM])

        assert isinstance(decoded, dict)
        assert "username" in decoded
        assert "role" in decoded


class TestJWTTokenVerification:
    """Тесты верификации токенов"""

    def test_verify_valid_token(self):
        """Верификация валидного токена"""
        token_data = create_token("testuser", "user")
        token = token_data["access_token"]

        # Создаём mock credentials
        class MockCredentials:
            credentials = token

        result = verify_token(MockCredentials())
        assert result["username"] == "testuser"
        assert result["role"] == "user"

    def test_verify_admin_token(self):
        """Верификация токена администратора"""
        token_data = create_token("admin", "admin")
        token = token_data["access_token"]

        class MockCredentials:
            credentials = token

        result = verify_token(MockCredentials())
        assert result["username"] == "admin"
        assert result["role"] == "admin"

    def test_verify_expired_token_fails(self):
        """Верификация истёкшего токена должна падать"""
        # Создаём токен с истёкшим сроком
        expired_payload = {
            "username": "testuser",
            "role": "user",
            "iat": datetime.now(timezone.utc) - timedelta(hours=2),
            "exp": datetime.now(timezone.utc) - timedelta(hours=1),
        }
        expired_token = jwt.encode(expired_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

        class MockCredentials:
            credentials = expired_token

        with pytest.raises(Exception) as exc_info:
            verify_token(MockCredentials())

        assert "Token expired" in str(exc_info.value)

    def test_verify_invalid_token_fails(self):
        """Верификация невалидного токена должна падать"""

        class MockCredentials:
            credentials = "invalid.token.here"

        with pytest.raises(Exception) as exc_info:
            verify_token(MockCredentials())

        assert "Invalid token" in str(exc_info.value)

    def test_verify_token_with_tampered_signature(self):
        """Верификация токена с подделанной подписью"""
        token_data = create_token("testuser", "user")
        parts = token_data["access_token"].split(".")

        # Подделываем payload
        import base64

        tampered_payload = (
            base64.urlsafe_b64encode(b'{"username": "hacker", "role": "admin"}')
            .rstrip(b"=")
            .decode()
        )

        tampered_token = f"{parts[0]}.{tampered_payload}.{parts[2]}"

        class MockCredentials:
            credentials = tampered_token

        with pytest.raises(Exception) as exc_info:
            verify_token(MockCredentials())

        assert "Invalid token" in str(exc_info.value)


class TestRoleBasedAccess:
    """Тесты ролевой модели"""

    def test_admin_role_in_token(self):
        """Проверка роли admin в токене"""
        token_data = create_token("admin", "admin")
        decoded = jwt.decode(token_data["access_token"], JWT_SECRET, algorithms=[JWT_ALGORITHM])
        assert decoded["role"] == "admin"

    def test_user_role_in_token(self):
        """Проверка роли user в токене"""
        token_data = create_token("regularuser", "user")
        decoded = jwt.decode(token_data["access_token"], JWT_SECRET, algorithms=[JWT_ALGORITHM])
        assert decoded["role"] == "user"

    def test_different_roles_produce_different_tokens(self):
        """Разные роли создают разные токены"""
        admin_token = create_token("admin", "admin")["access_token"]
        user_token = create_token("user", "user")["access_token"]

        assert admin_token != user_token

        # Декодируем и сравниваем роли
        admin_decoded = jwt.decode(admin_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_decoded = jwt.decode(user_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

        assert admin_decoded["role"] == "admin"
        assert user_decoded["role"] == "user"


class TestAPIEndpoints:
    """Тесты API эндпоинтов (FastAPI TestClient)"""

    @pytest.fixture
    def client(self):
        from fastapi.testclient import TestClient

        return TestClient(app)

    def test_health_endpoint(self, client):
        """Тест health check эндпоинта"""
        response = client.get("/health")
        assert response.status_code == 200
        assert "status" in response.json()

    def test_health_endpoint_details(self, client):
        """Тест health check с проверкой service name"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "auth-service"

    def test_token_endpoint_with_valid_credentials(self, client):
        """Получение токена с валидными учётными данными"""
        response = client.post("/auth/token", json={"username": "testuser", "password": "testpass"})
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] == JWT_EXPIRATION_HOURS * 3600

    def test_token_endpoint_with_user1(self, client):
        """Получение токена для user1"""
        response = client.post("/auth/token", json={"username": "user1", "password": "pass"})
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_token_endpoint_blocks_demo_demo(self, client):
        """Блокировка демо-учётных данных"""
        response = client.post("/auth/token", json={"username": "demo", "password": "demo"})
        assert response.status_code == 401
        assert "Demo credentials" in response.json()["detail"]

    def test_token_endpoint_rejects_empty_password(self, client):
        """Отклонение пустого пароля"""
        response = client.post("/auth/token", json={"username": "testuser", "password": ""})
        assert response.status_code == 401

    def test_token_endpoint_rejects_invalid_credentials(self, client):
        """Отклонение невалидных учётных данных"""
        response = client.post("/auth/token", json={"username": "", "password": ""})
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid credentials"

    def test_verify_endpoint_with_valid_token(self, client):
        """Верификация валидного токена через API"""
        # Сначала получаем токен
        token_response = client.post(
            "/auth/token", json={"username": "testuser", "password": "testpass"}
        )
        token = token_response.json()["access_token"]

        # Верифицируем через endpoint
        response = client.post(
            "/auth/verify",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert data["username"] == "testuser"
        assert data["role"] == "user"

    def test_verify_endpoint_with_invalid_token(self, client):
        """Верификация невалидного токена через API"""
        response = client.post(
            "/auth/verify",
            headers={"Authorization": "Bearer invalid-token"},
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid token"

    def test_root_endpoint(self, client):
        """Тест корневого эндпоинта"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "Auth Service"


class TestEdgeCases:
    """Граничные случаи"""

    def test_token_with_special_characters_in_username(self):
        """Токен с спецсимволами в имени пользователя"""
        token_data = create_token("user@domain.com", "user")
        decoded = jwt.decode(token_data["access_token"], JWT_SECRET, algorithms=[JWT_ALGORITHM])
        assert decoded["username"] == "user@domain.com"

    def test_token_with_unicode_username(self):
        """Токен с Unicode в имени пользователя"""
        token_data = create_token("пользователь", "user")
        decoded = jwt.decode(token_data["access_token"], JWT_SECRET, algorithms=[JWT_ALGORITHM])
        assert decoded["username"] == "пользователь"

    def test_token_payload_size(self):
        """Проверка размера payload токена"""
        token_data = create_token("testuser", "user")
        token = token_data["access_token"]

        # JWT не должен быть слишком большим (< 8KB)
        assert len(token) < 8192

    def test_multiple_tokens_same_user_are_different(self):
        """Разные токены для одного пользователя (разные сессии)"""
        import time

        token1 = create_token("testuser", "user")["access_token"]
        time.sleep(1.1)  # Ждём, чтобы iat отличался
        token2 = create_token("testuser", "user")["access_token"]

        # Токены должны отличаться (разное iat/exp)
        assert token1 != token2
