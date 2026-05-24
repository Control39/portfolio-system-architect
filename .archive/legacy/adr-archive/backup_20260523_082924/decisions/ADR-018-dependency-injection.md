# ADR-018: Dependency Injection для взаимодействия между микросервисами

**Дата:** 18 мая 2026 г.  
**Статус:** ✅ Принято  
**Автор:** Ekaterina Kudelya (Control39)  
**Решение:** Dependency Injection через интерфейсы

---

## 📋 Контекст

Проект `portfolio-system-architect` состоит из 15 микросервисов, которые должны взаимодействовать друг с другом.

**Проблема обнаружена при проверке:**
- `job_automation_agent` напрямую импортировал код из `cognitive_agent`:
  ```python
  from .apps.cognitive_agent.job_search import search_hh_ru
  ```
- Это нарушает границы микросервисов и создаёт жёсткую связанность.

**Требования:**
1. Сервисы должны быть **независимы** от реализации друг друга
2. Возможность **замены реализации** без изменения кода потребителя
3. **Тестируемость** через mock-объекты
4. **Соблюдение границ** микросервисной архитектуры

---

## ⚖️ Рассмотренные варианты

### Вариант 1: Прямые импорты (отклонено)

```python
from .apps.cognitive_agent.job_search import search_hh_ru
```

**Плюсы:**
- Простота реализации
- Нет накладных расходов на сериализацию

**Минусы:**
- Нарушение границ микросервисов
- Жёсткая связанность
- Невозможность независимого деплоя
- Сложное тестирование (нужен реальный сервис)

**Причина отклонения:** Возврат к монолитной архитектуре, противоречит принципам микросервисов.

---

### Вариант 2: HTTP/gRPC вызовы без абстракции (отклонено)

```python
import httpx

async def search_jobs(query: str):
    response = await httpx.get("http://cognitive-agent:8006/search", params={"q": query})
    return response.json()
```

**Плюсы:**
- Соблюдение границ микросервисов
- Независимый деплой

**Минусы:**
- Детали HTTP-протокола размазаны по бизнес-логике
- При изменении API нужно править все места вызова
- Сложность рефакторинга

**Причина отклонения:** Отсутствие уровня абстракции усложняет поддержку и изменение реализации.

---

### Вариант 3: Dependency Injection через интерфейсы (выбрано)

```python
from src.interfaces.job_search import IJobSearch

class CognitiveJobSearch(IJobSearch):
    async def search(self, query: str):
        response = await httpx.get("http://cognitive-agent:8006/search", params={"q": query})
        return response.json()

# В потребителе
search_provider: IJobSearch = get_job_search_provider()
vacancies = await search_provider.search("Python")
```

**Плюсы:**
- Нулевая связанность между сервисами
- Легкая замена реализации (только один файл)
- Тестируемость через mock-объекты
- Соблюдение принципа Dependency Inversion (SOLID D)
- Детали протокола скрыты в адаптере

**Минусы:**
- Немного больше кода (интерфейс + адаптер)
- Необходимость понимания паттерна

**Причина выбора:** Соответствует принципам чистой архитектуры и микросервисов, обеспечивает долгосрочную поддерживаемость.

---

## ✅ Решение

**1. Создан пакет интерфейсов:**
```
src/interfaces/
├── __init__.py
└── job_search.py  # IJobSearch
```

**2. Создан пакет адаптеров:**
```
apps/infra_orchestrator/src/adapters/
├── __init__.py
└── job_search_adapter.py  # CognitiveJobSearch
```

**3. Обновлены потребители:**
```
apps/job_automation_agent/src/main.py
# Теперь использует IJobSearch вместо прямого импорта
```

**4. Создана документация:**
```
docs/DEPENDENCY_INJECTION.md
```

---

## 📊 Последствия

### Положительные

| Последствие | Описание |
|-------------|----------|
| **Zero Coupling** | Сервисы не зависят от реализации друг друга |
| **Pluggability** | Замена реализации занимает ~10 минут (править 1 файл) |
| **Testability** | Тесты на mock-объектах, мгновенные, без поднятия сервисов |
| **Maintainability** | Изменение API локализовано в адаптере |
| **SOLID compliance** | Соблюдение принципов D (Dependency Inversion) и I (Interface Segregation) |

### Негативные

| Последствие | Описание |
|-------------|----------|
| **Больше кода** | Нужно писать интерфейс + адаптер (~50 строк кода) |
| **Сложность для новичков** | Требуется понимание паттерна Dependency Injection |
| **Косвенная зависимость** | Оба сервиса зависят от `src/interfaces/` (но это допустимо) |

---

## 🔄 Миграция

**Шаги:**
1. ✅ Создать интерфейс `IJobSearch` в `src/interfaces/`
2. ✅ Создать адаптер `CognitiveJobSearch` в `apps/infra_orchestrator/src/adapters/`
3. ✅ Обновить `job_automation_agent` для использования интерфейса
4. ✅ Удалить прямые импорты из `job_automation_agent`
5. ✅ Написать тесты на mock-объектах
6. ✅ Создать документацию в `docs/DEPENDENCY_INJECTION.md`

**Откат:**
- Вернуть прямые импорты в `job_automation_agent`
- Удалить интерфейс и адаптер
- **Но не рекомендуется** — это шаг назад в архитектуре

---

## 📚 Ссылки

- ADR-002: Интеграция компонентов в единую экосистему
- ADR-015: Граница между `src/` и `apps/`
- [Dependency Injection в Python](https://realpython.com/dependency-injection-python/)
- [SOLID Principles — Dependency Inversion](https://www.baeldung.com/solid-principles-dependency-inversion)

---

## 🎯 Следующие шаги

1. Применить паттерн к другим взаимодействиям:
   - `IResumeGenerator` — генерация резюме
   - `INotificationService` — отправка уведомлений
   - `ICareerTracker` — трекинг компетенций

2. Рассмотреть внедрение **DI Container** для автоматического управления зависимостями:
   - `dependency_injector` (Python)
   - `injector` (Python)

3. Добавить конфигурацию выбора провайдера через переменные окружения:
   ```bash
   export JOB_SEARCH_PROVIDER=cognitive-agent  # или hhru-api, linkedin-api
   ```

---

*ADR-018 принят 18 мая 2026 г.*
