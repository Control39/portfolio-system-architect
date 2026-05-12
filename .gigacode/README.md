# .gigacode/ — Конфигурация GigaChat

## Назначение

Эта папка содержит конфигурацию для интеграции с **Sber GigaChat API**:
- Личный API-ключ для расширения VS Code
- Скрипты для автоматического получения Access Token
- Настройки для проектного MCP-сервера

⚠️ **ВСЕ ФАЙЛЫ В ЭТОЙ ПАПКЕ ИГНОРИРУЮТСЯ GIT** (см. `.gitignore`)

---

## Файлы

### `personal.env`
Личные OAuth-credential для Sber GigaChat:
- `GIGACODE_AUTH_KEY` — Base64 encoded Client ID:Secret
- `GIGACODE_SCOPE` — OAuth scope (GIGACHAT_API_PERS)
- `GIGACODE_API_ENDPOINT` — API endpoint

### `project.env`
Проектные настройки для MCP-сервера (если используется корпоративный ключ)

### `get_token.py`
Скрипт для получения Access Token через OAuth 2.0:
```bash
cd .gigacode
python get_token.py
```

**Что делает:**
1. Получает Access Token через POST `/api/v2/oauth`
2. Кэширует токен в `.token_cache.json` (действует 30 мин)
3. Проверяет валидность через `/api/v1/models`
4. Выводит токен для использования

### `update_vscode_token.py`
Автоматически обновляет `.vscode/settings.json` с актуальным токеном:
```bash
cd .gigacode
python update_vscode_token.py
```

**Что делает:**
1. Получает Access Token через `get_token.py`
2. Обновляет `.vscode/settings.json` с заголовком `Authorization: Bearer <token>`
3. Готово для расширения Gigacode в VS Code

### `config.yaml`
Настройки расширения Gigacode (опционально):
- Лимиты токенов (чтобы избежать ошибки 413)
- Настройки контекста
- Включение/отключение функций

---

## Использование

### 1. Первый запуск

```bash
# Получите Access Token
cd .gigacode
python get_token.py

# Проверьте работу
# Токен будет выведен в консоли
```

### 2. Настройка VS Code

```bash
# Автоматически обновить .vscode/settings.json
python update_vscode_token.py

# Перезагрузите VS Code
# Ctrl+Shift+P → "Developer: Reload Window"
```

### 3. Ручное использование токена

```bash
# Получить токен и скопировать его
python get_token.py
# Скопируйте вывод Access Token

# Использовать в запросе:
curl https://gigachat.devices.sberbank.ru/api/v1/chat/completions \
  -H "Authorization: Bearer <ваш_токен>" \
  -H "Content-Type: application/json" \
  -d '{"model": "GigaChat", "messages": [{"role": "user", "content": "Привет!"}]}'
```

---

## OAuth Flow

```
┌─────────────────┐     POST /api/v2/oauth      ┌─────────────────┐
│  Client         │ ───────────────────────────▶ │  Sber OAuth     │
│  (Authorization │     Basic auth + scope       │  Endpoint       │
│   Key)          │                              │                 │
└─────────────────┘                              └────────┬────────┘
                                                          │
                                                          ▼
                                                ┌─────────────────┐
                                                │  Access Token   │
                                                │  (30 минут)     │
                                                └────────┬────────┘
                                                         │
                                                         │ Bearer token
                                                         ▼
                                                ┌─────────────────┐
                                                │  GigaChat API   │
                                                │  /api/v1/*      │
                                                └─────────────────┘
```

---

## Ошибки

### Ошибка 413 (Request Entity Too Large)
**Причина:** Слишком большой контекст запроса

**Решение:**
1. Уменьшите `maxContextTokens` в `.vscode/settings.json` (2048 или 4096)
2. Отключите `enableWorkspaceContext`
3. Используйте `config.yaml` для ограничения размера запроса

### Ошибка 401 (Unauthorized)
**Причина:** Просрочен Access Token (действует 30 мин)

**Решение:**
```bash
python update_vscode_token.py
# или
python get_token.py
```

### Ошибка подключения к OAuth endpoint
**Причина:** Нет доступа к `ngw.devices.sberbank.ru:9443`

**Решение:**
- Проверьте корпоративный прокси/фаервол
- Попробуйте с другого сети (домашняя)
- Свяжитесь с IT-отделом для открытия порта 9443

---

## Обновление токена

Access Token действует **30 минут**. Автоматического обновления нет в расширении VS Code, поэтому:

**Вариант 1: Ручное обновление каждые 30 мин**
```bash
python update_vscode_token.py
```

**Вариант 2: Автоматизация через task scheduler**
Создайте задачу Windows Task Scheduler на запуск скрипта каждые 25 минут.

**Вариант 3: Интеграция в расширение**
Если расширение поддерживает custom auth provider — настройте hook на обновление.

---

## Безопасность

- ✅ Файлы в `.gigacode/` игнорируются git
- ✅ Токен кэшируется локально в `.token_cache.json`
- ✅ Никогда не коммитьте эти файлы!
- ✅ Используйте разные ключи для личного и проектного использования

---

## Документация API

- [Официальная документация Sber GigaChat](https://developers.sber.ru/docs/ru/gigachat)
- [REST API спецификация](https://developers.sber.ru/docs/ru/gigachat/api/rest)
- [gRPC API спецификация](https://developers.sber.ru/docs/ru/gigachat/api/grpc)

---

*Конфигурация создана 12 мая 2026 г.*
