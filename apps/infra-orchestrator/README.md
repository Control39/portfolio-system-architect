# Infra Orchestrator

**Infrastructure orchestration and management system**

---

## 📊 Метрики качества

| Метрика | Значение | Статус |
|---------|----------|--------|
| **Тесты** | 58/58 | ✅ 100% |
| **Покрытие** | ~90% | ✅ |
| **Линтинг** | Чисто | ✅ |
| **Уязвимости** | 0 | ✅ |

---

## 🚀 Возможности

- **Service Lifecycle** — регистрация, развёртывание, масштабирование, остановка
- **Multi-Cluster** — поддержка нескольких кластеров
- **Health Checks** — мониторинг состояния сервисов
- **Scaling** — автоматическое и ручное масштабирование
- **Deployment History** — история развёртываний с rollback
- **API endpoints**:
  - `POST /services` — регистрация сервиса
  - `GET /services` — список сервисов
  - `POST /services/{id}/scale` — масштабирование
  - `GET /health` — health check

---

## 🧪 Тесты

```bash
# Запуск тестов
pytest apps/infra-orchestrator/tests/ -v

# С покрытием
pytest apps/infra-orchestrator/tests/ --cov=apps/infra-orchestrator --cov-report=html
```

### Ключевые тесты
- **58 тестов** (включая бизнес-логику оркестратора)
- Покрытие: жизненный цикл сервисов, масштабирование, health checks, multi-cluster

---

**Last Updated**: 2026-05-15
**Status**: 🟢 Production Ready