# AI Provider Failover - Резервирование провайдеров

## 🎯 Обзор

Система автоматического переключения между AI провайдерами для обеспечения отказоустойчивости:

- **Primary (основной):** GigaChat (облако)
- **Fallback (резервный):** Ollama (локальные модели)

## 🏗️ Архитектура

```
┌─────────────────────────────────────┐
│     Cognitive Agent                 │
└─────────────────┬───────────────────┘
                  │
          ┌───────▼────────┐
          │AI Provider     │
          │Manager         │
          └───────┬────────┘
                  │
    ┌─────────────┴─────────────┐
    │                           │
┌───▼────┐              ┌──────▼──────┐
│GigaChat│              │   Ollama    │
│(Cloud) │              │ (Local)     │
└────────┘              └─────────────┘
```

## 🔄 Стратегия переключения

1. **По умолчанию:** GigaChat (приоритет 1)
2. **При ошибке GigaChat:** Автоматически переключается на Ollama
3. **При успехе Ollama:** Помечает GigaChat как "temporarily unavailable"
4. **Периодическая проверка:** Пробует восстановить GigaChat каждые 5 минут

## 📦 Установка

### 1. Установить Ollama

**Windows:**
```powershell
.\scripts\setup-ollama.ps1
```

**Linux/macOS:**
```bash
chmod +x scripts/setup-ollama.sh
./scripts/setup-ollama.sh
```

### 2. Скачать локальные модели

```bash
# Рекомендуемые модели:
ollama pull llama3.2    # 7B, быстрый, для общих задач
ollama pull mistral     # 7B, сбалансированный
ollama pull codellama   # 7B, оптимизирован для кода
```

## 💻 Использование

### Через код

```python
from apps.ai_provider_manager.src.ai_provider_manager import (
    AIProviderManager,
    chat_with_fallback,
    get_provider_manager
)

# Вариант 1: Простой чат
response = chat_with_fallback([
    {"role": "user", "content": "Привет! Как дела?"}
])
print(response)

# Вариант 2: С управлением
manager = AIProviderManager()

# Проверить статус провайдеров
status = manager.get_status()
print(status)

# Отправить сообщение
response = manager.chat([
    {"role": "system", "content": "Ты — помощник по программированию"},
    {"role": "user", "content": "Напиши функцию для сортировки"}
])
print(response)

# Переключить провайдера вручную
manager.current_provider = "ollama"
```

### В Cognitive Agent

```python
# В коде агента просто используем:
from apps.ai_provider_manager.src.ai_provider_manager import chat_with_fallback

class CognitiveAgent:
    async def process_task(self, task: str):
        # Автоматически использует GigaChat или Ollama
        response = chat_with_fallback([
            {"role": "user", "content": task}
        ])
        return response
```

## ⚙️ Конфигурация

### Настройки провайдеров

```python
from apps.ai_provider_manager.src.ai_provider_manager import ProviderConfig, ProviderStatus

manager = AIProviderManager()

# Настроить GigaChat
manager.providers["gigachat"].timeout = 60
manager.providers["gigachat"].max_retries = 5

# Настроить Ollama
manager.providers["ollama"].timeout = 120
manager.providers["ollama"].priority = 2

# Проверить статус
print(manager.providers["gigachat"].status)
```

### Изменение приоритетов

```python
# Сделать Ollama основным
manager.providers["ollama"].priority = 1
manager.providers["gigachat"].priority = 2

# Пересобрать fallback chain
manager.fallback_chain = sorted(
    [k for k, v in manager.providers.items() if v.enabled],
    key=lambda x: manager.providers[x].priority
)
```

## 📊 Мониторинг

### Получить статус

```python
manager = get_provider_manager()
status = manager.get_status()

import json
print(json.dumps(status, indent=2, ensure_ascii=False))
```

