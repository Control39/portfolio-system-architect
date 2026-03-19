import pytest
import requests

@pytest.mark.e2e
def test_career_development_api():
    response = requests.get("http://localhost:8000/health")
    assert response.status_code == 200
    assert response.json() is not None
