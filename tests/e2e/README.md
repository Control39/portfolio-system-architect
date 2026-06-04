# 🧪 E2E Тесты

## ⚠️ Важно

Эти тесты **требуют запущенных сервисов**. Не запускай их локально без Docker!

## 🏗️ Архитектура тестов

### Атомы vs Молекулы

| Тип | Где тестировать | Пример |
|-----|----------------|--------|
| **Атомы** (`src/`) | `tests/unit/` | SecretManager, SecurityScanner |
| **Молекулы** (`apps/`) | `apps/<service>/tests/` | unit тесты каждого сервиса |
| **E2E** (API) | `tests/e2e/` | Интеграция сервисов через HTTP |

## 📋 Список тестов

| Файл | Сервис | Порт | Статус |
|------|--------|------|--------|
| `test_infra_orchestrator.py` | Infra Orchestrator | 8200 | ✅ Готов |
| `test_auth_service.py` | Auth Service | 8100 | ✅ Готов |
| `test_decision_engine.py` | Decision Engine | 8001 | ✅ Обновлён |
| `test_career_development.py` | Career Development | 8301 | ✅ Обновлён |
| `test_it_compass.py` | IT Compass | 8501 | ⚠️ Требуется Streamlit |
| `test_system_proof.py` | System Proof | - | ✅ Существующий |
| `test_portfolio_organizer.py` | Portfolio Organizer | - | ✅ Существующий |

## 🚀 Запуск тестов

### 1. Запусти сервисы через Docker

```bash
docker-compose up -d
```

### 2. Проверь, что сервисы работают

```bash
# Проверка Infra Orchestrator
curl http://localhost:8200/health

# Проверка Auth Service
curl http://localhost:8100/health

# Проверка Decision Engine
curl http://localhost:8001/health
```

### 3. Запусти e2e тесты

```bash
# Все e2e тесты
pytest tests/e2e/ -v -m e2e

# Только конкретный сервис
pytest tests/e2e/test_infra_orchestrator.py -v

# С покрытием
pytest tests/e2e/ -v --cov=tests/e2e
```

### 4. Пропусти тесты, если сервисы не запущены

```bash
# Запусти только unit тесты
pytest tests/unit/ -v

# Или пропусти e2e
pytest tests/ -v -m "not e2e"
```

## 📝 Написание новых e2e тестов

### Шаблон для Python сервиса (FastAPI)

```python
"""
E2E Тесты для <Service Name>

Service: apps/<service_name> (Python/FastAPI)
Port: <PORT>
Endpoints: /, /health, /api/v1/...
"""

import pytest
import requests


@pytest.mark.e2e
class Test<ServiceName>:
    """Тесты <Service Name> API"""

    BASE_URL = "http://localhost:<PORT>"

    def test_service_info(self):
        """Проверяет, что сервис отвечает на root endpoint"""
        response = requests.get(f"{self.BASE_URL}/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "<Service Name>"

    def test_health_check(self):
        """Проверяет health check endpoint"""
        response = requests.get(f"{self.BASE_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_custom_endpoint(self):
        """Проверяет кастомный endpoint"""
        payload = {"key": "value"}
        response = requests.post(
            f"{self.BASE_URL}/api/v1/custom",
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        assert "result" in data
```

## ❌ Что НЕ делать

### ❌ Не тестируй Python сервисы через PowerShell

```python
# НЕПРАВИЛЬНО ❌
def test_wrong():
    result = subprocess.run(
        ["pwsh", "-Command", "Import-Module ./apps/xyz/Module.psm1"],
        capture_output=True,
    )
    # Это не работает, потому что сервис Python!
```

### ❌ Не создавай тесты для несуществующих сервисов

```python
# НЕПРАВИЛЬНО ❌
def test_arch_compass():
    # Нет сервиса с таким именем!
```

### ❌ Не смешивай PowerShell атомы и Python сервисы

```python
# НЕПРАВИЛЬНО ❌
# PowerShell атомы → tests/unit/
# Python сервисы → tests/e2e/ (через HTTP API)
```

## 🔧 Тестирование PowerShell атомов

PowerShell модули из `src/` тестируются через **unit тесты**, не e2e:

```python
# tests/unit/security/test_secret_manager.py
import subprocess
import pytest


def test_secret_manager_import():
    """Проверяет, что SecretManager может быть импортирован"""
    result = subprocess.run(
        [
            "pwsh",
            "-Command",
            "Import-Module ./src/infrastructure/security/SecretManager.psm1 -Force; "
            "Get-Command SecretManager",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
```

## 📊 Результаты тестов

После запуска смотри статистику:

```bash
pytest tests/e2e/ -v --tb=short

# Пример вывода:
# ================= test session starts =================
# collected 15 items
#
# tests/e2e/test_infra_orchestrator.py::TestInfraOrchestrator::test_service_info PASSED
# tests/e2e/test_infra_orchestrator.py::TestInfraOrchestrator::test_health_check PASSED
# tests/e2e/test_auth_service.py::TestAuthService::test_login_success PASSED
# ...
#
# ================= 12 passed, 3 skipped in 5.23s =================
```

## 🎯 CI/CD

E2E тесты запускаются в GitHub Actions только на `main` ветке:

```yaml
# .github/workflows/e2e-tests.yml
name: E2E Tests

on:
  push:
    branches: [main]

jobs:
  e2e:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Start services
        run: docker-compose up -d
      - name: Run E2E tests
        run: pytest tests/e2e/ -v
```

## 📖 Дополнительная информация

- **Структура сервисов**: [`docs/SERVICE_STRUCTURE_STANDARD.md`](../../docs/SERVICE_STRUCTURE_STANDARD.md)
- **CI/CD**: [`docs/CI_CD_SERVICE_STRUCTURE.md`](../../docs/CI_CD_SERVICE_STRUCTURE.md)
- **Архитектура**: [`ARCHITECTURE.md`](../../ARCHITECTURE.md)

---

**Автор:** Koda AI
**Последнее обновление:** 2026-05-26
