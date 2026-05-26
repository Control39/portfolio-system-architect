# GigaCode - Руководство по использованию

## 🚀 Быстрый старт

### Установка и настройка
```powershell
# Запуск скрипта настройки
.\scripts\setup-gigacode.ps1
```

### Перезапуск расширения
```
Ctrl+Shift+P → GigaCode: Restart
```

---

## 🤖 Режимы работы

### 1. **Agent Mode** (Агент)
**Назначение:** Выполнение сложных задач, анализ кода, рефакторинг

**Активация:**
- `Ctrl+Shift+P` → `GigaCode: Agent Mode`
- Или начните сообщение с `@agent`

**Примеры запросов:**
```
@agent проанализируй архитектуру проекта
@agent исправь баг в файле X
@agent создай тесты для функции Y
@agent оптимизируй код в модуле Z
```

**Параметры:**
```json
"gigacode.agentMode": "auto"  // auto, manual, disabled
"gigacode.enableAgent": true
```

**Частые проблемы и решения:**

| Проблема | Решение |
|----------|---------|
| Режим агента ломается | Перезапустите расширение: `GigaCode: Restart` |
| Медленный ответ | Увеличьте `timeout` до 60000 |
| Недостаточно контекста | Увеличьте `contextWindow` до 4096 |
| Ошибки сети | Проверьте `sslVerify: false` для Sber GigaChat |

---

### 2. **Ask Mode** (Вопрос-ответ)
**Назначение:** Быстрые вопросы, объяснение кода, поиск информации

**Активация:**
- `Ctrl+Shift+P` → `GigaCode: Ask`
- Или начните сообщение с `?`

**Примеры запросов:**
```
? Что делает эта функция?
? Как работает контекстный менеджер?
? Найди все места, где используется X
? Объясни паттерн проектирования Y
```

**Параметры:**
```json
"gigacode.askMode": "smart"  // smart, simple, detailed
"gigacode.enableAsk": true
```

**Частые проблемы и решения:**

| Проблема | Решение |
|----------|---------|
| Неполные ответы | Установите `askMode: "detailed"` |
| Медленная генерация | Уменьшите `temperature` до 0.5 |
| Не понимает контекст | Выделите код перед запросом |
| Слишком длинные ответы | Установите `maxTokens: 4096` |

---

### 3. **Code Completion** (Автодополнение)
**Назначение:** Автодополнение кода в реальном времени

**Активация:** Автоматически при вводе

**Параметры:**
```json
"gigacode.enableCodeCompletion": true,
"gigacode.enableSuggestions": true
```

**Горячие клавиши:**
- `Tab` - Принять предложение
- `Ctrl+Enter` - Показать следующие предложения
- `Esc` - Отклонить предложение

---

### 4. **Inline Chat** (Встроенный чат)
**Назначение:** Быстрые правки кода без переключения окон

**Активация:**
- `Ctrl+I` - Открыть inline чат
- Напишите задачу, например: "добавь обработку ошибок"

**Примеры:**
```
Добавь type hints
Сделай функцию асинхронной
Добавь логирование
Оптимизируй этот цикл
```

---

## ⚙️ Настройки

### Основные настройки (`.vscode/settings.json`)
```json
{
  "gigacode.enable": true,
  "gigacode.model": "GigaChat-Latest",
  "gigacode.maxTokens": 8192,
  "gigacode.timeout": 60000,
  "gigacode.retries": 3,
  "gigacode.temperature": 0.7,
  "gigacode.enableAgent": true,
  "gigacode.enableAsk": true,
  "gigacode.agentMode": "auto",
  "gigacode.askMode": "smart"
}
```

### Продвинутые настройки (`.koda/config.json`)
```json
{
  "gigacode.topP": 0.9,
  "gigacode.topK": 40,
  "gigacode.presencePenalty": 0.1,
  "gigacode.frequencyPenalty": 0.1,
  "gigacode.contextWindow": 4096,
  "gigacode.systemPrompt": "Ты — опытный AI-ассистент...",
  "gigacode.logLevel": "info",
  "gigacode.debugMode": false
}
```

---

## 🐛 Диагностика

