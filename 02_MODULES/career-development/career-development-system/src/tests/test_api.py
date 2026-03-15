import json
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from api.app import app
from pathlib import Path

client = TestClient(app)

# Create temp profile for testing
PROFILE_PATH = Path(__file__).parent.parent.parent / "user_profile.json"
PROFILE_DATA = {
    "username": "testuser",
    "skills": [
        {
            "name": "Python",
            "level": 3,
            "markers": [
                {"id": "marker1", "title": "Basics", "status": "completed"}
            ]
        }
    ]
}


def setup_module(module):
    PROFILE_PATH.write_text(json.dumps(PROFILE_DATA, indent=2), encoding="utf-8")


def teardown_module(module):
    PROFILE_PATH.unlink(missing_ok=True)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Career Development System API is running"}


def test_get_profile():
    response = client.get("/profile")
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"


def test_create_goal():
    goal = {
        "title": "Test Goal",
        "description": "Test",
        "target_date": "2025-01-01"
    }
    response = client.post("/goals", json=goal)
    assert response.status_code == 200
    assert response.json()["status"] == "created"


def test_update_marker():
    response = client.patch("/markers/marker1", json={"status": "in_progress"})
    assert response.status_code == 200
    # Note: json body not used in app, but for test assume query or adjust

