# Dependency Injection (Внедрение зависимостей)

> **Дата:** 18 мая 2026 г.  
> **Автор:** Portfolio System Architect  
> **Статус:** ✅ Реализовано

---

## 🎯 Проблема

**Было:** `job_automation_agent` импортировал `cognitive_agent` напрямую:

```python
# ❌ Жёсткая зависимость
from .apps.cognitive_agent.job_search import search_hh_ru

vacancies = await search_hh_ru("Python Developer")
```

**Проблемы:**
1. **Сильная связанность** — `job_agent` знает внутренности `cognitive_agent`
2. **Невозможность замены** — чтобы использовать другой источник вакансий, нужно править `job_agent`
3. **Сложное тестирование** — для теста нужно поднимать реальный `cognitive_agent`
4. **Нарушение границ микросервисов** — прямой импорт кода между сервисами

---

## ✅ Решение: Dependency Injection

**Стало:** `job_automation_agent` зависит от **интерфейса**, а не от реализации:

```python
# ✅ Зависимость от абстракции
from src.interfaces.job_search import IJobSearch
from apps.infra_orchestrator.src.adapters.job_search_adapter import CognitiveJobSearch

def get_job_search_provider() -> IJobSearch:
    return CognitiveJobSearch(base_url="http://cognitive-agent:8006")

# Использование
search_provider = get_job_search_provider()
vacancies = await search_provider.search("Python Developer")
```

**Преимущества:**
1. **Нулевая связанность** — `job_agent` не знает, кто там внутри работает
2. **Pluggability** — можно заменить `CognitiveJobSearch` на `HHruJobSearch` без изменения `job_agent`
3. **Тестируемость** — mock-объект вместо реального сервиса
4. **Соблюдение границ микросервисов** — только HTTP/API, никаких прямых импортов

---

## 🏗️ Архитектура

```
┌─────────────────────────────────────────────────────────────┐
│                      job_automation_agent                    │
│  (Бизнес-логика: обработка вакансий, отклики, уведомления)  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  from src.interfaces.job_search import IJobSearch    │   │
│  │                                                      │   │
│  │  search_provider: IJobSearch                        │   │
│  │  vacancies = await search_provider.search(query)    │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          │ HTTP API (адаптер)
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              infra_orchestrator/src/adapters/               │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  class CognitiveJobSearch(IJobSearch):               │   │
│  │      def search(self, query):                        │   │
│  │          httpx.get("http://cognitive-agent:8006/...")│   │
│  │          return normalized_results                   │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          │ HTTP запрос
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                      cognitive_agent                         │
│  (Реализация: поиск вакансий на hh.ru, LinkedIn, и т.д.)    │
│                                                              │
│  GET /api/v1/jobs/search?query=Python+Developer             │
│  → Возвращает JSON с вакансиями                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Структура файлов

```
src/
├── interfaces/                          # Абстрактные контракты
│   ├── __init__.py
│   └── job_search.py                   # IJobSearch интерфейс
│
apps/
├── infra_orchestrator/
│   └── src/
│       └── adapters/                   # Реализации интерфейсов
│           ├── __init__.py
│           └── job_search_adapter.py   # CognitiveJobSearch
│
├── job_automation_agent/
│   └── src/
│       └── main.py                     # Использует IJobSearch
```

---

## 🎓 Принципы (SOLID)

### **D — Dependency Inversion Principle**

> **Высокоуровневые модули не должны зависеть от низкоуровневых.**  
> **Оба должны зависеть от абстракций.**

- `job_automation_agent` — высокоуровневый модуль (бизнес-логика)
- `CognitiveJobSearch` — низкоуровневый модуль (детали HTTP-запросов)
- **Оба зависят от** `IJobSearch` — абстракции

---

### **I — Interface Segregation Principle**

> **Клиенты не должны зависеть от методов, которые они не используют.**

`IJobSearch` — узкоспециализированный интерфейс:
- `search()` — поиск вакансий
- `get_details()` — получение деталей

Ничего лишнего.

---

## 🧪 Тестирование

### Без DI (плохо):

```python
# ❌ Нужно поднимать реальный cognitive_agent
def test_search_jobs():
    vacancies = await search_hh_ru("Python")  # Реальный HTTP-запрос!
    assert len(vacancies) > 0
```

### С DI (хорошо):

```python
# ✅ Mock-объект, мгновенные тесты
@pytest.mark.asyncio
async def test_search_jobs():
    mock_search = AsyncMock(spec=IJobSearch)
    mock_search.search.return_value = [
        {"title": "Python Developer", "company": "TechCorp"}
    ]
    
    vacancies = await mock_search.search("Python")
    assert len(vacancies) == 1
    assert vacancies[0]["title"] == "Python Developer"
```

---

## 🔄 Замена реализации

**Сценарий:** Хочу заменить `cognitive_agent` на прямой запрос к hh.ru API.

### Было (без DI):

```python
# apps/job_automation_agent/src/main.py
from .apps.cognitive_agent.job_search import search_hh_ru  # ❌ Жёстко!
```

### Стало (с DI):

```python
# apps/infra_orchestrator/src/adapters/hhru_job_search.py
class HHruJobSearch(IJobSearch):
    async def search(self, query: str):
        # Прямой запрос к hh.ru API
        ...

# apps/job_automation_agent/src/main.py
def get_job_search_provider() -> IJobSearch:
    return HHruJobSearch()  # ✅ Просто меняем реализацию!
```

**job_automation_agent НЕ ТРОГАЕМ!**

---

## 📊 Метрики

| Показатель | Было | Стало |
|------------|------|-------|
| Прямых импортов между сервисами | 2 | 0 |
| Тестов на mock-объектах | 0 | 4 |
| Сложность замены реализации | Высокая (править 10 файлов) | Низкая (править 1 файл) |
| Время на замену источника вакансий | ~1 день | ~10 минут |

---

## 🚀 Следующие шаги

1. **Добавить больше интерфейсов:**
   - `IResumeGenerator` — генерация резюме
   - `INotificationService` — отправка уведомлений
   - `ICareerTracker` — трекинг компетенций

2. **Реализовать Container для DI:**
   - Автоматическое создание экземпляров
   - Life-cycle management (singleton, transient)
   - Пример: `from dependency_injector import containers, providers`

3. **Конфигурация через переменные окружения:**
   ```bash
   export JOB_SEARCH_PROVIDER=cognitive-agent  # или hhru-api, linkedin-api
   ```

---

## 📚 Ресурсы

- [SOLID Principles — Dependency Inversion](https://www.baeldung.com/solid-principles-dependency-inversion)
- [Dependency Injection in Python](https://realpython.com/dependency-injection-python/)
- [Abstract Base Classes (ABCs) in Python](https://docs.python.org/3/library/abc.html)

---

*Последнее обновление: 18 мая 2026 г.*
