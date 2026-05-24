# Эксперименты и Референсные Архитектуры

Эта папка содержит альтернативные реализации и архитектурные эксперименты, которые не включены в основную production-систему, но демонстрируют важные паттерны и возможности.

---

## 🧪 Cloud Reasoning (Serverless)

**Статус:** Reference Architecture (Архитектурный эталон)  
**Путь:** `experiments/cloud-reason-serverless/`

### Концепция

Этот проект демонстрирует **гибридную архитектуру** для AI reasoning:

| Режим | Реализация | Преимущества | Сценарий использования |
|-------|------------|--------------|------------------------|
| **Local Mode** | `apps/decision_engine/` (FastAPI + Ollama/Llama) | Приватность, скорость, нет зависимости от облака | Разработка, тестирование, чувствительные данные |
| **Cloud Mode** | `cloud-reason-serverless/` (Yandex Cloud Functions) | Масштабируемость, экономия ресурсов, serverless | Production-нагрузки, пиковые запросы, экономия затрат |

### Архитектурные решения

1. **Serverless-first подход** — использование Cloud Functions для scale-to-zero и экономии на гранте 6000₽
2. **API Gateway как фасад** — единая точка входа с аутентификацией и rate limiting
3. **Объектное хранилище** — разделение данных и вычислений (S3-совместимость)
4. **Интеграция с YandexGPT** — нативная поддержка русского языка и контекста

### Ценность для портфолио

- ✅ **Cost Optimization** — умение выбирать между On-Premise и Serverless под бюджет
- ✅ **Cloud Integration** — практический опыт работы с Yandex Cloud (4+ сервиса)
- ✅ **Architectural Flexibility** — не фанатизм на одном стеке, а выбор под задачу
- ✅ **Grant Compliance** — демонстрация эффективного использования грантовых средств

### Связь с основной системой

- **decision_engine** — основная реализация (локальный режим)
- **cloud-reason-serverless** — альтернативная реализация (serverless режим)
- Обе реализации используют общие паттерны RAG и reasoning

### Как использовать

```bash
# Локальный режим (production)
docker-compose up -d decision-engine

# Serverless режим (для демонстрации/грантов)
# См. README в experiments/cloud-reason-serverless/
```

### Ссылки

- [Документация cloud-reason-serverless](./cloud-reason-serverless/README.md)
- [ADR-00XX: Выбор между Local и Cloud LLM](../docs/architecture/decisions/)
- [decision_engine API](../apps/decision_engine/README.md)

---

## 📝 Добавление новых экспериментов

Чтобы добавить новый эксперимент:

1. Создай папку `experiments/<name>/`
2. Добавь `README.md` с описанием концепции и архитектурных решений
3. Укажи статус: `Proof of Concept`, `Reference Architecture`, `Deprecated`
4. Добавь ссылку в этот файл

---

*Последнее обновление: 22 мая 2026 г.*
