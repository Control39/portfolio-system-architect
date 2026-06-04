"""Тесты для Infrastructure Orchestrator API"""

from fastapi.testclient import TestClient
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from apps.infra_orchestrator.src.api.app import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200


def test_ready():
    response = client.get("/ready")
    assert response.status_code == 200


def test_create_service():
    service_data = {"name": "Test Service", "version": "1.0.0", "port": 8080, "enabled": True}
    response = client.post("/services", json=service_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Service"
    assert "id" in data


def test_list_services():
    response = client.get("/services")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_service():
    service_data = {"name": "Get Test", "version": "1.0", "port": 8081}
    create_response = client.post("/services", json=service_data)
    service_id = create_response.json()["id"]

    response = client.get(f"/services/{service_id}")
    assert response.status_code == 200
    assert response.json()["id"] == service_id