### Просмотр логов
```
View → Output → GigaCode
```

### Проверка состояния
```powershell
.\scripts\setup-gigacode.ps1
```

### Перезапуск расширения
```
Ctrl+Shift+P → GigaCode: Restart
```

### Отладка
```json
"gigacode.debugMode": true,
"gigacode.logLevel": "debug"
```

---

## 🎯 Лучшие практики

### Для режима Agent:
1. **Давайте чёткие задачи:** Вместо "исправь код" → "исправь баг в функции X, где Y не обрабатывает null"
2. **Предоставляйте контекст:** Выделите relevant code перед запросом
3. **Используйте итерации:** Разбивайте сложные задачи на подзадачи
4. **Проверяйте результаты:** Всегда ревьюьте сгенерированный код

### Для режима Ask:
1. **Будьте конкретны:** Вместо "что это?" → "что делает эта декорация?"
2. **Используйте выделение:** Выделите код, о котором спрашиваете
3. **Задавайте контекст:** Укажите язык, фреймворк, версию
4. **Просите примеры:** "покажи пример использования"

### Для автодополнения:
1. **Начинайте писать:** AI подхватит паттерн
2. **Используйте подсказки:** Ctrl+Enter для альтернатив
3. **Принимайте релевантные:** Tab для подходящих предложений
4. **Отклоняйте нерелевантные:** Esc для пропуска

---

## 🔧 Troubleshooting

### Проблема: Агент постоянно отключается
**Решение:**
1. Увеличьте `timeout`: `"gigacode.timeout": 60000`
2. Увеличьте `maxTokens`: `"gigacode.maxTokens": 8192`
3. Перезапустите расширение: `GigaCode: Restart`
4. Проверьте логи на ошибки сети

### Проблема: Ask даёт неполные ответы
**Решение:**
1. Установите `askMode`: `"gigacode.askMode": "detailed"`
2. Увеличьте `maxTokens`: `"gigacode.maxTokens": 4096`
3. Уменьшите `temperature`: `"gigacode.temperature": 0.5`
4. Выделите больше контекста

### Проблема: Медленная работа
**Решение:**
1. Уменьшите `maxTokens`: `"gigacode.maxTokens": 2048`
2. Уменьшите `temperature`: `"gigacode.temperature": 0.3`
3. Отключите лишние функции: `"gigacode.enableSuggestions": false`
4. Проверьте сеть: `ping gigachat.devices.sberbank.ru`

### Проблема: Ошибки подключения
**Решение:**
1. Проверьте `sslVerify`: `"gigacode.sslVerify": false`
2. Проверьте `baseUrl`: `"gigacode.baseUrl": "https://gigachat.devices.sberbank.ru/api/v1"`
3. Проверьте `bearerToken` в настройках
4. Проверьте сеть: `.\\scripts\\setup-gigacode.ps1`

---

## 📞 Поддержка

### Горячие клавиши
| Команда | Горячая клавиша | Описание |
|---------|----------------|----------|
| Agent Mode | `Ctrl+Shift+P` → `GigaCode: Agent` | Режим агента |
| Ask Mode | `Ctrl+Shift+P` → `GigaCode: Ask` | Режим вопросов |
| Inline Chat | `Ctrl+I` | Встроенный чат |
| Restart | `Ctrl+Shift+P` → `GigaCode: Restart` | Перезапуск |
| Show Logs | `Ctrl+Shift+U` → `GigaCode` | Показать логи |

### Полезные команды
```
GigaCode: Chat - Открыть чат
GigaCode: Agent - Режим агента
GigaCode: Ask - Режим вопросов
GigaCode: Explain Code - Объяснить код
GigaCode: Generate Tests - Сгенерировать тесты
GigaCode: Refactor - Рефакторинг
GigaCode: Debug - Отладка
GigaCode: Restart - Перезапуск
```

---

## 📚 Дополнительные ресурсы

- [Официальная документация GigaCode](https://gigachat.dev)
- [Примеры использования](https://github.com/gigacode/examples)
- [Сообщество](https://t.me/gigachat)

---

**Версия:** 1.0.0  
**Последнее обновление:** 2026-05-26
