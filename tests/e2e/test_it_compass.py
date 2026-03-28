import pytest
import requests
from playwright.sync_api import expect

@pytest.mark.e2e
def test_it_compass_ui(page):
    page.goto("http://localhost:8501")
    expect(page).to_have_title("IT-Compass")  # Assume title
    expect(page.locator("h1")).to_be_visible()

@pytest.mark.e2e
def test_it_compass_api(page):
    response = requests.get("http://localhost:8501/health", timeout=5)  # Assume endpoint
    assert response.status_code == 200

