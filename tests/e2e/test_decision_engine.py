import pytest
import requests


@pytest.mark.e2e
def test_decision_engine_api():
    response = requests.get("http://localhost:8001/reason", timeout=5)  # Assume
    assert response.status_code == 200
    assert "reasoning" in response.json()


