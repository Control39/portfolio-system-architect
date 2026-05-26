# Получение Bearer Token для GigaChat

## Проблема
Текущий токен не работает (403 Forbidden)

## Решение

### Вариант 1: Через Sber ID (рекомендуется)

1. **Зайдите в [GigaChat Portal](https://gigachat.dev/)**
   - Авторизуйтесь через Sber ID
   - Перейдите в раздел "API Keys" или "Токены"

2. **Создайте новый токен:**
   - Нажмите "Create new token" или "Создать токен"
   - Дайте имя (например, "VSCode-GigaCode")
   - Скопируйте токен

3. **Добавьте токен в настройки:**
   ```json
   {
     "gigacode.bearerToken": "ВАШ_НОВЫЙ_ТОКЕН"
   }
   ```

### Вариант 2: Через авторизационный код

1. **Получите авторизационный код:**
   ```bash
   # Откройте в браузере
   https://ngw.devices.sberbank.ru:9443/api/v2/oauth
   ?scope=GIGACHAT_API_PERS
   &response_type=code
   &redirect_uri=https://gigachat.devices.sberbank.ru/api/v2/oauth
   &client_id=ВАШ_CLIENT_ID
   ```

2. **Обменяйте код на токен:**
   ```bash
   curl -X POST https://ngw.devices.sberbank.ru:9443/api/v2/oauth \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "client_id=ВАШ_CLIENT_ID" \
     -d "client_secret=ВАШ_CLIENT_SECRET" \
     -d "code=ПОЛУЧЕННЫЙ_КОД" \
     -d "redirect_uri=https://gigachat.devices.sberbank.ru/api/v2/oauth"
   ```

3. **Получите access_token из ответа**

### Вариант 3: Через Sber ID (упрощённый)

1. **Установите расширение GigaChat для VS Code**
   - Откройте VS Code
   - Ctrl+Shift+P → "Extensions: Install Extensions"
   - Найдите "GigaChat"
   - Установите

2. **Авторизуйтесь:**
   - Откройте панель GigaChat
   - Нажмите "Login with Sber ID"
   - Авторизуйтесь в браузере
   - Токен сохранится автоматически

### Вариант 4: Через API Sber ID

1. **Получите Client ID и Client Secret:**
   - Зайдите в [Sber ID Developer Portal](https://developers.sber.ru/)
   - Создайте новое приложение
   - Скопируйте Client ID и Client Secret

2. **Получите токен через API:**
   ```powershell
   # PowerShell скрипт для получения токена
   $clientId = "ВАШ_CLIENT_ID"
   $clientSecret = "ВАШ_CLIENT_SECRET"
   
   $auth = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("$clientId:$clientSecret"))
   
   $response = Invoke-RestMethod -Uri "https://ngw.devices.sberbank.ru:9443/api/v2/oauth" \
     -Method POST \
     -Headers @{
       "Authorization" = "Basic $auth"
       "Content-Type" = "application/x-www-form-urlencoded"
     } \
     -Body "scope=GIGACHAT_API_PERS&grant_type=client_credentials"
   
   $response.access_token
   ```

## Обновление токена в VS Code

### Способ 1: Через settings.json

1. Откройте `.vscode/settings.json`
2. Найдите строку `"gigacode.bearerToken"`
3. Замените значение на новый токен
4. Сохраните файл
5. Перезагрузите VS Code

### Способ 2: Через команду

```powershell
# Запустите скрипт обновления
.\scripts\update-gigacode-token.ps1
```

### Способ 3: Через интерфейс GigaCode

1. Откройте палету команд: `Ctrl+Shift+P`
2. Введите: `GigaCode: Update Token`
3. Вставьте новый токен
4. Перезапустите расширение

## Проверка токена

```powershell
# Скрипт проверки токена
$token = "ВАШ_ТОКЕН"
$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

$response = Invoke-RestMethod -Uri "https://gigachat.devices.sberbank.ru/api/v1/health" \
  -Method GET \
  -Headers $headers

Write-Host "✅ Токен валиден: $($response.status)"
```

## Сроки действия токенов

| Тип токена | Срок действия | Обновление |
|------------|--------------|------------|
| Access Token | 1 час | Автоматическое |
| Refresh Token | 30 дней | Через авторизацию |
| API Key | Постоянно | Вручную |

## Troubleshooting

### Проблема: 403 Forbidden
**Решение:**
1. Проверьте, что токен не истёк
2. Убедитесь, что токен имеет scope `GIGACHAT_API_PERS`
3. Пересоздайте токен

### Проблема: 401 Unauthorized
**Решение:**
1. Проверьте формат токена (Bearer)
2. Убедитесь, что нет пробелов
3. Скопируйте токен заново

### Проблема: 429 Too Many Requests
**Решение:**
1. Уменьшите количество запросов
2. Увеличьте `rateLimit` в настройках
3. Проверьте лимиты вашего тарифа

## Полезные ссылки

- [Официальная документация GigaChat](https://developers.sber.ru/docs/ru/gigachat)
- [Sber ID Developer Portal](https://developers.sber.ru/)
- [GigaChat API Reference](https://gigachat.dev/docs/api)
- [Примеры использования](https://github.com/sbercloud-ai/gigachat-examples)

---

**Важно:** Никогда не коммитьте токены в Git! Используйте `.gitignore` для `settings.json` или переменные окружения.
