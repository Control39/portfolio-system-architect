import pytest
import requests

@pytest.mark.e2e
def test_cloud_reason_api():
    response = requests.get("http://localhost:8001/reason")  # Assume
    assert response.status_code == 200
    assert "reasoning" in response.json()

