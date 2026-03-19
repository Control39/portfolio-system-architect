import pytest
import requests

@pytest.mark.e2e
def test_thought_architecture_api():
    response = requests.get("http://localhost:8005/health")  # Assume port
    assert response.status_code == 200
