import pytest
import requests


@pytest.mark.e2e
def test_ml_model_registry_api():
    response = requests.get("http://localhost:8002/health", timeout=5)
    assert response.status_code == 200
    assert response.json() is not None
