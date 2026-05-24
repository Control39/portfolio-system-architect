# 🏗️ ARCHITECTURE_DEFENSE.md

## 🚨 CRITICAL: Паттерн "Атомы + Молекулы" — Защита от деструктивных ИИ-агентов

**Статус:** Восстановление после инцидента (2026-05-24)
**Инцидент:** ИИ удалил 40% кода из src/, не понимая что это переиспользуемые компоненты
**Решение:** Этот документ — инструкция для агентов

---

## 📐 Архитектура (Правильная Версия)

```
portfolio-system-architect/
│
├── src/ ← АТОМЫ (переиспользуемые компоненты)
│   ├── ai/                          # LLM интеграции (GigaChat, OpenAI)
│   ├── assistant_orchestrator/      # Оркестрация агентов
│   ├── core/                        # Основные компоненты (database, models, etc)
│   ├── embedding_agent/             # RAG + embedding
│   ├── infrastructure/              # Docker, K8s, monitoring
│   ├── security/                    # Авторизация, шифрование
│   ├── config/                      # Конфигурация
│   └── ... (10+ модулей)
│
├── apps/ ← МОЛЕКУЛЫ (независимые сервисы)
│   ├── auth_service/
│   │   ├── main.py                  # from src.security import ...
│   │   ├── requirements.txt
│   │   ├── Dockerfile               # COPY src/ И COPY apps/auth_service/
│   │   └── tests/
│   │
│   ├── decision_engine/
│   │   ├── main.py                  # from src.ai import LLMProvider
│   │   ├── Dockerfile               # COPY src/ И COPY apps/decision_engine/
│   │   └── src/                     # Специфичные компоненты этого сервиса
│   │
│   ├── it_compass/
│   │   ├── main.py                  # Streamlit UI
│   │   ├── scripts/reasoning_integration.py  # АВТОМАТИЧЕСКОЕ извлечение маркеров
│   │   └── Dockerfile               # COPY src/
│   │
│   └── ... (14 сервисов всего)
│
├── deployment/
│   ├── kubernetes/
│   │   ├── overlays/dev/
│   │   ├── overlays/staging/
│   │   └── overlays/prod/
│   │
│   └── docker-compose.yml           # context: . для ВСЕХ сервисов
│
└── docs/
    ├── architecture/decisions/      # 19 ADR (Архитектурные решения)
    └── evidence/                    # Артефакты для IT-Compass
```

---

## 🔗 Как это работает (Диаграмма)

```
┌─────────────────────────────────────────────────────────────┐
│                      docker-compose up                       │
└──────────┬──────────────────────────────────────────────────┘
           │
           ├─→ Для каждого сервиса (auth_service, decision_engine и т.д.):
           │
           │   1. Берём Dockerfile сервиса
           │   2. context: . (КОРЕНЬ репо, не папка сервиса!)
           │   3. Копируем:
           │      - COPY src/ /app/src              ← Атомы
           │      - COPY apps/SERVICE/ /app         ← Молекула
           │      - COPY requirements.txt /app      ← Корневые зависимости
           │
           │   4. В контейнере:
           │      - /app/src/ содержит все атомы
           │      - /app/main.py может делать: from src.ai import ...
           │      - PYTHONPATH=/app:/app/src
           │
           └─→ Результат: 14 независимых сервисов, каждый импортирует нужные атомы

┌────────────────────────────────────┐
│ docker-compose ps -a               │
├────────────────────────────────────┤
│ ✅ auth_service         Up (8100)  │
│ ✅ decision_engine      Up (8001)  │
│ ✅ it_compass           Up (8501)  │
│ ✅ portfolio_organizer  Up (8004)  │
│ ✅ + 10 сервисов        Up        │
└────────────────────────────────────┘
```

---

## 🚫 ЧТО НЕ ТРОГАТЬ (И ПОЧЕМУ)

### 1. src/ — СВЯЩЕННОЕ МЕСТО

