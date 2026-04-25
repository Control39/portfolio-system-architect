import pytest
import requests


@pytest.mark.e2e
def test_portfolio_organizer_api():
    response = requests.get("http://localhost:8004/health", timeout=5)
    assert response.status_code == 200
    assert response.json() is not None

