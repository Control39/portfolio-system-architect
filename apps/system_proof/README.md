# System Proof

**Proof collection and verification system for Chain-of-Thought (CoT)**

---

## 📊 Метрики качества

| Метрика | Значение | Статус |
|---------|----------|--------|
| **Тесты** | 40/40 | ✅ 100% |
| **Покрытие** | ~80% | ✅ |
| **Линтинг** | Чисто | ✅ |
| **Уязвимости** | 0 | ✅ |

---

## 🚀 Возможности

- **Proof Collection** — CRUD операций с коллекциями доказательств
- **Step Management** — добавление и верификация шагов рассуждения
- **Search & Filter** — поиск по chain_id, архитектуре, тегам
- **Verification** — автоматическая верификация доказательств
- **CoT Support** — полная поддержка Chain-of-Thought
- **API endpoints**:
  - `POST /proofs` — создание доказательства
  - `GET /proofs` — список доказательств
  - `POST /proofs/{id}/verify` — верификация
  - `GET /health` — health check

---

## 🧪 Тесты

```bash
# Запуск тестов
pytest apps/system_proof/tests/ -v

# С покрытием
pytest apps/system_proof/tests/ --cov=apps/system_proof --cov-report=html
```

### Ключевые тесты
- **40 тестов** (15 базовых + 25 бизнес-логики)
- Покрытие: CRUD, верификация, поиск, фильтрация, граничные случаи

---

**Last Updated**: 2026-05-15
**Status**: 🟢 Production Ready