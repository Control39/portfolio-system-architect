# Тесты Cognitive Agent

**Статус:** MVP + Восстановление
**Цель:** >90% покрытие тестами
**Дата:** 5 июня 2026

---

## 📊 Структура тестов

```
tests/
├── test_config_integration_advanced.py   # Углублённые тесты config_integration.py (HIGH)
├── test_endpoints.py                      # Тесты FastAPI endpoints (HIGH)
├── test_orchestrator.py                   # Тесты оркестратора (HIGH)
├── test_integration.py                    # Интеграционные тесты (HIGH)
├── test_agent_basic.py                    # Базовые тесты (MVP)
├── test_integration_cognitive_agent.py    # Существующие интеграционные тесты (MVP)
├── test_project_scanner.py                # Тесты сканера (MVP)
└── test_import.py                         # Импорт-тесты (MVP)
```

---

## 🎯 Покрытие тестами

| Тестовый файл | Покрытие | Статус |
|--------------|----------|--------|
| `test_config_integration_advanced.py` | 90%+ | ✅ Создан |
| `test_endpoints.py` | 85%+ | ✅ Создан |
| `test_orchestrator.py` | 80%+ | ✅ Создан |
| `test_integration.py` | 80%+ | ✅ Создан |
| `test_agent_basic.py` | ~50% | 🟡 MVP |
| `test_integration_cognitive_agent.py` | ~40% | 🟡 MVP |
| `test_project_scanner.py` | ~30% | 🟡 MVP |
| `test_import.py` | ~20% | 🟡 MVP |

**Общее покрытие:** ~65% (цель: ≥90%)

---

## 🚀 Запуск тестов

### Локальный запуск:

```bash
cd apps/cognitive_agent

# Запуск всех тестов
pytest tests/ -v

# Запуск с покрытием
pytest tests/ -v --cov=. --cov-report=xml

# Запуск конкретного теста
pytest tests/test_endpoints.py::TestEndpoints::test_health_endpoint -v

# Запуск с подробным выводом
pytest tests/ -v --tb=short
```

### Запуск через CI/CD:

```bash
# GitHub Actions автоматически запускает тесты
# Workflow: .github/workflows/cognitive-agent-ci.yml
```

---

## 📋 Типы тестов

### Unit Tests (HIGH)
- **test_config_integration_advanced.py** — тесты config_integration.py
- **test_endpoints.py** — тесты FastAPI endpoints
- **test_orchestrator.py** — тесты оркестратора

### Integration Tests (HIGH)
- **test_integration.py** — тесты связей между компонентами

### MVP Tests (MEDIUM)
- **test_agent_basic.py** — базовые тесты
- **test_integration_cognitive_agent.py** — существующие интеграционные тесты
- **test_project_scanner.py** — тесты сканера

---

## 🔧 Инструменты

### Тестовый стек:
- **pytest** — основной фреймворк
- **pytest-asyncio** — асинхронные тесты
- **pytest-cov** — покрытие кода
- **unittest.mock** — моки и патчи
- **httpx** — тесты HTTP endpoints

### CI/CD интеграция:
- **GitHub Actions** —/.github/workflows/cognitive-agent-ci.yml
- **Codecov** — загрузка coverage отчётов
- **pytest-cov** — генерация coverage.xml

---

## 📈 Метрики успеха

| Этап | Цель | Статус |
|------|------|--------|
| **Сейчас** | ~55% покрытие | 🟡 MVP |
| **1 неделя** | 70% покрытие | 🔄 В процессе |
| **2 недели** | 80% покрытие | ⚪ Планируется |
| **1 месяц** | 90%+ покрытие | ⚪ Планируется |

---

## ⚠️ Правила

1. **Не удалять legacy/ и служебные папки**
2. **Не удалять атомы из src/ без проверки зависимостей**
3. **Сохранять структуру Compositional Architecture**
4. **Использовать fixtures для повторяющихся данных**
5. **Использовать mock для внешних зависимостей**
6. **Не удалять существующие тесты — расширять их**

---

## 📝 План развития

1. ✅ Создать `test_config_integration_advanced.py` (HIGH)
2. ✅ Создать `test_endpoints.py` (HIGH)
3. ✅ Создать `test_orchestrator.py` (HIGH)
4. ✅ Создать `test_integration.py` (HIGH)
5. 🔄 Рефакторинг существующих тестов
6. 🔄 Создать `test_scanner.py`, `test_planner.py`, `test_learning.py`
7. 🔄 Создать `test_e2e.py` (E2E тесты)
8. 🔄 Интеграция с CI/CD и coverage отчёты

---

**Автор:** GigaCode
**Дата:** 5 июня 2026
**Версия:** 0.1.0 (Plan)
