import sys
from pathlib import Path
from unittest.mock import MagicMock, patch


# Добавляем корень проекта в путь
ROOT_DIR = Path(__file__).parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from fastapi.testclient import TestClient  # noqa: E402

from apps.decision_engine.decision_engine.api.endpoints import app  # noqa: E402


client = TestClient(app)


def test_health():
    response = client.get("/")
    assert response.status_code == 200
    assert "health" in response.json()


@patch("apps.decision_engine.decision_engine.api.endpoints.git")
def test_reasoning(mock_git):
    mock_git.Repo.return_value = MagicMock()
    response = client.post("/reason", json={"repo": "test"})
    assert response.status_code == 200
