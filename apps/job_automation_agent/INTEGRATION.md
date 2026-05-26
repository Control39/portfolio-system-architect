# 🔌 Интеграция с реальными сервисами

## 🎯 Обзор

Job Automation Agent интегрирован с:
- ✅ **hh.ru** — крупнейший сайт вакансий в России
- ✅ **Habr Career** — IT-вакансии от Хабра

---

## 🚀 Быстрый старт

### 1. Установите зависимости

```bash
cd apps/job_automation_agent
pip install -r requirements.txt
```

### 2. Настройте окружение

```bash
cp .env.example .env
# Отредактируйте .env при необходимости
```

### 3. Запустите поиск

```bash
# Через Python
python -m src.job_search

# Или через API
python -m uvicorn src.main:app --reload --port 8005
```

---

## 🔍 Поиск вакансий

### Через Python

```python
from apps.job_automation_agent.src.job_search import search_all_jobs
import asyncio

async def search():
    vacancies = await search_all_jobs(
        query="Python архитектор системное мышление",
        area="113",  # Россия
        enable_hh=True,
        enable_habr=True
    )
    
    print(f"Найдено: {len(vacancies)} вакансий")
    for v in vacancies[:5]:
        print(f"- {v['name']} @ {v['employer']}")

asyncio.run(search())
```

### Через API

```bash
# Поиск на hh.ru
curl "http://localhost:8005/jobs/search/Python%20архитектор"

# Через Traefik
curl "http://localhost/job-agent/jobs/search/Python%20архитектор"
```

---

## 📊 Провайдеры

### hh.ru Provider

**URL:** `https://api.hh.ru/vacancies`

**Параметры:**
- `query` — строка поиска
- `area` — регион (1=Москва, 2=СПб, 113=Россия)
- `per_page` — до 100 вакансий на страницу
- `pages` — количество страниц

**Пример:**
```python
from apps.job_automation_agent.src.providers.hh_ru import search_hh_ru

vacancies = await search_hh_ru(
    query="Python системное мышление",
    area="113",  # Россия
    per_page=20,
    pages=2
)
```

### Habr Career Provider

**URL:** `https://career.habr.com/search.json`

**Параметры:**
- `q` — строка поиска
- `page` — номер страницы
- `per_page` — количество на странице

**Пример:**
```python
from apps.job_automation_agent.src.providers.habr_career import search_habr_career

vacancies = await search_habr_career(
    query="архитектор когнитивных систем",
    per_page=20
)
```

---

## 🎯 Интеграция с IT Compass

### Шаги:

1. **IT Compass сканирует прогресс:**
   ```python
   from apps.it_compass.src.core.tracker import CareerTracker
   
   tracker = CareerTracker()
   progress = tracker.calculate_progress()
   completed_markers = tracker.progress.get("completed_markers", [])
   ```

2. **Извлекает ключевые навыки:**
   ```python
   key_skills = []
   for skill_name, skill_data in tracker.markers.items():
       for level_markers in skill_data.levels.values():
           for marker in level_markers:
               if marker.id in completed_markers:
                   key_skills.append(skill_name)
   ```

3. **Ищет вакансии:**
   ```python
   from apps.job_automation_agent.src.job_search import search_all_jobs
   
   query = f"{', '.join(key_skills[:5])} архитектор методология"
   vacancies = await search_all_jobs(query)
   ```

4. **Сопоставляет и рекомендует:**
   - Сортирует по релевантности
   - Показывает match score
   - Даёт рекомендации по развитию

---

## 🔧 Конфигурация

### Переменные окружения

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `HH_RU_SEARCH_ENABLED` | Включить hh.ru | `true` |
| `HABR_CAREER_SEARCH_ENABLED` | Включить Habr Career | `true` |
| `LOG_LEVEL` | Уровень логирования | `INFO` |

### Пример `.env`:

```env
HH_RU_SEARCH_ENABLED=true
HABR_CAREER_SEARCH_ENABLED=true
LOG_LEVEL=INFO
```

---

## 🧪 Тестирование

### Тест провайдера hh.ru:

```bash
python -m apps.job_automation_agent.src.providers.hh_ru
```

### Тест провайдера Habr Career:

```bash
python -m apps.job_automation_agent.src.providers.habr_career
```

### Полный тест:

```bash
pytest apps/job_automation_agent/tests/ -v
```

---

## 📝 Примеры использования

### 1. Поиск для IT Compass

```python
from apps.it_compass.src.core.tracker import CareerTracker
from apps.job_automation_agent.src.job_search import search_all_jobs
import asyncio

async def find_jobs_for_user():
    # 1. Получить прогресс
    tracker = CareerTracker()
    progress = tracker.calculate_progress()
    
    # 2. Извлечь навыки
    completed = tracker.progress.get("completed_markers", [])
    skills = [name for name, data in tracker.markers.items() 
              for level in data.levels.values() 
              for m in level if m.id in completed]
    
    # 3. Поиск вакансий
    query = f"{', '.join(skills[:5])} архитектор системное мышление"
    vacancies = await search_all_jobs(query, area="113")
    
    # 4. Показать результаты
    print(f"🎯 Найдено {len(vacancies)} вакансий")
    for v in vacancies[:10]:
        print(f"• {v['name']} @ {v['employer']} ({v['salary']})")

asyncio.run(find_jobs_for_user())
```

### 2. Интеграция с демо

```bash
python demo_integration.py
```

Демо автоматически:
1. Сканирует IT Compass
2. Извлекает навыки
3. Ищет на hh.ru и Habr Career
4. Показывает рекомендации

---

## 🛡️ Безопасность

### SSRF-защита

Все URL валидируются через `ALLOWED_HOSTS`:

```python
ALLOWED_HOSTS = {
    "api.hh.ru",
    "career.habr.com",
    "localhost",
    "127.0.0.1"
}
```

### Санитизация ошибок

Ошибки логируются без чувствительных данных:

```python
from .utils.security import sanitize_error_message

safe_message = sanitize_error_message(e, url)
```

---

## 🚀 Развёртывание

### Docker

```bash
docker-compose up -d job-automation-agent
```

### Production

```bash
docker build -t job-automation-agent .
docker run -p 8005:8005 job-automation-agent
```

---

## 📚 Дополнительные ресурсы

- [hh.ru API](https://github.com/hhru/api)
- [Habr Career API](https://career.habr.com/api)
- [IT Compass README](../../apps/it_compass/README.md)
- [Demo Integration](../../DEMO.md)

---

## 👩‍💻 Автор

**Ekaterina Kudelya** — Architect & Methodologist  
**Лицензия:** CC BY-ND 4.0

---

**Дата:** 27 мая 2026  
**Статус:** ✅ Интеграция готова
