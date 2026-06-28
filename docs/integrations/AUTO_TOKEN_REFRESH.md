# Автоматическое обновление GigaChat токенов

## Обзор

Система автоматического обновления токенов GigaChat обеспечивает непрерывную работу с API без ручного вмешательства.

## Компоненты

### 1. TokenRefreshService

Центральный сервис для управления токенами:

```python
from ai.config.token_refresh_service import TokenRefreshService

service = TokenRefreshService()
token = service.get_token()  # Получает токен или обновляет при необходимости
```

**Основные возможности:**
- ✅ OAuth через client_id/client_secret
- ✅ RqUID и Accept заголовки (обязательны для GigaChat API)
- ✅ Кэширование токена с expiry timestamp
- ✅ Автоматическое обновление перед истечением (pre-refresh за 5 мин)
- ✅ Thread-safe операции
- ✅ Фоновый поток auto-refresh

### 2. ConfigManager Integration

Интеграция с конфигурацией:

```python
from ai.config.config_manager import ConfigManager

config = ConfigManager("config/ai-config.yaml")
config.start_token_auto_refresh(interval=60)  # Запуск авто-обновления
token = config.get_gigachat_token()  # Получение токена
config.stop_token_auto_refresh()  # Остановка
```

## Использование

### Базовое использование

```python
from ai.config.token_refresh_service import TokenRefreshService

service = TokenRefreshService()

# Получение токена (автоматическое обновление при необходимости)
token = service.get_token()
```

### Фоновое обновление

```python
# Запуск фонового потока (каждые 60 секунд)
service.start_auto_refresh(interval=60)

# Получение токена (всегда валидный)
token = service.get_token()

# Остановка
service.stop_auto_refresh()
```

### С ConfigManager

```python
config = ConfigManager("config/ai-config.yaml")

# Запуск авто-обновления
config.start_token_auto_refresh(interval=60)

# Получение токена
token = config.get_gigachat_token()

# Остановка
config.stop_token_auto_refresh()
```

### Скрипты

#### demo_token_refresh.py

Демонстрация всех возможностей:

```bash
python demo_token_refresh.py
```

#### run_auto_update_token.py

Запуск сервиса обновления:

```bash
python run_auto_update_token.py
```

Сохраняет токен в `.env` файл.

## Конфигурация

### Переменные окружения

```bash
# Обязательные
GIGACHAT_CLIENT_ID="54b03e66-d6b4-4945-aae4-e071d1439347"
GIGACHAT_CLIENT_SECRET="b6caf308-8ac8-4caf-b9a8-435568f31658"

# Опциональные
GIGACHAT_AUTH_URL="https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
GIGACHAT_SCOPE="GIGACHAT_API_PERS"
GIGACHAT_VERIFY_SSL="false"  # Для корпоративных сетей
GIGACHAT_API_KEY=""  # Приоритет: если установлен, используется напрямую
```

## Архитектура

### Маршрут получения токена

```
get_token()
    ↓
Проверка кэша и expiry
    ↓
[если устарел] → _fetch_token()
    ↓
OAuth запрос (RqUID, Accept заголовки)
    ↓
Обновление кэша
    ↓
Возврат токена
```

### Превентивное обновление

Токен обновляется **за 5 минут** до истечения:

```
Токен получен → Экспирация: +30 мин
                  ↓
              Auto-refresh thread (каждые 60 сек)
                  ↓
            Проверка: time + 300 >= expiry?
                  ↓
              [да] → Обновить токен
              [нет] → Использовать кэш
```

## Решение проблем

### Проблема: "Токен не является валидным JWT"

**Решение:** Fallback работает корректно (30 минут по умолчанию).

### Проблема: OAuth 400 Unauthorized

**Причина:** Отсутствуют RqUID или Accept заголовки.

**Решение:** Обновите TokenRefreshService (обязательные заголовки добавлены).

### Проблема: Токен не обновляется

