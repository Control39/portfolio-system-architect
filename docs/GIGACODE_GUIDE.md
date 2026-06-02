# 📘 Полное руководство по GigaCode

## 📋 Содержание

1. [Что такое GigaCode](#что-такое-gigacode)
2. [Быстрый старт](#быстрый-старт)
3. [Настройка токена](#настройка-токена)
4. [Использование](#использование)
5. [Оптимизация](#оптимизация)
6. [Troubleshooting](#troubleshooting)

---

## Что такое GigaCode

**GigaCode** — AI-ассистент для разработки на русском языке (расширение VS Code от Сбера):

- ✅ **Автодополнение кода** (как GitHub Copilot)
- ✅ **Чат с AI** (объяснение, рефакторинг, генерация)
- ✅ **Режим Agent** (сложные задачи, анализ проекта)
- ✅ **Режим Ask** (вопросы по коду)

**Модели:**
| Модель | Назначение | Токенов |
|--------|-----------|---------|
| **GigaChat-Lite** | Основная работа | 899k |
| **GigaChat-Pro** | Сложные задачи | 50k |
| **GigaChat-Max** | Критичные решения | 45k |

---

## Быстрый старт

### 1. Установить расширение

```powershell
code --install-extension GigaCode.gigacode-vscode
```

Или через Marketplace:
1. Открыть Extensions (`Ctrl+Shift+X`)
2. Найти "GigaCode"
3. Нажать "Install"

### 2. Настроить токен

```powershell
.\scripts\refresh-gigacode-token.ps1
```

### 3. Перезагрузить VS Code

```
Ctrl+Shift+P → "Developer: Reload Window"
```

### 4. Проверить работу

Откройте чат (`Ctrl+Shift+L`) и напишите:
```
@agent привет
```

---

## Настройка токена

### Получить токен

1. Зайдите на [https://gigachat.cloud](https://gigachat.cloud)
2. Авторизуйтесь через Sber ID
3. Перейдите в раздел "API Keys"
4. Создайте новый токен
5. Скопируйте токен

### Обновить токен вручную

```powershell
# Откройте .vscode/settings.json
code .vscode/settings.json

# Найдите строку "gigacode.bearerToken"
# Замените значение на новый токен
```

### Автоматическое обновление

**Вариант 1: Планировщик задач**
```
.\scripts\setup-gigacode-autorefresh.ps1
```

**Вариант 2: Ручное обновление каждые 30 минут**
```
.\scripts\refresh-gigacode-token.ps1
```

---

## Использование

### Режимы работы

#### @agent — Режим агента (сложные задачи)
```
@agent проанализируй архитектуру проекта
@agent исправь баг в функции X
@agent создай тесты для модуля Y
```

#### ? — Режим Ask (вопросы)
```
? Как работает эта функция?
? Объясни паттерн проектирования
? Что делает этот класс?
```

#### Inline чат (Ctrl+I)
Выделите код → `Ctrl+I` → введите запрос:
```
Рефакторинг
Добавить комментарии
Написать тесты
```

### Примеры запросов

| Задача | Пример запроса |
|--------|---------------|
| Объяснить код | `@agent объясни, что делает эта функция` |
| Найти баг | `@agent найди потенциальные уязвимости в этом коде` |
| Рефакторинг | `@agent оптимизируй этот код` |
| Генерация | `@agent создай REST API на FastAPI для CRUD операций` |
| Документация | `? напиши docstring для этой функции` |

### Горячие клавиши

| Команда | Клавиши |
|---------|---------|
| Открыть чат | `Ctrl+Shift+L` |
| Inline чат | `Ctrl+I` |
| Перезапуск расширения | `Ctrl+Shift+P` → "GigaCode: Restart" |
| Показать логи | `Ctrl+Shift+U` → "GigaCode" |

---

## Оптимизация

### Уменьшить расход токенов

```json
{
  "gigacode.maxContextTokens": 4096,
  "gigacode.maxResponseTokens": 2048,
  "gigacode.enableWorkspaceContext": false,
  "gigacode.autoSuggest": false
}
```

### Ускорить работу

```json
{
  "gigacode.suggestDelay": 500,
  "gigacode.contextWindow": 2000,
  "gigacode.useLightModel": true
}
```

### Включить только для Python

```json
{
  "gigacode.python.enabled": true,
  "gigacode.typescript.enabled": false,
  "gigacode.javascript.enabled": false
}
```

---

## Troubleshooting

### Проблема: 403 Forbidden

**Причина:** Токен просрочен (действует 30 минут)

**Решение:**
```
.\scripts\refresh-gigacode-token.ps1
```

### Проблема: 401 Unauthorized

**Причина:** OAuth credentials невалидны

**Решение:**
1. Получите новый Client ID/Secret на [gigachat.cloud](https://gigachat.cloud)
2. Обновите `tools/devtools/.devtools/.gigacode/personal.env`
3. Запустите скрипт обновления

### Проблема: Медленная работа

**Решение:**
1. Уменьшите `maxContextTokens` до 2048
2. Отключите `enableWorkspaceContext`
3. Используйте GigaChat-Lite вместо Pro/Max

### Проблема: Расширение не отвечает

**Решение:**
```
Ctrl+Shift+P → "GigaCode: Restart"
```

### Проблема: Ошибка 413 (Request Entity Too Large)

**Решение:**
```json
{
  "gigacode.maxContextTokens": 2048,
  "gigacode.enableWorkspaceContext": false
}
```

---

## 📞 Полезные ссылки

- [Официальная документация](https://developers.sber.ru/docs/ru/gigachat)
- [Telegram канал](https://t.me/gigacode_ru)
- [Marketplace](https://marketplace.visualstudio.com/items?itemName=GigaCode.gigacode-vscode)

---

*Последнее обновление: 31 мая 2026 г.*