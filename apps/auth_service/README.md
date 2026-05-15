# Auth Service

**JWT-аутентификация для Portfolio System Architect**

---

## 📊 Метрики качества

| Метрика | Значение | Статус |
|---------|----------|--------|
| **Тесты** | 21/21 | ✅ 100% |
| **Покрытие** | ~95% | ✅ |
| **Линтинг** | Чисто | ✅ |
| **Уязвимости** | 0 | ✅ |

---

## 🚀 Возможности

- **JWT токены** (HS256 алгоритм)
- **Ролевая модель** (admin/user)
- **Безопасность**:
  - Блокировка демо-учётных данных
  - Валидация подписи токена
  - Проверка срока действия
- **API endpoints**:
  - `POST /auth/token` — получение токена
  - `GET /health` — health check

---

## 🧪 Тесты

```bash
# Запуск тестов
pytest apps/auth_service/tests/ -v

# С покрытием
pytest apps/auth_service/tests/ --cov=apps/auth_service --cov-report=html
```

### Покрытие тестами

| Класс тестов | Тесты | Описание |
|-------------|-------|----------|
| `TestJWTTokenCreation` | 4 | Создание токенов |
| `TestJWTTokenVerification` | 5 | Верификация (включая истёкшие/подделанные) |
| `TestRoleBasedAccess` | 3 | Ролевая модель |
| `TestAPIEndpoints` | 5 | API endpoints |
| `TestEdgeCases` | 4 | Граничные случаи (Unicode, спецсимволы) |

**Итого:** 21 тест, 100% прохождение ✅

---

## 🔧 Конфигурация

Переменные окружения:

```bash
JWT_SECRET=your-secret-key          # Секретный ключ (обязательно)
JWT_ALGORITHM=HS256                  # Алгоритм (по умолчанию)
JWT_EXPIRATION_HOURS=24              # Срок действия (по умолчанию)
```

---

## 📖 Использование

### Получение токена

```bash
curl -X POST http://localhost:8100/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "pass"}'
```

### Верификация токена

```python
from apps.auth_service.main import verify_token

class Credentials:
    credentials = "eyJhbGciOiJIUzI1NiIs..."  # pragma: allowlist secret

user_data = verify_token(Credentials())
# {'username': 'user', 'role': 'user'}
```

---

## 🔒 Безопасность

- ✅ Не коммитить `JWT_SECRET` в репо
- ✅ Использовать `.secrets.baseline` для сканирования
- ✅ Регулярные Trivy-сканы
- ✅ Rate limiting через Traefik

---

## 📚 Документация

- [ARCHITECTURE.md](../../ARCHITECTURE.md) — общая архитектура
- [SECURITY.md](../../SECURITY.md) — политика безопасности
- [CONTRIBUTING.md](../../CONTRIBUTING.md) — правила контрибуции

---

*© 2026 Ekaterina Kudelya. Portfolio System Architect*
