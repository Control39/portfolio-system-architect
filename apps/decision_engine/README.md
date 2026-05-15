# Decision Engine

**AI-driven decision-making system with RAG and reasoning capabilities**

---

## 📊 Метрики качества

| Метрика | Значение | Статус |
|---------|----------|--------|
| **Тесты** | 50/50 | ✅ 100% |
| **Покрытие** | ~85% | ✅ |
| **Линтинг** | Чисто | ✅ |
| **Уязвимости** | 0 | ✅ |

---

## 🚀 Возможности

- **AI Reasoning** — принятие решений на основе ИИ
- **RAG Integration** — поиск в векторной базе знаний
- **Explainable AI** — прозрачная логика решений
- **API endpoints**:
  - `POST /decide` — принятие решения
  - `GET /health` — health check
  - `GET /docs` — Swagger UI

---

## 🧪 Тесты

```bash
# Запуск тестов
pytest apps/decision_engine/tests/ -v

# С покрытием
pytest apps/decision_engine/tests/ --cov=apps/decision_engine --cov-report=html
```

### Ключевые тесты
- **50 тестов** (включая интеграционные с decision_engine и knowledge_graph)
- Покрытие: ядро принятия решений, RAG интеграция, обработка ошибок

## Structure

```
apps/decision-engine/
├── src/                    # Main application code
│   ├── __init__.py
│   └── main.py
├── config/                 # Configuration files
│   ├── __init__.py
│   └── default.yaml
├── tests/                  # Test files
│   ├── __init__.py
│   ├── test_basic.py       # Enhanced tests (15 tests)
│   └── test_integration_decision_engine.py  # Integration tests (if applicable)
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

## 🔌 Контракты / API
Краткое описание.
| Метод | Путь | Описание |
|-------|------|----------|
| `GET` | `/health` | Проверка статуса |
> 💡 Swagger доступен по `/docs`

---

**Last Updated**: 2026-05-04
**Status**: 🟢 Production Ready
