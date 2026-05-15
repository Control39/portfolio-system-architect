# Portfolio Organizer

**Система организации и анализа портфолио проектов**

---

## 📊 Метрики качества

| Метрика | Значение | Статус |
|---------|----------|--------|
| **Тесты** | 20/20 | ✅ 100% |
| **Пропущено** | 4 (known issues) | ⚠️ |
| **Покрытие** | ~75% | ✅ |
| **Линтинг** | Чисто | ✅ |

---

## 🚀 Возможности

### Project API

- **Управление проектами**:
  - `GET /api/projects` — список всех проектов
  - `GET /api/projects/<id>` — проект по ID
  - `GET /api/projects/<id>/recommendations` — рекомендации для проекта
- **Анализ портфолио**:
  - `GET /api/portfolio/analysis` — сводка портфолио
  - `POST /api/portfolio/analysis` — анализ с ML-моделями

### Интеграции

- **IT-Compass API**: Маркеры компетенций
- **Notification Service**: Уведомления по email
- **ML Model Registry**: Интеграция для предсказаний

---

## 🧪 Тесты

```bash
# Запуск тестов
pytest apps/portfolio_organizer/tests/ -v

# С покрытием
pytest apps/portfolio_organizer/tests/ --cov=apps/portfolio_organizer --cov-report=html
```

### Покрытие тестами

| Класс тестов | Тесты | Статус | Описание |
|-------------|-------|--------|----------|
| `TestProjectAPI` | 6 | ✅ | Project endpoints |
| `TestPortfolioAnalysis` | 3 | ✅ | Portfolio analysis |
| `TestHealthEndpoints` | 4 | ✅ | Health checks |
| `TestITCompassAPI` | 3 | ✅ | IT-Compass integration |
| `TestNotificationService` | 2 | ✅ | Notifications |
| `TestMLModelRegistryIntegration` | 4 | ⏸️ | ML integration (known issues) |
| `TestErrorHandling` | 2 | ✅ | Error handling |

**Итого:** 24 теста (20 passed, 4 skipped) ✅

### Known Issues

4 теста пропущены из-за импорта `ml_model_registry_integration` (отсутствует `utils.security` в контексте тестирования). Требуется рефакторинг импортов.

---

## 📁 Структура

```
apps/portfolio_organizer/
├── src/
│   ├── api/
│   │   ├── reasoning_api.py       # Project & portfolio API
│   │   └── ml_model_registry_integration.py  # ML integration
│   ├── core/
│   │   ├── ITCompassAPI.py        # IT-Compass integration
│   │   └── notification_service.py # Email notifications
│   └── utils/
│       └── security.py             # Security utilities
├── tests/
│   ├── test_basic.py               # Шаблонные тесты (устарели)
│   └── test_real.py                # Реальные тесты (20 passed)
└── Dockerfile                      # Контейнеризация
```

---

## 🚀 Использование

```python
# Получить проекты
GET /api/projects

# Получить рекомендации
GET /api/projects/1/recommendations

# Анализ портфолио
GET /api/portfolio/analysis
```

---

## 📚 Документация

- [ARCHITECTURE.md](../../ARCHITECTURE.md)
- [ML Model Registry](../ml_model_registry/README.md)
- [IT-Compass](../it_compass/README.md)

---

*© 2026 Ekaterina Kudelya. Portfolio System Architect*
