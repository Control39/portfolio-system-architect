from fastapi.testclient import TestClient

from apps.ml_model_registry.src.api.main import app

client = TestClient(app)


def test_health():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "ml-model-registry"


def test_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "ML Model Registry"
    assert data["version"] == "1.0.0"
