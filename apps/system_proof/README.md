# System Proof

> **Статус:** 🟢 Production Ready
> **Версия:** 1.0.0
> **Владелец:** Portfolio System Architect Team

---

## 🎯 Назначение

System Proof — сервис автоматической валидации критериев производственной готовности микросервисов. Проверяет тестирование, безопасность, документацию, мониторинг и деплоймент, генерируя доказательства готовности к production.

### Ключевые возможности
- [x] Валидация покрытия тестами (цель: 80%+)
- [x] Проверка безопасности (Trivy, Bandit, Sealed Secrets)
- [x] Проверка документации (README, ADR, CONTRIBUTING)
- [x] Проверка мониторинга (метрики, логирование, health checks)
- [x] Проверка деплоймента (Dockerfile, K8s manifests)
- [x] Генерация отчётов о готовности (score 0-100%)
- [x] Интеграция с AI Config Manager

---

## 💼 Архитектурная ценность

### Проблема

При развёртывании микросервисов часто упускаются критические аспекты:
- **Недостаточное покрытие тестами** → баги в production
- **Уязвимости безопасности** → компрометация системы
- **Отсутствие документации** → сложность поддержки
- **Нет мониторинга** → невозможно отладить инциденты

### Решение

System Proof автоматически проверяет все критерии готовности и выдаёт **объективный score**:
- **< 70%:** Не готов к production
- **70-85%:** Готов с оговорками (warning)
- **85%+:** Production Ready ✅

---

## 📦 Зависимости

Основные зависимости (см. `requirements.txt`):

- **FastAPI** >= 0.100.0 — веб-фреймворк
- **Pydantic** >= 2.0.0 — валидация данных
- **Uvicorn** >= 0.20.0 — ASGI сервер
- **PyYAML** >= 6.0.0 — загрузка конфигов

Установка:

```bash
pip install -r requirements.txt
```

---

## 🚀 Быстрый старт

### Запуск через Docker

```bash
docker-compose up -d system-proof
```

### Локальный запуск

```bash
cd apps/system_proof
python -m uvicorn main:app --reload --port 8300
```

### Доступ к API

- **Swagger UI:** http://localhost:8300/docs
- **Redoc:** http://localhost:8300/redoc
- **Health check:** http://localhost:8300/health

---

## 🛠️ API Endpoints

### Основные
- `GET /` — Информация о сервисе
- `GET /health` — Проверка здоровья

### Proof Management
- `GET /api/v1/proofs` — Список доказательств всех сервисов
- `GET /api/v1/proofs/{service_name}` — Доказательство конкретного сервиса
- `POST /api/v1/proofs/{service_name}/validate` — Запустить валидацию

### Примеры

```bash
# Получить proof для cognitive-agent
curl http://localhost:8300/api/v1/proofs/cognitive-agent

# Запустить валидацию
curl -X POST http://localhost:8300/api/v1/proofs/cognitive-agent/validate
```

---

## 🏗️ Архитектура

```
system_proof/
├── src/
│   ├── config_integration.py  # AI Config Manager
│   ├── validators/            # Валидаторы по категориям
│   │   ├── test_validator.py
│   │   ├── security_validator.py
│   │   ├── docs_validator.py
│   │   ├── monitoring_validator.py
│   │   └── deployment_validator.py
│   └── __init__.py
├── tests/
│   ├── test_validators.py
│   └── test_api.py
├── Dockerfile
├── main.py                    # FastAPI приложение
└── README.md
```

---

## 🧪 Тестирование

```bash
# Все тесты
pytest apps/system_proof/tests/ -v

# С покрытием
pytest apps/system_proof/tests/ --cov=apps/system_proof/src --cov-report=term-missing
```

---

## 🔐 Безопасность

- ✅ Валидация всех входных данных через Pydantic
- ✅ Защита от SQL-инъекций (нет SQL)
- ✅ Rate limiting через Traefik
- ✅ Маскировка секретов в логах

---

## 📚 AI Config Manager

Сервис интегрирован с централизованной конфигурацией:

```python
from apps.system_proof.src.config_integration import get_config

config = get_config()
settings = config.get_config()
```

---

## 🛣️ Маршрутизация

| Порт (внешний) | Маршрут (Traefik) | Порт (внутренний) |
|----------------|-------------------|-------------------|
| 8300 | `/system-proof` | 8300 |

---

## 📝 Known Issues

- Требуется настройка путей к сканерам безопасности (Trivy, Bandit)
- Нет интеграции с CI/CD пайплайнами (планируется)

---

## 🛠️ Contributing

1. Fork репозиторий
2. Создайте ветку: `git checkout -b feature/sp-feature`
3. Внесите изменения и протестируйте
4. Закоммитьте: `git commit -m "feat: описание"`
5. Push: `git push origin feature/sp-feature`
6. Создайте Pull Request

**Правила:**
- Следуйте стилю Black + isort
- Добавьте тесты для новых валидаторов
- Обновите документацию при необходимости

---

*Последнее обновление: 18 мая 2026 г.*
