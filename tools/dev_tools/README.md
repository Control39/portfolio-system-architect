# AI Proxy Server

Унифицированный API-прокси для переключения между AI-провайдерами (GigaChat ↔ Codette/Ollama).

## 🎯 Назначение

Сервер предоставляет единый интерфейс к разным AI-провайдерам, совместимый с OpenAI API форматом.

**Основные возможности:**
- 🔄 **Переключение провайдеров** — GigaChat (Sber) или Codette (Ollama)
- 📡 **Единый API** — формат `/v1/chat/completions` (OpenAI-compatible)
- 🔐 **Безопасность** — OAuth 2.0 для GigaChat, ключи из `.env`
- ⚙️ **Конфигурация** — JSON-файл с настройками моделей

## 🏗️ Архитектура

```
┌─────────────────────┐
│   Client Request    │
│  (OpenAI format)    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   server.py         │
│  (FastAPI Proxy)    │
└──────────┬──────────┘
           │
    ┌──────┴──────┐
    │ active_provider
    └──────┬──────┘
           │
    ┌──────┴──────┐
    │             │
    ▼             ▼
┌─────────┐ ┌──────────┐
│GigaChat │ │ Codette  │
│(Sber)   │ │ (Ollama) │
└─────────┘ └──────────┘
```

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
cd tools/dev-tools
pip install fastapi uvicorn requests python-dotenv pydantic
```

### 2. Настройка конфигурации

Создайте файл `.gigacode/config.json`:

```json
{
  "active_provider": "codette",
  "codette": {
    "model": "codette:7b",
    "temperature": 0.7
  },
  "gigachat": {
    "model": "GigaChat-Pro",
    "api_key": "YOUR_GIGACHAT_TOKEN_HERE"  # pragma: allowlist secret
  }
}
```

### 3. Настройка переменных окружения

Создайте `.env` в корне проекта:

```bash
GIGACHAT_API_KEY=your_actual_gigachat_token_here
```

### 4. Запуск сервера

```bash
# Из директории tools/dev-tools
python server.py

# Или через uvicorn
uvicorn server:app --reload --host 0.0.0.0 --port 8081
```

Сервер запустится на `http://127.0.0.1:8081`

## 📡 API Endpoints

### POST `/v1/chat/completions`

Запрос к AI-провайдеру в формате OpenAI.

**Request:**
```json
{
  "messages": [
    {"role": "system", "content": "Ты полезный помощник."},
    {"role": "user", "content": "Привет! Как дела?"}
  ],
  "model": "codette:7b"
}
```

**Response:**
```json
{
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "Привет! Всё отлично, спасибо! Чем могу помочь?"
      }
    }
  ],
  "model": "codette:7b"
}
```

### GET `/health`

Проверка состояния сервера.

**Response:**
```json
{
  "status": "healthy",
  "provider": "codette",
  "uptime": 3600
}
```

## ⚙️ Конфигурация

### `.gigacode/config.json`

| Параметр | Описание | Значение по умолчанию |
|----------|----------|----------------------|
| `active_provider` | Текущий провайдер | `"codette"` |
| `codette.model` | Модель Ollama | `"codette:7b"` |
| `codette.temperature` | Температура генерации | `0.7` |
| `gigachat.model` | Модель GigaChat | `"GigaChat-Pro"` |
| `gigachat.api_key` | API-ключ (или из `.env`) | `"YOUR_GIGACHAT_TOKEN_HERE"` |

### Переменные окружения

| Переменная | Описание | Обязательно |
|------------|----------|-------------|
| `GIGACHAT_API_KEY` | API-ключ GigaChat | Если не указан в config.json |

## 🧪 Тестирование

### Запуск тестов

```bash
cd tools/dev-tools
pytest tests/ -v --cov=. --cov-report=term-missing
```

### Пример теста

```python
def test_codette_provider(test_client):
    response = test_client.post(
        "/v1/chat/completions",
        json={
            "messages": [{"role": "user", "content": "Привет"}]
        }
    )
    assert response.status_code == 200
    assert "choices" in response.json()
```

## 🔄 Переключение провайдеров

### Временное переключение (через код)

```python
import requests

# Переключение на GigaChat
response = requests.post(
    "http://127.0.0.1:8081/v1/chat/completions",
    json={
        "messages": [{"role": "user", "content": "Привет"}],
        "provider": "gigachat"  # Переопределение
    }
)
```

### Постоянное переключение

Изменить `active_provider` в `.gigacode/config.json`:
```json
{
  "active_provider": "gigachat"
}
```

## 🐳 Docker-развёртывание

### Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY tools/dev-tools/requirements.txt .
RUN pip install -r requirements.txt

COPY tools/dev-tools/ .
COPY .gigacode/ .gigacode/

EXPOSE 8081
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8081"]
```

### docker-compose.yml

```yaml
services:
  ai-proxy:
    build:
      context: .
      dockerfile: tools/dev-tools/Dockerfile
    ports:
      - "8081:8081"
    environment:
      - GIGACHAT_API_KEY=${GIGACHAT_API_KEY}
    volumes:
      - .gigacode:/app/.gigacode
```

## 🛠️ Troubleshooting

### Ошибка: "Файл конфигурации не найден"

**Решение:** Создайте `.gigacode/config.json` по шаблону выше.

### Ошибка: "GIGACHAT_API_KEY не задан"

**Решение:** Добавьте в `.env`:
```bash
GIGACHAT_API_KEY=your_token_here
```

### Ошибка: "Ollama не запущен"

**Решение:** Запустите Ollama:
```bash
ollama serve
```

## 📊 Метрики

### Тесты

- **Количество:** ≥10 тестов
- **Покрытие:** ≥70%
- **Прохождение:** 100%

### Производительность

- **Latency (Codette):** ~500ms локально
- **Latency (GigaChat):** ~2s облачно
- **Throughput:** ~10 запросов/сек

## 🤝 Вклад

1. Создайте тест для нового провайдера
2. Добавьте документацию
3. Отправьте PR

## 📝 История изменений

### v0.1.0 (2026-05-16)
- ✨ Первоначальная реализация
- 🔀 Поддержка GigaChat и Codette
- 📡 OpenAI-compatible API
- 🧪 Базовые тесты

---

*Документация создана: 16 мая 2026 г.*
