"""Business logic tests for thought_architecture."""

from fastapi.testclient import TestClient
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from apps.thought_architecture.src.api.app import app

client = TestClient(app)


def test_decision_workflow():
    """Test complete decision workflow."""
    # Create
    create_response = client.post(
        "/decisions", json={"title": "Workflow Test", "description": "Test workflow"}
    )
    assert create_response.status_code == 200
    decision_id = create_response.json()["id"]

    # Approve
    approve_response = client.put(f"/decisions/{decision_id}/approve?approver=tester")
    assert approve_response.status_code == 200

    # Verify
    get_response = client.get(f"/decisions/{decision_id}")
    assert get_response.json()["status"] == "approved"


def test_decision_rejection():
    """Test decision rejection."""
    create_response = client.post(
        "/decisions", json={"title": "Rejection Test", "description": "Should be rejected"}
    )
    decision_id = create_response.json()["id"]

    reject_response = client.put(f"/decisions/{decision_id}/reject?reason=Not good")
    assert reject_response.status_code == 200
    assert reject_response.json()["status"] == "rejected"
