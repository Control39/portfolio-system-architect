# 🧭 GigaCode: Единая конфигурация и руководство

**Версия:** 1.0 (31 мая 2026 г.)  
**Статус:** Production Ready ✅

---

## 📋 Быстрый доступ

| Задача | Команда / Ссылка |
|--------|------------------|
| **Обновить токен** | `\.\scripts\refresh-gigacode-token.ps1` |
| **Диагностика** | `\.\scripts\setup-gigacode.ps1` |
| **Автообновление** | `\.\scripts\setup-gigacode-autorefresh.ps1` |
| **Полное руководство** | [docs/GIGACODE_GUIDE.md](docs/GIGACODE_GUIDE.md) |
| **Настройка токена** | [docs/GIGACODE_TOKEN_SETUP.md](docs/GIGACODE_TOKEN_SETUP.md) |

---

## 🗂️ Структура файлов

```
C:\repo\
├── .vscode/
│   ├── settings.json              ← Личные настройки (ТОКЕН) ⚠️ НЕ КОММИТИТЬ
│   └── settings-default.json      ← Шаблон (без токена) ✅
│
├── tools/devtools/.devtools/.gigacode/
│   ├── personal.env               ← OAuth credentials ⚠️ НЕ КОММИТИТЬ
│   ├── .token_cache.json          ← Кэш токена (30 мин) ⚠️ НЕ КОММИТИТЬ
│   ├── config.yaml                ← Настройки расширения ✅
│   ├── get_token.py               ← Скрипт получения токена ✅
│   └── update_vscode_token.py     ← Обновление настроек VS Code ✅
│
├── scripts/
│   ├── refresh-gigacode-token.ps1 ← Обновление токена (рекомендуется) ✅
│   ├── setup-gigacode.ps1         ← Диагностика ✅
│   ├── setup-gigacode-autorefresh.ps1 ← Автообновление ✅
│   └── run_gigacode_update.py     ← Обёртка Python ✅
│
├── config/ai/
│   └── ai-models.yaml             ← Конфиг моделей (Lite/Pro/Max) ✅
│
└── docs/
    ├── GIGACODE_GUIDE.md          ← Полное руководство ✅
    └── GIGACODE_TOKEN_SETUP.md    ← Настройка токена ✅
```

---

## 🔑 Ключевые настройки

### .vscode/settings.json (Личные)

```json
{
  "gigacode.enable": true,
  "gigacode.model": "GigaChat-Latest",
  "gigacode.bearerToken": "eyJ...",  // ⚠️ Обновляется каждые 30 мин
  "gigacode.maxTokens": 8192,
  "gigacode.timeout": 60000,
  "gigacode.enableAgent": true,
  "gigacode.enableAsk": true
}
```

### tools/.../.gigacode/personal.env (Credentials)

```ini
GIGACODE_AUTH_KEY=REDACTED_AUTH_KEY_1
GIGACODE_SCOPE=GIGACHAT_API_PERS
GIGACODE_OAUTH_ENDPOINT=https://ngw.devices.sberbank.ru:9443/api/v2/oauth
GIGACODE_API_ENDPOINT=https://gigachat.devices.sberbank.ru/api/v1
```

### tools/.../.gigacode/config.yaml (Расширение)

```yaml
api:
  base_url: "https://gigachat.devices.sberbank.ru/api/v1"

limits:
  max_context_tokens: 4096
  max_response_tokens: 2048
  max_request_size_bytes: 524288

context:
  auto_include_project_context: false
  include_active_file: true
  include_open_tabs: false

features:
  code_completion: true
  inline_chat: true
  workspace_chat: false
```

---

## 🚀 Рабочий процесс

### Первый запуск

1. **Установить расширение:**
   ```powershell
   code --install-extension GigaCode.gigacode-vscode
   ```

