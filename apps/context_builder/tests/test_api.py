# apps/context_builder/tests/test_api.py

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_ready():
    response = client.get("/ready")
    assert response.status_code == 200


def test_get_filter():
    response = client.get("/filter")
    assert response.status_code == 200
    assert "extensions" in response.json()


def test_update_filter():
    response = client.post("/filter", json={"add_extensions": ["xyz"], "add_exclude_dirs": ["temp"]})
    assert response.status_code == 200
    data = response.json()
    assert "xyz" in data["extensions"]
    assert "temp" in data["excluded_dirs"]


def test_build_context():
    response = client.post("/build", json={"structure_only": True})
    assert response.status_code == 200
    assert "СТРУКТУРА ПРОЕКТА" in response.text


def test_build_json():
    response = client.post("/build/json", json={"structure_only": True})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "files" in data["context"]


def test_build_chunked_disabled():
    response = client.post("/build/chunked", json={})
    assert response.status_code == 400  # Disabled by default


def test_get_structure():
    response = client.get("/structure")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "structure" in data
    assert len(data["structure"]) > 0
