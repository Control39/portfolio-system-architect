import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

os.environ["JWT_SECRET"] = "test-secret-key-for-unit-tests"

import pytest
from fastapi.testclient import TestClient
from apps.auth_service.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "auth-service"

def test_login_demo():
    response = client.post("/auth/token", json={"username": "demo", "password": "demo"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["expires_in"] == 24 * 3600

def test_login_any():
    response = client.post("/auth/token", json={"username": "user1", "password": "pass"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data

def test_login_invalid():
    response = client.post("/auth/token", json={"username": "", "password": ""})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"

def test_verify_token():
    # First get a token
    response = client.post("/auth/token", json={"username": "demo", "password": "demo"})
    token = response.json()["access_token"]
    # Verify
    response = client.post("/auth/verify", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True
    assert data["username"] == "demo"
    assert data["role"] == "admin"

def test_verify_invalid_token():
    response = client.post("/auth/verify", headers={"Authorization": "Bearer invalid"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "Auth Service"