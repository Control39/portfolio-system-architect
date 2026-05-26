# 🧪 Руководство по тестированию

> **Для ИИ-агентов и разработчиков: как правильно тестировать в архитектуре "Атомы и Молекулы"**

---

## 🎯 Основной принцип

| Тип компонента | Где тестировать | Как тестировать |
|----------------|----------------|-----------------|
| **Атомы** (`src/`) | `tests/unit/` | PowerShell: `Import-Module`, Python: `import` |
| **Молекулы** (`apps/`) | `apps/<service>/tests/` | Unit тесты сервиса |
| **E2E** (интеграция) | `tests/e2e/` | HTTP API запросы (`requests`) |

---

## ⚠️ КРИТИЧЕСКИЕ ПРАВИЛА (НЕ НАРУШАТЬ!)

### ❌ ЗАПРЕЩЕНО

1. **Тестировать Python сервисы через PowerShell**
   ```python
   # НЕПРАВИЛЬНО ❌
   def test_python_service_with_powershell():
       subprocess.run(["pwsh", "-Command", "Import-Module ./apps/infra_orchestrator/..."])
       # infra_orchestrator — Python/FastAPI, не PowerShell модуль!
   ```

2. **Создавать тесты для несуществующих сервисов**
   ```python
   # НЕПРАВИЛЬНО ❌
   def test_arch_compass():
       # Сервиса с таким именем нет в проекте!
   ```

3. **Смешивать PowerShell и Python в одном e2e тесте**
   ```python
   # НЕПРАВИЛЬНО ❌
   def test_mixed():
       # PowerShell атомы → unit тесты
       # Python сервисы → e2e тесты через HTTP
   ```

### ✅ ПРАВИЛЬНО

1. **Python сервисы тестируй через HTTP API**
   ```python
   # ПРАВИЛЬНО ✅
   def test_python_service():
       response = requests.get("http://localhost:8200/health")
       assert response.status_code == 200
   ```

2. **PowerShell атомы тестируй через Import-Module в unit тестах**
   ```python
   # ПРАВИЛЬНО ✅
   def test_powershell_atom():
       result = subprocess.run(
           ["pwsh", "-Command", "Import-Module ./src/security/SecretManager.psm1"],
           capture_output=True,
       )
       assert result.returncode == 0
   ```

3. **Проверяй существование сервиса перед созданием теста**
   ```bash
   # Проверь структуру
   ls apps/
   # Если сервиса нет — не создавай для него тест!
   ```

---

## 📋 Алгоритм создания e2e теста

### Шаг 1: Проверь, что сервис существует

```bash
# Проверь папку сервиса
ls apps/<service_name>/

# Ожидаемая структура:
# apps/<service_name>/
#   ├── main.py
#   ├── README.md
#   ├── Dockerfile
#   └── tests/
```

### Шаг 2: Определи порт и endpoints

```bash
# Посмотри main.py
cat apps/<service_name>/main.py

# Ищи:
# - app = FastAPI(...) или app = Flask(...)
# - @app.get("/") — root endpoint
# - @app.get("/health") — health check
# - @app.post("/api/...") — бизнес-логика
```

