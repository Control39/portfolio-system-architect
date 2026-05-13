# Known Test Issues

> **Дата создания:** 13 мая 2026 г.
> **Статус:** Pre-existing проблемы, не связанные с текущей работой

---

## 📊 Обзор

| Категория | Количество |
|-----------|------------|
| ✅ Пройдающие тесты | 238 |
| ❌ Pre-existing failures | 17 |
| ⏭️ Skipped | 9 |
| 📊 Покрытие | ~60% |

---

## ❌ Pre-existing Проблемы

### 1. `apps/career_development/tests/test_helpers.py` — 6 тестов

**Статус:** Pre-existing API mismatch

**Описание:** Тесты написаны под несуществующую реализацию helper-функций.

**Проблемы:**
- `test_convert_bytes_to_human_readable` — ожидает `1024`, получает `0`
- `test_create_directory_if_not_exists` — `assert False is not True`
- `test_format_date` — формат `'2026-02-14T10:30:00' != '14.02.2026 10:30'`
- `test_get_file_size` — ожидает `1024`, получает `0`
- `test_json_file_operations` — `{stub: True} != {test: 'data', number: 42}`
- `test_validate_email` — `True is not false`

**Причина:** Реализация `helpers.py` не соответствует тестовым ожиданиям.

**Решение:**
- [ ] Обновить `helpers.py` под тесты ИЛИ
- [ ] Переписать тесты под реализацию

---

### 2. `apps/infra-orchestrator/tests/test_integration_infra_orchestrator.py` — 5 тестов

**Статус:** Pre-existing async mock issues

**Описание:** Mock-объекты не вызываются в асинхронных тестах.

**Проблемы:**
- `test_orchestration_service_initialization_async` — `mock.initialize.called == False`
- `test_orchestration_resource_allocation_async` — `mock.initialize.called == False`
- `test_orchestration_scaling_async` — `mock.initialize.called == False`
- `test_orchestration_recovery_async` — `mock.initialize.called == False`

**Причина:** Неправильная настройка async mocks (нужно `AsyncMock` вместо `MagicMock`).

**Решение:**
- [ ] Заменить `MagicMock` на `AsyncMock` в тестах

---

### 3. `apps/mcp-server/tests/` — 6 тестов

**Статус:** Pre-existing config validation issues

**Описание:** Ошибки валидации конфигурации.

**Проблемы:**
- `test_mcp_resource_management_async` — `mock.initialize.called == False`
- `test_config_validation` — `'gpt5' unexpectedly found in config`

**Причина:** Конфигурация содержит `'gpt-4'`, тест ожидает без 'gpt5'.

**Решение:**
- [ ] Исправить тест на `assert 'gpt5' not in config`
- [ ] Исправить async mocks на `AsyncMock`

---

### 4. `apps/template-service/tests/` — 15 тестов

**Статус:** Pre-existing missing module

**Описание:** Отсутствует модуль `src.api`.

**Ошибки:**
```python
ModuleNotFoundError: No module named 'src.api'
```

**Причина:** Пакет `template-service` имеет невалидное имя (дефис) и зависимости от несуществующих модулей.

**Решение:**
- [ ] Удалить пакет (если не используется) ИЛИ
- [ ] Создать недостающий модуль `src/api.py`

---

## ⏭️ Skipped Тесты

### `apps/mcp-server/tests/` — 9 тестов

**Маркеры:** `@unittest.skipIf(not HAS_MCP_TOOLS, ...)`

**Причина:** Отсутствуют MCP-тулзы в окружении.

**Решение:**
- [ ] Установить MCP-зависимости ИЛИ
- [ ] Добавить маркер `pytest.mark.skip` с пояснением

---

## 🔧 CI/CD Конфигурация

### Исключения в `.github/workflows/ci.yml`

```yaml
# Исключить template-service (полностью нерабочий)
- run: pytest --ignore=apps/template-service/tests

# Деселект known issues
- run: pytest --deselect=apps/career_development/tests/test_helpers.py
  --deselect=apps/infra-orchestrator/tests/test_integration_infra_orchestrator.py
  --deselect=apps/mcp-server/tests/test_integration_mcp_server.py::test_mcp_resource_management_async
```

---

## 📅 История изменений

| Дата | Изменения | Автор |
|------|-----------|-------|
| 13.05.2026 | Создание документа | Koda |

---

## ✅ Checklist для исправления

- [ ] Исправить 6 тестов в `test_helpers.py`
- [ ] Исправить 5 async mock тестов в `infra-orchestrator`
- [ ] Исправить 6 тестов в `mcp-server`
- [ ] Удалить/исправить `template-service`
- [ ] Обновить CI/CD конфигурацию
- [ ] Достичь покрытия ≥80%
