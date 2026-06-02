# 🚀 Быстрая настройка GigaCode

## ✅ Что сделано

1. **Созданы конфигурационные файлы:**
   - `.vscode/settings.json` - основные настройки
   - `.koda/config.json` - продвинутые настройки

2. **Созданы скрипты:**
   - `scripts/setup-gigacode.ps1` - диагностика
   - `scripts/update-gigacode-token.ps1` - обновление токена

3. **Создана документация:**
   - `docs/GIGACODE_GUIDE.md` - полное руководство
   - `docs/GIGACODE_TOKEN_SETUP.md` - получение токена

---

## 🔧 Что нужно сделать

### Шаг 1: Получите новый Bearer Token

**Вариант А: Через веб-интерфейс (рекомендуется)**
1. Откройте https://gigachat.dev/
2. Авторизуйтесь через Sber ID
3. Перейдите в раздел "API Keys" или "Токены"
4. Создайте новый токен
5. Скопируйте токен

**Вариант Б: Через скрипт**
```powershell
.\scripts\update-gigacode-token.ps1
```

### Шаг 2: Обновите токен в настройках

```powershell
# Запустите скрипт обновления
.\scripts\update-gigacode-token.ps1

# Или вручную:
# 1. Откройте .vscode/settings.json
# 2. Найдите строку "gigacode.bearerToken"
# 3. Замените значение на новый токен
```

### Шаг 3: Перезагрузите VS Code

```
1. Закройте VS Code полностью
2. Откройте VS Code заново
3. Или: Ctrl+Shift+P → "Developer: Reload Window"
```

### Шаг 4: Перезапустите расширение GigaCode

```
Ctrl+Shift+P → "GigaCode: Restart"
```

### Шаг 5: Проверьте работу

**Проверка режима Agent:**
```
Напишите в чате: @agent проверь мои настройки
```

**Проверка режима Ask:**
```
Напишите в чате: ? Как работает AI Config Manager?
```

---

## 🎯 Режимы работы

### Режим Agent (для сложных задач)
```
@agent <ваш запрос>
```

**Примеры:**
- `@agent проанализируй архитектуру проекта`
- `@agent исправь баг в функции X`
- `@agent создай тесты для модуля Y`

### Режим Ask (для вопросов)
```
? <ваш вопрос>
```

**Примеры:**
- `? Что делает эта функция?`
- `? Как работает контекстный менеджер?`
- `? Объясни паттерн проектирования`

---

## ⚙️ Основные настройки

### .vscode/settings.json
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

### .koda/config.json
```json
{
  "gigacode.agentMode": "auto",
  "gigacode.askMode": "smart",
  "gigacode.contextWindow": 4096,
  "gigacode.logLevel": "info"
}
```

---

## 🐛 Troubleshooting

### Проблема: Режим агента ломается
**Решение:**
1. Увеличьте timeout: `"gigacode.timeout": 60000`
2. Увеличьте maxTokens: `"gigacode.maxTokens": 8192`
3. Перезапустите расширение: `GigaCode: Restart`

### Проблема: Режим Ask даёт плохие ответы
**Решение:**
1. Установите: `"gigacode.askMode": "detailed"`
2. Выделите больше контекста кода
3. Установите: `"gigacode.temperature": 0.5`

### Проблема: 403 Forbidden
**Решение:**
1. Получите новый токен
2. Обновите токен через: `.\scripts\update-gigacode-token.ps1`
3. Перезагрузите VS Code

### Проблема: Медленная работа
**Решение:**
1. Уменьшите maxTokens: `"gigacode.maxTokens": 2048`
2. Уменьшите temperature: `"gigacode.temperature": 0.3`
3. Отключите лишние функции

---

## 📞 Полезные команды

| Команда | Описание |
|---------|----------|
| `Ctrl+Shift+P` → `GigaCode: Chat` | Открыть чат |
| `Ctrl+Shift+P` → `GigaCode: Agent` | Режим агента |
| `Ctrl+Shift+P` → `GigaCode: Ask` | Режим вопросов |
| `Ctrl+Shift+P` → `GigaCode: Restart` | Перезапуск |
| `Ctrl+I` | Inline чат |
| `Ctrl+Shift+U` → `GigaCode` | Логи |

---

## 📚 Дополнительная документация

- `docs/GIGACODE_GUIDE.md` - Полное руководство
- `docs/GIGACODE_TOKEN_SETUP.md` - Получение токена
- `scripts/setup-gigacode.ps1` - Диагностика

---

## ✅ Проверка

Запустите диагностику:
```powershell
.\scripts\setup-gigacode.ps1
```

Ожидаемый результат:
```
✅ GigaCode установлен
✅ Настройки GigaCode найдены
✅ Bearer Token найден
✅ .koda/config.json найден
```

---

**Готово! Теперь GigaCode настроен и готов к работе!** 🎉
