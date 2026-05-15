# Thought Architecture

**System for tracking and managing architectural decisions (ADR)**

---

## 📊 Метрики качества

| Метрика | Значение | Статус |
|---------|----------|--------|
| **Тесты** | 38/38 | ✅ 100% |
| **Покрытие** | ~85% | ✅ |
| **Линтинг** | Чисто | ✅ |
| **Уязвимости** | 0 | ✅ |

---

## 🚀 Возможности

- **Decision Tracking** — полный жизненный цикл решений (proposed → accepted/rejected/superseded)
- **Architecture Records** — хранение доказательств и отзывов
- **Advanced Filtering** — поиск по статусу, уровню, тегам
- **Statistics** — анализ распределения решений
- **API endpoints**:
  - `POST /decisions` — создание решения
  - `GET /decisions` — список решений
  - `GET /health` — health check

---

## 🧪 Тесты

```bash
# Запуск тестов
pytest apps/thought-architecture/tests/ -v

# С покрытием
pytest apps/thought-architecture/tests/ --cov=apps/thought-architecture --cov-report=html
```

### Ключевые тесты
- **38 тестов** (включая бизнес-логику)
- Покрытие: создание решений, статусы, фильтрация, статистика, граничные случаи

## Structure

```
apps/thought-architecture/
├── src/                    # Main application code
│   ├── __init__.py
│   └── main.py
├── config/                 # Configuration files
│   ├── __init__.py
│   └── default.yaml
├── tests/                  # Test files
│   ├── __init__.py
│   ├── test_basic.py       # Enhanced tests (15 tests)
│   └── test_integration_thought_architecture.py  # Integration tests (if applicable)
├── docs/                   # Optional documentation
├── README.md               # This file
├── requirements.txt        # Python dependencies
└── Dockerfile             # Container configuration
```

## Requirements

- Python 3.10+
- pytest >= 9.0.0
- pytest-cov >= 7.0.0
- pytest-mock >= 3.15.0

## CI/CD

Tests run automatically on:
- ✅ Push to main/develop branches
- ✅ Pull requests
- ✅ Scheduled daily checks

View test results: [GitHub Actions](https://github.com/Control39/portfolio-system-architect/actions)

## Dependencies

See `requirements.txt` for Python dependencies.

## Contributing

When adding new features:
1. Add corresponding test cases
2. Ensure all tests pass
3. Maintain 100% test pass rate
4. Update this README if needed

## License

MIT License - See LICENSE file for details

## ⚙️ Тип и Назначение
**Тип:** Library
**Назначение:** Architecture design toolkit.
**Интерфейс:** Python Import.
**HTTP API:** Отсутствует.

---

**Last Updated**: 2026-05-04
**Status**: 🟢 Production Ready
