
---

### Файл 16: `apps/context_builder/tests/test_api.py`

```python
from fastapi.testclient import TestClient
from pathlib import Path
import sys
import tempfile

# Добавляем путь для импорта
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_get_filter():
    response = client.get("/filter")
    assert response.status_code == 200
    data = response.json()
    assert "extensions" in data
    assert "excluded_dirs" in data


def test_build_context():
    response = client.post("/build", json={
        "paths": ["."],
        "structure_only": True
    })
    assert response.status_code == 200
    assert "СТРУКТУРА ПРОЕКТА" in response.text


def test_get_structure():
    response = client.get("/structure")
    assert response.status_code == 200
    data = response.json()
    assert "success" in data
    assert "structure" in data


def test_build_context_to_file():
    response = client.post("/build/file", json={
        "paths": ["."],
        "structure_only": True
    })
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "file_path" in data