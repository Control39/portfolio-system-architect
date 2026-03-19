import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from apps.cloud_reason.cloud_reason.api.endpoints import app

client = TestClient(app)

def test_health():
    response = client.get("/")
    assert response.status_code == 200
    assert "health" in response.json()

@patch('apps.cloud_reason.api.endpoints.git')
def test_reasoning(mock_git):
    mock_git.Repo.return_value = MagicMock()
    response = client.post("/reason", json={"repo": "test"})
    assert response.status_code == 200
