"""Тесты для Thought Architecture API"""

from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Добавляем корень репозитория в путь
REPO_ROOT = Path(__file__).parent.parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Импортируем через полный путь от корня
from apps.thought_architecture.src.api.app import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200


def test_ready():
    response = client.get("/ready")
    assert response.status_code == 200


def test_live():
    response = client.get("/live")
    assert response.status_code == 200


def test_create_decision():
    decision_data = {"title": "Test Decision", "description": "Test Description"}
    response = client.post("/decisions", json=decision_data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Decision"
    assert "id" in data


def test_get_decision():
    decision_data = {"title": "Get Test", "description": "For get test"}
    create_response = client.post("/decisions", json=decision_data)
    decision_id = create_response.json()["id"]

    response = client.get(f"/decisions/{decision_id}")
    assert response.status_code == 200
    assert response.json()["id"] == decision_id


def test_update_decision():
    decision_data = {"title": "Update Test", "description": "Original"}
    create_response = client.post("/decisions", json=decision_data)
    decision_id = create_response.json()["id"]

    update_data = {"title": "Updated Title"}
    response = client.put(f"/decisions/{decision_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Title"


def test_delete_decision():
    decision_data = {"title": "Delete Test", "description": "To be deleted"}
    create_response = client.post("/decisions", json=decision_data)
    decision_id = create_response.json()["id"]

    response = client.delete(f"/decisions/{decision_id}")
    assert response.status_code == 200

    get_response = client.get(f"/decisions/{decision_id}")
    assert get_response.status_code == 404


def test_approve_decision():
    decision_data = {"title": "Approve Test", "description": "To be approved"}
    create_response = client.post("/decisions", json=decision_data)
    decision_id = create_response.json()["id"]

    response = client.put(f"/decisions/{decision_id}/approve?approver=architect")
    assert response.status_code == 200
    assert response.json()["status"] == "approved"


def test_reject_decision():
    decision_data = {"title": "Reject Test", "description": "To be rejected"}
    create_response = client.post("/decisions", json=decision_data)
    decision_id = create_response.json()["id"]

    response = client.put(f"/decisions/{decision_id}/reject?reason=Too expensive")
    assert response.status_code == 200
    assert response.json()["status"] == "rejected"