**Проверьте:**
1. ✅ GIGACHAT_CLIENT_ID и GIGACHAT_CLIENT_SECRET настроены
2. ✅ Auto-refresh запущен: `service.start_auto_refresh()`
3. ✅ Файрвол не блокирует запросы к `ngw.devices.sberbank.ru`

## Безопасность

### Хранение токенов

- ⚠️ **Никогда** не коммитьте `.env` с реальными токенами
- ✅ Используйте `.env.example` с шаблонами
- ✅ `.gitignore` должен включать `.env`

### Рекомендации

```bash
# .gitignore
.env
.env.local
.env.*.local
```

```bash
# .env.example
GIGACHAT_CLIENT_ID="your-client-id-here"
GIGACHAT_CLIENT_SECRET="your-client-secret-here"  # pragma: allowlist secret
GIGACHAT_VERIFY_SSL="false"
```

## Мониторинг

### Prometheus метрики (в ConfigManager)

```python
# Автоматически собираются:
- config_loads_total
- config_reloads_total
- config_load_duration_seconds
- config_validation_errors_total
```

### Логирование

```python
import logging
logging.basicConfig(level=logging.INFO)

# Пример логов:
INFO: TokenRefreshService инициализирован (verify_ssl=False)
INFO: Запрос нового токена GigaChat (RqUID=...)
INFO: Токен GigaChat успешно получен (expires in ~30 мин)
INFO: Auto-refresh запущен (interval=60s)
```

## Best Practices

### 1. Всегда запускайте auto-refresh

```python
# ❌ Плохо: токен может истечь в любой момент
token = service.get_token()

# ✅ Хорошо: токен всегда валиден
service.start_auto_refresh(interval=60)
token = service.get_token()
```

### 2. Проверяйте возвращаемый токен

```python
token = config.get_gigachat_token()
if not token:
    logger.error("Токен GigaChat недоступен")
    return
```

### 3. Используйте ConfigManager как singleton

```python
# ❌ Плохо: много экземпляров
config1 = ConfigManager("config1.yaml")
config2 = ConfigManager("config2.yaml")

# ✅ Хорошо: один экземпляр
config = ConfigManager("config.yaml")
```

### 4. Останавливайте сервис при завершении

```python
try:
    config.start_token_auto_refresh(interval=60)
    # Ваш код
finally:
    config.stop_token_auto_refresh()
```

## Миграция со старой версии

### До ( without RqUID)

```python
headers = {
    "Authorization": f"Basic {encoded_auth}",
    "Content-Type": "application/x-www-form-urlencoded",
}
# ❌ Не работает: 400 Unauthorized
```

### После ( with RqUID)

```python
headers = {
    "Authorization": f"Basic {encoded_auth}",
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "application/json",  # ✅ Обязательно
    "RqUID": str(uuid.uuid4()),    # ✅ Обязательно
}
# ✅ Работает: 200 OK
```

## Troubleshooting

### Логи

```bash
# Включить отладку
export LOG_LEVEL=DEBUG

# Запустить демо
python demo_token_refresh.py
```

### Проверка токена

```python
service = TokenRefreshService()
token = service.get_token()

if token:
    print(f"Токен валиден (длина: {len(token)})")
else:
    print("Токен недоступен")
    print("Проверьте GIGACHAT_CLIENT_ID и GIGACHAT_CLIENT_SECRET")
```

### Сетевые проблемы

```bash
# Проверка доступности API
curl -X POST https://ngw.devices.sberbank.ru:9443/api/v2/oauth \
  -H "Authorization: Basic ..." \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "scope=GIGACHAT_API_PERS&grant_type=client_credentials"
```

## Вопросы?

Смотрите:
- `GIGACHAT_SETUP.md` - начальная настройка
- `INTEGRATION_SUMMARY_RU.md` - общий отчёт интеграции
- `ARCHITECTURE.md` - архитектура системы