| Папка | Используется сервисами | Пример | Удалять? |
|-------|------------------------|--------|----------|
| src/ai/ | ВСЕ сервисы с LLM | decision_engine, cognitive_agent | 🚫 NO |
| src/core/ | ВСЕ сервисы | auth_service (JWT), portfolio (DB) | 🚫 NO |
| src/security/ | auth_service, infra_orchestrator | Шифрование API ключей | 🚫 NO |
| src/infrastructure/ | Все мониторинг | prometheus, k8s интеграция | 🚫 NO |
| src/embedding_agent/ | decision_engine, knowledge_graph | RAG, ChromaDB | 🚫 NO |
| src/assistant_orchestrator/ | cognitive_agent | Оркестрация микро-агентов | 🚫 NO |

**Если видишь в main.py:**
```python
from src.ai import LLMProvider
from src.core import Database
from src.security import APIKeyEncryption
```

**Это ЗНАЧИТ:**
- ✅ Эти компоненты используются
- ✅ Они должны быть в src/
- ✅ Dockerfile должен копировать src/
- 🚫 Их категорически НЕЛЬЗЯ удалять

### 2. apps/*/Dockerfile — КРИТИЧНЫЕ

**Правильный Dockerfile:**
```dockerfile
FROM python:3.12-slim
WORKDIR /app

# ✅ ОБЯЗАТЕЛЬНО: Копируем src/ (атомы)
COPY src/ /app/src

# ✅ ОБЯЗАТЕЛЬНО: Копируем сервис (молекула)
COPY apps/SERVICE_NAME/ /app

# ✅ ОБЯЗАТЕЛЬНО: PYTHONPATH с обеими папками
ENV PYTHONPATH=/app:/app/src

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0"]
```

**ЕСЛИ Dockerfile не содержит `COPY src/`:**
```
❌ НЕПРАВИЛЬНО (удаляет возможность импортировать src/)
```

---

## ⚙️ Как IT-Compass работает (Автономная Система)

### Без ручного ввода:

```python
# apps/it_compass/scripts/reasoning_integration.py

def analyze_repository():
    """Автоматически сканирует репо и находит маркеры"""
    
    # 1. Читает все ADR (docs/architecture/decisions/*.md)
    adrs = load_adrs()
    
    # 2. Запускает git log для истории решений
    commits = get_git_history()
    
    # 3. Анализирует тесты (tests/, apps/*/tests/)
    test_coverage = measure_coverage()
    
    # 4. Отправляет в LLM (GigaChat/OpenAI):
    #    "На основе этих ADR, коммитов и тестов —
    #     какие маркеры компетенций доказаны?"
    
    markers = llm_reason_about_markers(adrs, commits, test_coverage)
    
    # 5. Сохраняет результат
    save_to_json('docs/evidence/markers.json', markers)
    
    # 6. UI автоматически обновляется
    #    (Streamlit читает JSON и отмечает маркеры)
```

### Результат:
```json
{
  "found_markers": [
    {
      "marker_id": "system_architecture_3_2",
      "name": "Microservices Architecture",
      "confidence": 0.92,
      "evidence": [
        "16 сервисов в apps/",
        "Loose coupling через API",
        "19 ADR документирующих решения"
      ]
    },
    {
      "marker_id": "devops_2_1",
      "name": "Docker Containerization",
      "confidence": 0.95,
      "evidence": [
        "Все сервисы в Docker",
        "docker-compose.yml с 14 сервисами",
        "CI/CD pipeline с Docker builds"
      ]
    }
  ],
  "total_markers_found": 23,
  "coverage": "27.7% маркеров найдено (23/83)"
}
```

