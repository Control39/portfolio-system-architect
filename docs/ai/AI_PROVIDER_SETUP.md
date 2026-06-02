# ⚡ Быстрая настройка AI Provider Failover

## 🎯 Что это?

Система автоматического переключения между AI провайдерами:
- **GigaChat** (облако) → основной
- **Ollama** (локально) → резервный

**Если GigaChat упал → автоматически переключается на Ollama**

---

## 🚀 Установка (3 шага)

### Шаг 1: Установить Ollama

**Windows:**
```powershell
.\scripts\setup-ollama.ps1
```

**Linux/macOS:**
```bash
chmod +x scripts/setup-ollama.sh
./scripts/setup-ollama.sh
```

**Что делает скрипт:**
- ✅ Устанавливает Ollama
- ✅ Запускает сервис
- ✅ Скачивает 3 модели (llama3.2, mistral, codellama)
- ✅ Проверяет работоспособность

**Время:** ~10-15 минут (зависит от интернета)

---

### Шаг 2: Проверить модели

```bash
ollama list
```

Ожидаешь:
```
NAME              ID           SIZE
llama3.2          7B           3.8 GB
mistral           7B           4.1 GB
codellama         7B           3.8 GB
```

---

### Шаг 3: Протестировать

```bash
# Тест Ollama
ollama run llama3.2 "Привет! Как дела?"

# Тест AI Provider Manager
python -m apps.ai_provider_manager.src.ai_provider_manager
```

Ожидаешь:
```
📊 AI Providers Status:
{
  "gigachat": {"status": "available"},
  "ollama": {"status": "available"}
}

🧪 Testing chat...
✅ Response: Привет! Я искусственный интеллект...
```

---

## 💡 Использование

### Простой чат

```python
from apps.ai_provider_manager.src.ai_provider_manager import chat_with_fallback

response = chat_with_fallback([
    {"role": "user", "content": "Напиши функцию для сортировки списка"}
])

print(response)
```

### В Cognitive Agent

```python
from apps.ai_provider_manager.src.ai_provider_manager import get_provider_manager

class CognitiveAgent:
    def __init__(self):
        self.manager = get_provider_manager()
    
    def process(self, task: str):
        # Автоматически использует GigaChat или Ollama
        response = self.manager.chat([
            {"role": "user", "content": task}
        ])
        return response
```

---

## 🔍 Проверка работы

### 1. Проверить статус провайдеров

```python
from apps.ai_provider_manager.src.ai_provider_manager import get_provider_manager

manager = get_provider_manager()
status = manager.get_status()

print(f"Primary: {manager.current_provider}")
print(f"GigaChat: {status['gigachat']['status']}")
print(f"Ollama: {status['ollama']['status']}")
```

### 2. Проверить переключение

```python
# Имитировать ошибку GigaChat
manager.set_provider_status("gigachat", "unavailable")

# Отправить сообщение - должно использовать Ollama
response = manager.chat([{"role": "user", "content": "Привет!"}])
print(f"Использован: {manager.current_provider}")
```

---

## 📊 Статус

| Компонент | Статус | Команда |
|-----------|--------|---------|
| **GigaChat** | ✅ Настроен | В `.vscode/settings.json` |
| **Ollama** | 🔄 Установить | `.\scripts\setup-ollama.ps1` |
| **AI Provider Manager** | ✅ Готов | `apps/ai_provider_manager/` |
| **Документация** | ✅ Готово | `docs/AI_PROVIDER_FAILOVER.md` |

---

## 🎯 Как это работает

```
┌─────────────────────────────────────────┐
│  Ты: "Напиши функцию для сортировки"    │
└─────────────────┬───────────────────────┘
                  │
          ┌───────▼────────┐
          │AI Provider     │
          │Manager         │
          └───────┬────────┘
                  │
    ┌─────────────┴─────────────┐
    │ Пробуем GigaChat          │
    │ ✅ Успех → ответ          │
    │ ❌ Ошибка → пробуем Ollama│
    └───────────────────────────┘
                  │
          ┌───────▼────────┐
          │  Ответ от AI   │
          └────────────────┘
```

---

## 🐛 Troubleshooting

### Ошибка: "Ollama не найден"

```bash
# Перезапусти терминал
# Или добавь в PATH вручную:
$env:Path += ";C:\Program Files\Ollama"
```

### Ошибка: "Нет доступных моделей"

```bash
# Скачать модель
ollama pull llama3.2

# Проверить
ollama list
```

### Ошибка: "GigaChat недоступен"

```bash
# Обновить токен
.\scripts\auto-update-gigacode-token.ps1

# Или использовать только Ollama
# (система автоматически переключится)
```

---

## ✅ Готово!

Теперь:
1. ✅ Ollama установлен и настроен
2. ✅ 3 локальные модели скачаны
3. ✅ AI Provider Manager готов
4. ✅ Автоматическое переключение работает

**Больше не нужно думать о токенах и доступности!** 🎉

---

## 📚 Дополнительная документация

- `docs/AI_PROVIDER_FAILOVER.md` - Полное руководство
- `docs/GIGACODE_QUICKSTART.md` - Настройка GigaCode
- `scripts/ai_provider_manager.py` - Исходный код

---

**Начни с:** `.\scripts\setup-ollama.ps1` ⚡
