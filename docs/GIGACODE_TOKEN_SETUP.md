# 🔑 Настройка токена GigaCode

## 📋 Что нужно знать

- **Access Token** действует **30 минут**
- **OAuth credentials** (Client ID/Secret) — постоянные
- Токен хранится в `.vscode/settings.json`
- Credentials хранятся в `tools/devtools/.devtools/.gigacode/personal.env`

---

## 🔧 Получение OAuth credentials

### Шаг 1: Зарегистрируйтесь на gigachat.cloud

1. Откройте [https://gigachat.cloud](https://gigachat.cloud)
2. Нажмите "Регистрация" / "Sign Up"
3. Войдите через Sber ID

### Шаг 2: Создайте OAuth-приложение

1. Перейдите в раздел **"API Keys"** или **"Developer Console"**
2. Нажмите **"Create New Application"** / **"Создать приложение"**
3. Заполните:
   - **Name:** `Portfolio System Architect` (или любое)
   - **Description:** `AI assistant for portfolio system`
   - **Callback URL:** `http://localhost` (для тестов)

### Шаг 3: Получите Client ID и Client Secret

После создания приложения вы увидите:
- **Client ID:** `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- **Client Secret:** `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`

**⚠️ Скопируйте Client Secret сразу!** После закрытия окна его нельзя будет увидеть снова.

### Шаг 4: Encode в Base64

Создайте строку `ClientID:ClientSecret` и закодируйте в Base64:

```python
import base64

client_id = "REDACTED_CLIENT_ID"
client_secret = "REDACTED_CLIENT_SECRET_2"

auth_string = f"{client_id}:{client_secret}"
auth_key = base64.b64encode(auth_string.encode()).decode()

print(auth_key)
# Вывод: REDACTED_AUTH_KEY_1
```

---

## 📝 Обновление credentials

### Файл: `tools/devtools/.devtools/.gigacode/personal.env`

```ini
# OAuth Credentials для Sber GigaChat
GIGACODE_AUTH_KEY=REDACTED_AUTH_KEY_1

# Scope для OAuth
GIGACODE_SCOPE=GIGACHAT_API_PERS

# OAuth Endpoint
GIGACODE_OAUTH_ENDPOINT=https://ngw.devices.sberbank.ru:9443/api/v2/oauth

# API Endpoint
GIGACODE_API_ENDPOINT=https://gigachat.devices.sberbank.ru/api/v1

# Модель по умолчанию
GIGACODE_MODEL=GigaChat-Lite

# Лимиты
GIGACODE_MAX_CONTEXT_TOKENS=4096
GIGACODE_MAX_RESPONSE_TOKENS=2048
```

**⚠️ NEVER commit this file to git!** (в `.gitignore`)

---

## 🔄 Получение Access Token

### Автоматически (рекомендуется)

```powershell
.\scripts\refresh-gigacode-token.ps1
```

**Что делает:**
1. Получает Access Token через OAuth (используя `personal.env`)
2. Обновляет `.vscode/settings.json` с новым токеном
3. Кэширует токен в `.token_cache.json`

### Вручную через Python

```powershell
cd C:\repo\tools\devtools\.devtools\.gigacode
$env:PYTHONPATH="C:\repo"
.\.venv\Scripts\python.exe get_token.py
```

### Вручную через curl

```bash
# Получить токен
curl -X POST https://ngw.devices.sberbank.ru:9443/api/v2/oauth \
  -H "Authorization: Basic REDACTED_AUTH_KEY_1" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "RqUID: $(uuidgen)" \
  -d "scope=GIGACHAT_API_PERS"

# Вывод: {"access_token": "eyJ...", "expires_in": 1800}
```

---

## 📍 Обновление токена в VS Code

### Способ 1: Автоматический (скрипт)

```powershell
.\scripts\refresh-gigacode-token.ps1
```

### Способ 2: Ручной

1. Откройте `.vscode/settings.json`
2. Найдите строку:
   ```json
   "gigacode.bearerToken": "eyJ..."
   ```
3. Замените значение на новый токен
4. Сохраните файл

### Способ 3: Через PowerShell

```powershell
$token = "eyJ..."  # ваш новый токен
$settings = Get-Content .vscode\settings.json | ConvertFrom-Json
$settings.gigacode.bearerToken = $token
$settings | ConvertTo-Json -Depth 100 | Out-File .vscode\settings.json -Encoding UTF8
```

---

## ⏰ Автоматическое обновление

### Вариант 1: Планировщик задач Windows

```powershell
.\scripts\setup-gigacode-autorefresh.ps1
```

**Что создаёт:**
- Задачу `GigaCodeTokenRefresh` в Планировщике
- Запускается каждые 25 минут
- Обновляет токен автоматически

**Проверка:**
```powershell
schtasks /Query /TN GigaCodeTokenRefresh
```

**Управление:**
```powershell
# Запустить вручную
schtasks /Run /TN GigaCodeTokenRefresh

# Остановить
schtasks /End /TN GigaCodeTokenRefresh

# Удалить
schtasks /Delete /TN GigaCodeTokenRefresh /F
```

### Вариант 2: Ручной запуск по требованию

Настройте напоминание:
- Каждые 25-28 минут (токен действует 30 мин)
- Запустить: `.\scripts\refresh-gigacode-token.ps1`

---

## 🔐 Безопасность

### Где хранятся секреты

| Файл | Содержит | Исключён из git? |
|------|----------|------------------|
| `.vscode/settings.json` | Access Token | ⚠️ **Да** (но лучше не коммитить) |
| `tools/.../personal.env` | OAuth credentials | ✅ **Да** (в `.gitignore`) |
| `tools/.../.token_cache.json` | Кэш токена | ✅ **Да** (в `.gitignore`) |

### Рекомендации

1. **Никогда не коммитьте** файлы с токенами
2. Используйте `.env` для credentials
3. Регулярно обновляйте Client Secret (раз в 3-6 месяцев)
4. Ограничьте доступ к `personal.env` (chmod 600)

### Проверка на утечки

```powershell
# Проверить, нет ли токенов в git history
git log -p --all -- .vscode/settings.json | Select-String "bearerToken"
```

---

## 🐛 Troubleshooting

### Ошибка: 401 Unauthorized

**Причина:** OAuth credentials невалидны или просрочены

**Решение:**
1. Проверьте `personal.env`
2. Убедитесь, что `GIGACODE_AUTH_KEY` корректен
3. Получите новые credentials на gigachat.cloud

### Ошибка: 403 Forbidden

**Причина:** Access Token просрочен

**Решение:**
```powershell
.\scripts\refresh-gigacode-token.ps1
```

### Ошибка: SSL certificate verification failed

**Причина:** Корпоративный прокси с самоподписанным сертификатом

**Решение:**
1. Добавьте исключение в `get_token.py`:
   ```python
   import urllib3
   urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
   ```
2. Или установите корпоративный корневой сертификат

### Ошибка: ModuleNotFoundError: No module named 'apps'

**Причина:** PYTHONPATH не настроен

**Решение:**
```powershell
$env:PYTHONPATH="C:\repo"
```

---

## 📞 Полезные ссылки

- [OAuth 2.0 документация](https://developers.sber.ru/docs/ru/gigachat/oauth)
- [API Reference](https://developers.sber.ru/docs/ru/gigachat/api/rest)
- [Получить токены](https://gigachat.cloud)

---

*Последнее обновление: 31 мая 2026 г.*