**В UI (http://localhost:8501):**
- ✅ Радар компетенций автоматически заполняется
- ✅ Зелёные галочки в найденных маркерах
- ✅ Серые — не найдены
- ✅ Всё без ручного ввода

---

## 🛡️ Защита от Инцидентов

### Инцидент 1: "Удалю src/ai/, она неиспользуется"

**Признак:** ИИ видит `src/ai/` и думает, что она не используется

**Правильная реакция:**
```bash
grep -r "from src.ai import" apps/*/main.py
# Результат: 8 сервисов используют src.ai
# ✅ Это ДОСТАТОЧНО, чтобы НЕ удалять
```

**Агент должен:**
1. Проверить: `grep -r "from src.X import" apps/*/`
2. Если результат не пуст — файл ИСПОЛЬЗУЕТСЯ
3. 🚫 НЕ удалять

### Инцидент 2: "Dockerfile неправильный, нету src/"

**Признак:** Ошибка `ModuleNotFoundError: No module named 'src'`

**Агент должен:**
1. Проверить `apps/SERVICE/Dockerfile`
2. Если нет `COPY src/` — ДОБАВИТЬ
3. Проверить `docker-compose.yml`: `context: .`?
4. Пересобрать: `docker-compose build SERVICE`
5. 🚫 НЕ удалять src/

### Инцидент 3: "apps/SERVICE/src/ пуста"

**Правильно:** Каждый сервис имеет свой `apps/SERVICE/src/` (специфичные компоненты) И импортирует общий `/src/` из корня

**Агент НЕ должен:**
```python
# ❌ НЕПРАВИЛЬНО
if not os.listdir('apps/auth_service/src/'):
    shutil.rmtree('apps/auth_service/src/')  # Удалить пустую папку
```

**Агент ДОЛЖЕН:**
```python
# ✅ ПРАВИЛЬНО
if not os.listdir('apps/auth_service/src/'):
    # Это нормально — специфичные компоненты могут быть минимальными
    # Основное: /app/src (из корня репо)
    pass
```

---

## ✅ Контрольный Список для Агентов

Перед ЛЮБЫМ изменением архитектуры:

- [ ] Проверил: есть ли в `main.py` импорты из `src/`?
- [ ] Проверил: находятся ли эти файлы в `src/`?
- [ ] Проверил: есть ли в Dockerfile `COPY src/`?
- [ ] Проверил: есть ли в `docker-compose.yml` `context: .`?
- [ ] Проверил: есть ли `ENV PYTHONPATH=/app:/app/src`?
- [ ] Запустил: `docker-compose up -d` и `docker-compose ps`?
- [ ] Прочитал: `.guardrails.json` в корне репо?
- [ ] Согласовал: изменения архитектуры требуют approval?

Если ответ на любой вопрос "нет" — **СТОП**. Запросить clarification.

---

## 📞 Если Что-то Сломалось

**Шаг 1:** Проверить структуру
```bash
ls -la src/ apps/
# Все папки на месте?
```

**Шаг 2:** Проверить Dockerfile
```bash
grep "COPY src/" apps/*/Dockerfile
# Все сервисы копируют src/?
```

**Шаг 3:** Проверить docker-compose.yml
```bash
grep "context: ." docker-compose.yml
# Все сервисы используют context: . (не ./apps/SERVICE)?
```

**Шаг 4:** Пересобрать
```bash
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
docker-compose ps
```

**Шаг 5:** Если не помогло
```bash
Telegram: @koda_dev
GitHub: Control39/portfolio-system-architect
```

---

## 🎯 ГЛАВНОЕ

**Паттерн "Атомы + Молекулы" работает ТОЛЬКОесли:**

1. ✅ `src/` скопирована в контейнер
2. ✅ Сервис скопирован в контейнер
3. ✅ `PYTHONPATH` указывает на ОБА пути
4. ✅ `docker-compose.yml` использует `context: .`
5. ✅ Агенты НЕ удаляют файлы из `src/`, видя "неиспользуемость"

**Если это нарушено:**
```
❌ Контейнер не запустится
❌ ModuleNotFoundError: No module named 'src'
❌ Вся система сломана
```

---

**Автор:** Ekaterina Kudelya
**Дата создания:** 2024-01-15
**Последнее обновление:** 2026-05-24 (после инцидента)
**Статус:** 🟢 ACTIVE | Обязателен для прочтения всем агентам