### Шаг 3: Создай тест по шаблону

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
        """Проверяет root endpoint"""
        response = requests.get(f"{self.BASE_URL}/")
        assert response.status_code == 200

    def test_health_check(self):
        """Проверяет health check"""
        response = requests.get(f"{self.BASE_URL}/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_custom_endpoint(self):
        """Проверяет кастомный endpoint"""
        # Реализуй под конкретный сервис
        pass
```

### Шаг 4: Сохрани в `tests/e2e/test_<service_name>.py`

```bash
# Название файла должно совпадать с именем сервиса
tests/e2e/test_infra_orchestrator.py
tests/e2e/test_auth_service.py
tests/e2e/test_decision_engine.py
```

---

## 🗂️ Карта сервисов и портов

| Сервис | Порт | Тип | E2E тест |
|--------|------|-----|----------|
| `infra_orchestrator` | 8200 | FastAPI | ✅ `test_infra_orchestrator.py` |
| `auth_service` | 8100 | FastAPI | ✅ `test_auth_service.py` |
| `decision_engine` | 8001 | FastAPI | ✅ `test_decision_engine.py` |
| `career_development` | 8301 | FastAPI | ✅ `test_career_development.py` |
| `it_compass` | 8501 | Streamlit | ⚠️ `test_it_compass.py` (UI) |
| `chat_backend` | 8005 | FastAPI | 🔄 TODO |
| `ai_config_manager` | 8000 | FastAPI | 🔄 TODO |
| `portfolio_organizer` | - | CLI | ✅ `test_portfolio_organizer.py` |
| `system_proof` | - | CLI | ✅ `test_system_proof.py` |

---

## 🧬 Тестирование Атомов (PowerShell)

PowerShell модули из `src/` — это **Атомы**. Тестируй их через **unit тесты**:

### Пример: SecretManager

```python
# tests/unit/security/test_secret_manager.py
import subprocess
import pytest


class TestSecretManager:
    """Тесты SecretManager (PowerShell атом)"""

    def test_module_import(self):
        """Проверяет импорт модуля"""
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

    def test_initialize_function(self):
        """Проверяет функцию Initialize"""
        result = subprocess.run(
            [
                "pwsh",
                "-Command",
                "Import-Module ./src/infrastructure/security/SecretManager.psm1 -Force; "
                "[SecretManager]::Initialize(@{ VaultType = 'Environment' }); "
                "Write-Output 'OK'",
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "OK" in result.stdout
```

---

## 🧪 Запуск тестов

### Все тесты

```bash
pytest tests/ -v
```

### Только e2e (требует запущенных сервисов)

```bash
pytest tests/e2e/ -v -m e2e
```

### Только unit (без запущенных сервисов)

```bash
pytest tests/unit/ -v
```

### Исключить e2e

```bash
pytest tests/ -v -m "not e2e"
```

### Конкретный сервис

```bash
pytest tests/e2e/test_infra_orchestrator.py -v
```

---

## 🔍 Отладка проблем

### Тест падает с "Connection refused"

**Проблема:** Сервис не запущен

**Решение:**
```bash
docker-compose up -d
docker-compose ps  # Проверь статус
```

### Тест падает с "Module not found"

**Проблема:** PowerShell модуль не найден

**Решение:**
```bash
# Проверь путь
Test-Path ./src/infrastructure/security/SecretManager.psm1

# Если файла нет — проверь, правильный ли путь
```

### Тест падает с "TypeNotFound" (PowerShell классы)

**Проблема:** Pester 3.4.0 не поддерживает PowerShell классы

**Решение:**
```powershell
# Установи Pester 5.x
Install-Module -Name Pester -RequiredVersion 5.3.0 -Force
```

Или закомментируй тест, пока Pester не обновлён:
```python
@pytest.mark.skip(reason="Requires Pester 5.x for PowerShell class support")
def test_powershell_class():
    ...
```

---

## 📖 Дополнительная документация

- **Архитектура**: [`ARCHITECTURE.md`](../ARCHITECTURE.md)
- **Структура сервисов**: [`SERVICE_STRUCTURE_STANDARD.md`](../SERVICE_STRUCTURE_STANDARD.md)
- **E2E тесты**: [`tests/e2e/README.md`](../tests/e2e/README.md)
- **CI/CD**: [`CI_CD_SERVICE_STRUCTURE.md`](../CI_CD_SERVICE_STRUCTURE.md)

---

## 🎯 Чек-лист перед созданием нового теста

- [ ] Сервис существует в `apps/<service_name>/`
- [ ] Я проверил `main.py` и узнал порт/endpoints
- [ ] Я использую `requests` для Python сервисов (не PowerShell!)
- [ ] Я использую `subprocess + pwsh` для PowerShell атомов
- [ ] Файл теста назван `test_<service_name>.py`
- [ ] Тест помечен `@pytest.mark.e2e`
- [ ] Я добавил тест в `tests/e2e/README.md`

---

**Автор:** Koda AI  
**Версия:** 1.0.0  
**Последнее обновление:** 2026-05-26