Пример вывода:
```json
{
  "gigachat": {
    "name": "GigaChat",
    "enabled": true,
    "status": "available",
    "priority": 1,
    "error_count": 0,
    "last_error": null,
    "last_success": 1716912345.678
  },
  "ollama": {
    "name": "Ollama",
    "enabled": true,
    "status": "available",
    "priority": 2,
    "error_count": 0,
    "last_error": null,
    "last_success": 1716912345.678
  }
}
```

### Логирование

```python
import logging

logging.basicConfig(level=logging.INFO)

# INFO: AI Providers initialized: ['gigachat', 'ollama']
# INFO: Trying provider: gigachat
# WARNING: gigachat marked as unavailable: Connection timeout
# INFO: Trying provider: ollama
# INFO: Response from ollama successfully
```

## 🐛 Troubleshooting

### Проблема: Ollama не запускается

**Решение:**
```bash
# Проверить, что порт свободен
netstat -an | grep 11434

# Перезапустить
ollama serve

# Проверить логи
ollama --debug serve
```

### Проблема: Модели не скачиваются

**Решение:**
```bash
# Проверить интернет-соединение
ping ollama.com

# Скачать вручную
ollama pull llama3.2

# Проверить место на диске
df -h  # Linux/macOS
dir C:\  # Windows
```

### Проблема: GigaChat постоянно недоступен

**Решение:**
```python
# Проверить токен
from apps.ai_config_manager.src.config_manager import ConfigManager
config = ConfigManager()
token = config.get_gigachat_token()

if not token:
    print("Token not found!")
    # Обновить токен
    # см. docs/GIGACODE_TOKEN_SETUP.md

# Попробовать вручную
import requests
response = requests.get("https://gigachat.devices.sberbank.ru/api/v1/health")
print(response.status_code)
```

### Проблема: Медленная работа Ollama

**Решение:**
```bash
# Использовать меньшую модель
ollama pull llama3.2:1b  # 1.5B параметров

# Или оптимизировать текущую
ollama pull llama3.2:7b  # 7B параметров (баланс)

# Проверить нагрузку на CPU/GPU
htop  # Linux/macOS
Task Manager  # Windows
```

## 📈 Производительность

### Сравнение провайдеров

| Провайдер | Скорость | Качество | Стоимость | Доступность |
|-----------|----------|----------|-----------|-------------|
| **GigaChat** | ~300 ток/сек | Высокое | Платно | 99.9% |
| **Ollama** | ~50 ток/сек | Среднее | Бесплатно | 100% (локально) |

### Рекомендации

- **GigaChat:** Сложные задачи, высокое качество
- **Ollama:** Быстрые задачи, конфиденциальность, оффлайн

## 🔐 Безопасность

### Локальность данных

С Ollama все данные остаются на вашем компьютере:
- ✅ Нет отправки в облако
- ✅ Нет логирования
- ✅ Полная конфиденциальность

### Настройка брандмауэра

```bash
# Разрешить только локальный доступ
sudo ufw deny from any to any port 11434  # Заблокировать внешний доступ
```

## 🎯 Best Practices

### 1. Держите Ollama запущенным

```bash
# Добавить в автозагрузку (Linux)
systemctl --user enable ollama

# Или как сервис (Windows)
New-Service -Name "Ollama" -Path "C:\Program Files\Ollama\ollama.exe" -ArgumentList "serve"
```

### 2. Регулярно обновляйте модели

```bash
# Обновить все модели
ollama list | awk 'NR>1 {print $1}' | xargs -I {} ollama pull {}
```

### 3. Мониторьте использование ресурсов

```bash
# Проверить использование GPU
ollama ps

# Проверить память
ollama list --format json | jq '.[].size'
```

## 📚 Дополнительные ресурсы

- [Официальная документация Ollama](https://ollama.ai/docs)
- [Список доступных моделей](https://ollama.ai/library)
- [GigaChat API](https://developers.sber.ru/docs/ru/gigachat)

---

**Версия:** 1.0.0  
**Дата:** 2026-05-27  
**Статус:** ✅ Готово к использованию
