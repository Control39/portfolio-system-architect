> **Former ID:** ADR-019-local-vs-cloud-llm
> **Former path:** `docs\architecture\decisions\ADR-019-local-vs-cloud-llm.md`
> **Current ID:** ADR-019
> **Consolidated:** 2026-05-30
>
---

> **Former ID:** ADR-019-local-vs-cloud-llm
> **Former path:** `docs\architecture\decisions\ADR-019-local-vs-cloud-llm.md`
> **Current ID:** ADR-019
> **Consolidated:** 2026-05-23
>
---

---
id: ADR-019
title: Выбор между Local LLM и Cloud Serverless для AI Reasoning
status: accepted
date: 2026-05-22
authors:
  - Control39
consulted:
  - Architecture Team
deciders:
  - Lead Architect
  - CTO
---

# ADR-019: Выбор между Local LLM и Cloud Serverless для AI Reasoning

## Context (Контекст)

Проект Portfolio System Architect требует AI reasoning engine для:
- Генерации объяснений решений
- RAG (Retrieval-Augmented Generation) из документации
- Анализу компетенций (IT-Compass)
- Автоматизации задач (Cognitive Agent)

Возникает вопрос: где выполнять инференс LLM — локально (On-Premise) или в облаке (Serverless)?

## Decision Drivers (Драйверы решений)

1. **Приватность данных** — чувствительные данные не должны покидать периметр
2. **Стоимость** — бюджет гранта 6000₽/месяц на Yandex Cloud
3. **Производительность** — latency для интерактивных сценариев
4. **Масштабируемость** — пиковые нагрузки (например, batch обработка)
5. **Зависимость от инфраструктуры** — оффлайн-режим для разработки

## Considered Options (Рассмотренные варианты)

| Вариант | Описание | Плюсы | Минусы |
|---------|----------|-------|--------|
| **1. Local LLM (Ollama)** | Модели запускаются локально (Llama 3, Mistral) | Приватность, нет latency сети, оффлайн-режим | Требует GPU/CPU, ограничено масштабом |
| **2. Cloud Serverless (Yandex Functions)** | Модели в Yandex Cloud Functions | Масштабируемость, pay-per-use, грант 6000₽ | Зависимость от сети, latency, стоимость при нагрузке |
| **3. Гибридная архитектура** | Local для dev/test, Cloud для production | Оптимально по цене и гибкости | Сложность переключения режимов |

## Decision (Решение)

**Принята гибридная архитектура (Вариант 3):**

### Режимы работы

| Режим | Реализация | Сценарий |
|-------|------------|----------|
| **Local (Default)** | `apps/decision_engine/` + Ollama (Llama 3 8B) | Разработка, тестирование, чувствительные данные |
| **Cloud (Production)** | `experiments/cloud-reason-serverless/` + YandexGPT | Production-нагрузки, пиковые запросы, демо для грантов |

### Переключение режимов

```bash
# Local mode (по умолчанию)
export REASONING_MODE=local
python -m apps.decision_engine.main

# Cloud mode (для production)
export REASONING_MODE=cloud
export YANDEX_CLOUD_FOLDER_ID=...
python -m experiments.cloud_reason_serverless.main
```

### API-контракт

Оба режима реализуют единый интерфейс:

```python
@dataclass
class ReasoningRequest:
    query: str
    context: list[str]
    temperature: float = 0.7

@dataclass
class ReasoningResponse:
    answer: str
    explanation: str  # Chain-of-Thought
    confidence: float
```

## Consequences (Последствия)

### Положительные

✅ **Гибкость**: Можно выбирать под задачу (Local для приватности, Cloud для масштаба)
✅ **Cost Optimization**: Грант 6000₽ покрывает production-нагрузку до 10K запросов/месяц
✅ **DevEx**: Разработчики работают оффлайн без зависимости от облака
✅ **Enterprise-ready**: Демонстрация гибридной архитектуры для клиентов

### Отрицательные

❌ **Сложность**: Нужно поддерживать 2 реализации (Local + Cloud)
❌ **Тестирование**: E2E тесты требуют настройки обоих режимов
❌ **Конфигурация**: Переменные окружения для переключения режимов

## Status (Статус)

**Accepted** — решение принято и реализовано:
- `apps/decision_engine/` — Local режим (production)
- `experiments/cloud-reason-serverless/` — Cloud режим (reference architecture)

## Changelog (История изменений)

- **2026-05-22**: Принято решение, создана документация
- **TODO**: Добавить автоматическое переключение режимов на основе нагрузки

## References (Ссылки)

- [experiments/cloud-reason-serverless/](../../experiments/cloud-reason-serverless/README.md)
- [apps/decision_engine/](../../apps/decision_engine/README.md)
- [Yandex Cloud Functions Pricing](https://yandex.cloud/ru/pricing/serverless-functions)
- [Ollama Documentation](https://ollama.ai/docs)
