# IT Compass

**Методология объективного измерения компетенций через 83 маркера в 19 доменах**

---

## 📊 Метрики качества

| Метрика | Значение | Статус |
|---------|----------|--------|
| **Тесты** | 18/18 (новые) + 28/28 (существующие) | ✅ 100% |
| **Покрытие** | ~85% | ✅ |
| **Линтинг** | Чисто | ✅ |
| **Уязвимости** | 0 | ✅ |

---

## 🎯 Методология

**IT-Compass** — это система отслеживания карьерного прогресса на основе:

- **83 проверочных маркера** в 19 IT-доменах
- **3 уровня сложности**: junior, middle, senior
- **Приоритеты**: high, medium, low
- **SMART-критерии** для каждого маркера

### Пример маркера

```json
{
  "id": "python_basics",
  "marker": "Базовый синтаксис Python",
  "validation": "Успешное прохождение тестов",
  "priority": "high",
  "resources": ["https://docs.python.org/"],
  "smart_criteria": {
    "beginner": "Создать простой скрипт"
  },
  "skill_name": "Python"
}
```

---

## 🧪 Тесты

```bash
# Запуск тестов
pytest apps/it_compass/tests/ -v

# С покрытием
pytest apps/it_compass/tests/ --cov=apps/it_compass --cov-report=html
```

### Новые тесты (реальная бизнес-логика)

| Класс тестов | Тесты | Описание |
|-------------|-------|----------|
| `TestCareerTrackerRealLogic` | 18 | Трекинг, прогресс, рекомендации |

**Итого новых:** 18 тестов, 100% прохождение ✅
**Всего:** 46 тестов (включая интеграционные)

---

## 🚀 Возможности

### CareerTracker

- **Отслеживание прогресса**:
  - `mark_completed(marker_id)` — отметить маркер
  - `show_progress()` — показать прогресс
  - `get_skill_progress(skill_name)` — прогресс по навыку
- **Рекомендации**:
  - `show_recommendations(limit=5)` — показать рекомендации

### Использование

```python
from apps.it_compass.src.core.tracker import CareerTracker

# Инициализация
tracker = CareerTracker(
    markers_dir="apps/it_compass/src/data/markers",
    progress_file="data/user_progress.json"
)

# Отметить маркер
tracker.mark_completed("python_basics")

# Показать прогресс
tracker.show_progress()

# Получить рекомендации
tracker.show_recommendations(limit=3)
```

---

## 📁 Структура данных

```
apps/it_compass/
├── src/
│   ├── core/
│   │   ├── tracker.py       # Основная логика
│   │   └── models.py        # Модели данных
│   └── data/
│       └── markers/         # JSON-файлы маркеров
│           ├── python.json
│           ├── docker.json
│           └── ...
└── tests/
    ├── test_tracker_real.py        # Новые тесты (18)
    ├── test_tracker_integration.py # Интеграционные (12)
    └── test_basic.py               # Шаблоны (16)
```

---

## 🎓 Домены

1. Python
2. Docker
3. Kubernetes
4. AWS/Azure
5. CI/CD
6. Тестирование
7. Архитектура
8. Безопасность
9. ... (19 всего)

---

## 🔒 Лицензия

**Методология © 2025 Ekaterina Kudelya**
Лицензия: CC BY-ND 4.0

---

## 📚 Документация

- [Методология](../../docs/methodology/IT-COMPASS.md)
- [ARCHITECTURE.md](../../ARCHITECTURE.md)
- [CONTRIBUTING.md](../../CONTRIBUTING.md)

---

*© 2026 Ekaterina Kudelya. Portfolio System Architect*