2. **Получить OAuth credentials:**
   - Зайти на [gigachat.cloud](https://gigachat.cloud)
   - Создать приложение
   - Скопировать Client ID + Secret
   - Закодировать в Base64
   - Вставить в `personal.env`

3. **Получить первый токен:**
   ```powershell
   .\scripts\refresh-gigacode-token.ps1
   ```

4. **Перезагрузить VS Code:**
   ```
   Ctrl+Shift+P → "Developer: Reload Window"
   ```

5. **Проверить работу:**
   ```
   Ctrl+Shift+L → @agent привет
   ```

### Ежедневная работа

**Вариант А: Автоматическое обновление (рекомендуется)**
```powershell
.\scripts\setup-gigacode-autorefresh.ps1
```
→ Токен обновляется каждые 25 минут автоматически

**Вариант Б: Ручное обновление**
```powershell
# Каждые 30 минут или при ошибке 403
.\scripts\refresh-gigacode-token.ps1
```

### Диагностика проблем

```powershell
# Запустить полную диагностику
.\scripts\setup-gigacode.ps1

# Проверить статус токена
.\scripts\GigaCode.psm1; Get-GigaCodeStatus

# Проверить логи расширения
Ctrl+Shift+U → "GigaCode"
```

---

## 📊 Модели и их использование

| Модель | Назначение | Токенов | Когда использовать |
|--------|-----------|---------|-------------------|
| **GigaChat-Lite** | Основная работа | 899k | Автодополнение, простые вопросы, рефакторинг |
| **GigaChat-Pro** | Сложные задачи | 50k | Архитектурный анализ, генерация кода с нуля |
| **GigaChat-Max** | Критичные решения | 45k | Security audit, оптимизация, сложные алгоритмы |

**Настройка в `.agents/config/agent-config.yaml`:**
```yaml
default: "gigachat-lite"
smart_selection:
  - task_type == "quick_edit" → gigachat-lite
  - task_type == "architecture" → gigachat-pro
  - task_type == "security" → gigachat-max
  - gigachat_unavailable → ollama (fallback)
```

---

## 🛡️ Безопасность

### Что НЕЛЬЗЯ коммитить

| Файл | Причина | Исключён? |
|------|---------|-----------|
| `.vscode/settings.json` | Содержит токен | ⚠️ Частично (проверять вручную) |
| `personal.env` | OAuth credentials | ✅ Да (в `.gitignore`) |
| `.token_cache.json` | Кэш токена | ✅ Да (в `.gitignore`) |

### Проверка перед коммитом

```powershell
# Проверить, нет ли секретов в staged файлах
git diff --cached | Select-String "bearerToken|GIGACODE_AUTH_KEY"

# Проверить историю
git log -p --all -- .vscode/settings.json | Select-String "eyJ"
```

### Рекомендации

1. **Регулярно обновляйте** Client Secret (раз в 3-6 месяцев)
2. **Используйте разные** credentials для dev/prod
3. **Ограничьте доступ** к `personal.env` (chmod 600)
4. **Мониторьте** использование токенов в личном кабинете

---

## 🐛 Частые проблемы и решения

| Проблема | Причина | Решение |
|----------|---------|---------|
| **403 Forbidden** | Токен просрочен | `.\scripts\refresh-gigacode-token.ps1` |
| **401 Unauthorized** | Неверные credentials | Обновить `personal.env` |
| **413 Request Too Large** | Контекст слишком большой | Уменьшить `maxContextTokens` до 2048 |
| **SSL certificate error** | Корпоративный прокси | Добавить `verify=False` в `get_token.py` |
| **Модуль не найден** | PYTHONPATH не настроен | `$env:PYTHONPATH="C:\repo"` |
| **Расширение не отвечает** | Завис процесс | `Ctrl+Shift+P` → "GigaCode: Restart" |

---

## 📞 Полезные ресурсы

| Ресурс | Ссылка |
|--------|--------|
| **Официальная документация** | [developers.sber.ru/docs/ru/gigachat](https://developers.sber.ru/docs/ru/gigachat) |
| **Получить токены** | [gigachat.cloud](https://gigachat.cloud) |
| **Marketplace** | [VS Code Marketplace](https://marketplace.visualstudio.com/items?itemName=GigaCode.gigacode-vscode) |
| **Telegram канал** | [t.me/gigacode_ru](https://t.me/gigacode_ru) |
| **API Reference** | [REST API](https://developers.sber.ru/docs/ru/gigachat/api/rest) |

---

## 📝 История изменений

| Дата | Изменение | Автор |
|------|-----------|-------|
| 31.05.2026 | Создан единый гайд, удалены дубликаты | Koda AI |
| 24.05.2026 | Обновлены OAuth credentials | Екатерина Куделя |
| 12.05.2026 | Первоначальная настройка | Koda AI |

---

**Готово!** 🎉  
Теперь GigaCode настроен и готов к работе.

**Следующие шаги:**
1. Перезагрузите VS Code
2. Проверьте работу: `@agent привет`
3. Настройте автообновление (рекомендуется)
