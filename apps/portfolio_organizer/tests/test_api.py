"""API tests for portfolio_organizer."""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.main import app

client = TestClient(app)

def test_health():
    """Test health endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json().get("status") == "healthy"

def test_ready():
    """Test ready endpoint."""
    response = client.get("/api/ready")
    assert response.status_code == 200

def test_live():
    """Test live endpoint."""
    response = client.get("/api/live")
    assert response.status_code == 200

def test_projects_list():
    """Test get projects list."""
    response = client.get("/api/projects")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_portfolio_analysis():
    """Test portfolio analysis."""
    response = client.get("/api/portfolio/analysis")
    assert response.status_code == 200
    data = response.json()
    assert "technologies" in data or "analysis" in data

def test_project_detail():
    """Test get single project."""
    response = client.get("/api/projects/1")
    assert response.status_code in [200, 404]
