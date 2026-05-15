# Job Automation Agent

**AI-powered agent for automated job search and resume optimization**

---

## 📊 Метрики качества

| Метрика | Значение | Статус |
|---------|----------|--------|
| **Тесты** | 21/21 | ✅ 100% |
| **Покрытие** | ~85% | ✅ |
| **Линтинг** | Чисто | ✅ |
| **Уязвимости** | 0 | ✅ |

---

## 🚀 Возможности

- **Job Analysis** — анализ вакансий и требований
- **Resume Parsing** — извлечение навыков из резюме
- **Match Scoring** — вычисление совпадения навыков
- **Market Trends** — анализ рыночных трендов
- **Agent Orchestration** — автономная работа агента
- **API endpoints**:
  - `POST /analyze/jobs` — анализ вакансии
  - `POST /parse/resume` — парсинг резюме
  - `GET /match` — расчёт совпадения
  - `GET /health` — health check

---

## 🧪 Тесты

```bash
# Запуск тестов
pytest apps/job-automation-agent/tests/ -v

# С покрытием
pytest apps/job-automation-agent/tests/ --cov=apps/job-automation-agent --cov-report=html
```

### Ключевые тесты
- **21 тест** (включая оркестрацию агента)
- Покрытие: парсинг резюме, анализ вакансий, matching, рыночные тренды

---

**Last Updated**: 2026-05-15
**Status**: 🟢 Production Ready