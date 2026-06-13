"""API tests for portfolio_organizer."""

from fastapi.testclient import TestClient

from apps.portfolio_organizer.endpoints.routes import app

client = TestClient(app)


def test_health():
    """Test health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json().get("status") == "healthy"


def test_portfolio_creation():
    """Test portfolio creation."""
    response = client.post(
        "/portfolio",
        json={
            "owner_id": "550e8400-e29b-41d4-a716-446655440000",
            "name": "Test Portfolio",
            "compass_markers": ["marker-1", "marker-2"],
        },
    )
    assert response.status_code == 200
    assert "id" in response.json()


def test_project_creation():
    """Test project creation."""
    response = client.post(
        "/project",
        json={
            "portfolio_id": "550e8400-e29b-41d4-a716-446655440000",
            "name": "Test Project",
            "description": "Test description",
            "evidence_links": ["https://github.com/test"],
            "demonstrated_markers": ["marker-1"],
        },
    )
    assert response.status_code == 200
    assert "id" in response.json()
