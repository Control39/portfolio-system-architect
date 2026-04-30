# Интеграция MCP-сервера с Claude Desktop

## Что такое Claude Desktop?

Claude Desktop - это настольное приложение от Anthropic, которое позволяет использовать Claude AI локально на вашем компьютере. Ключевая особенность - поддержка **MCP (Model Context Protocol)**, который позволяет подключать внешние серверы с данными и инструментами.

## Как работает MCP (Model Context Protocol)?

MCP - это протокол, который позволяет ИИ-моделям (как Claude) взаимодействовать с внешними системами через стандартизированный интерфейс:

```
Claude Desktop <--MCP--> MCP Server <---> Ваши данные и инструменты
```

### Компоненты:
1. **MCP Server** (наш сервер) - предоставляет инструменты и ресурсы
2. **MCP Client** (Claude Desktop) - использует инструменты через Claude
3. **Протокол** - стандартизированное общение между сервером и клиентом

## Конфигурация Claude Desktop для нашего MCP-сервера

### 1. Файл конфигурации Claude Desktop
Расположение зависит от ОС:
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

### 2. Пример конфигурации
```json
{
  "mcpServers": {
    "career-autopilot": {
      "command": "python",
      "args": [
        "C:/Users/Z/DeveloperEnvironment/projects/portfolio-system-architect/apps/mcp-server/src/main.py"
      ],
      "env": {
        "MCP_ENV": "development",
        "PYTHONPATH": "C:/Users/Z/DeveloperEnvironment/projects/portfolio-system-architect"
      }
    }
  },
  "models": [
    {
      "model": "claude-3-opus-20240229",
      "provider": "anthropic"
    },
    {
      "model": "claude-3-sonnet-20240229",
      "provider": "anthropic"
    }
  ]
}
```

### 3. Альтернативная конфигурация (с виртуальным окружением)
```json
{
  "mcpServers": {
    "career-autopilot": {
      "command": "C:/Users/Z/DeveloperEnvironment/projects/portfolio-system-architect/.venv/Scripts/python.exe",
      "args": [
        "C:/Users/Z/DeveloperEnvironment/projects/portfolio-system-architect/apps/mcp-server/src/main.py"
      ]
    }
  }
}
```

## Какие агенты и модели используются?

### 1. В Claude Desktop:
- **Основная модель**: Claude 3 (Opus или Sonnet) от Anthropic
- **Провайдер**: Anthropic API (требуется API ключ)
- **Альтернативы**: Можно настроить локальные модели через Ollama

### 2. В нашем MCP-сервере:
- **FastMCP**: Фреймворк для создания MCP-серверов на Python
- **Инструменты**: Наши кастомные инструменты для работы с файлами, Git, IT-Compass
- **Модели AI для анализа**: Конфигурируются в `mcp-config.yaml`:
  - GPT-4 (OpenAI)
  - Claude 3 (Anthropic)
  - Gemini 1.5 (Google)
  - Локальные модели (Ollama)

## Как это работает на практике?

### Пример диалога:
```
Вы: "Проанализируй мои последние коммиты на наличие маркеров IT-Compass"

Claude Desktop → MCP Server: Вызывает инструмент scan_last_commits_for_markers_tool()

MCP Server → Git: Анализирует последние 10 коммитов
MCP Server → IT-Compass: Сравнивает с маркерами компетенций
MCP Server → Claude Desktop: Возвращает обнаруженные маркеры

Claude Desktop → Вам: "В ваших последних коммитах обнаружены маркеры:
- Системное мышление: спроектировал методологию с обратной связью
- Python: создал микросервисную архитектуру на FastAPI
- DevOps: настроил полный CI/CD пайплайн"
```

## Преимущества этой архитектуры

### 1. Безопасность
- MCP-сервер работает локально
- Данные не уходят в облако (кроме запросов к Claude API)
- Контроль над тем, какие инструменты доступны

### 2. Мощность Claude + специализированные инструменты
- Используете интеллект Claude 3
- + Наши специализированные инструменты для карьерного роста
- + Доступ к вашему портфолио и IT-Compass

### 3. Автономность
- Работает даже без интернета (кроме запросов к Claude API)
- Все ваши данные локально
- Можно использовать локальные модели через Ollama

## Настройка шаг за шагом

### Шаг 1: Установка зависимостей
```bash
cd apps/mcp-server
pip install -r requirements.txt
```

### Шаг 2: Тестирование MCP-сервера
```bash
python src/main.py
# Сервер должен запуститься на localhost:8000
```

### Шаг 3: Настройка Claude Desktop
1. Откройте Claude Desktop
2. Перейдите в Settings → Developer
3. Добавьте конфигурацию MCP сервера
4. Перезапустите Claude Desktop

### Шаг 4: Проверка
1. Откройте Claude Desktop
2. Спросите: "Какие инструменты доступны через Career Autopilot?"
3. Claude должен перечислить доступные инструменты

## Устранение неполадок

### Проблема 1: "Server not found"
**Решение:** Проверьте путь к Python и скрипту в конфигурации

### Проблема 2: "Permission denied"
**Решение:** Дайте права на выполнение скрипту
```bash
chmod +x apps/mcp-server/src/main.py
```

### Проблема 3: "Import error"
**Решение:** Установите зависимости
```bash
pip install fastmcp python-dotenv
```

### Проблема 4: "Connection refused"
**Решение:** Проверьте, что сервер запущен
```bash
# В отдельном терминале
python apps/mcp-server/src/main.py
```

## Альтернативы Claude Desktop

### 1. Continue.dev (VS Code расширение)
- Также поддерживает MCP
- Интеграция прямо в VS Code
- Меньше переключений между приложениями

### 2. Cursor
- Поддерживает собственный протокол, похожий на MCP
- Хорошая интеграция с кодом

### 3. Прямое использование через API
- Можно вызывать MCP-сервер через Python скрипты
- Больше контроля, но меньше удобства

## Безопасность и конфиденциальность

### Что остается локально:
- Весь ваш код и коммиты
- IT-Compass маркеры и методология
- Конфигурации MCP-сервера
- Результаты анализа

### Что уходит в Anthropic:
- Только текст запросов и ответов MCP-сервера
- API ключи для моделей (если используете облачные)

### Рекомендации:
1. Используйте локальные модели (Ollama) для конфиденциальных данных
2. Настройте .gitignore для исключения конфиденциальных конфигураций
3. Регулярно обновляйте зависимости для безопасности

## Дальнейшее развитие

### Планируемые улучшения:
1. **Веб-интерфейс**: Доступ через браузер, а не только Claude Desktop
2. **Мобильное приложение**: Доступ с телефона
3. **Интеграция с LinkedIn**: Автоматический анализ вакансий
4. **Оффлайн-режим**: Полная работа без интернета

### Roadmap:
- **Q2 2026**: Стабильная интеграция с Claude Desktop
- **Q3 2026**: Веб-интерфейс и мобильное приложение
- **Q4 2026**: Интеграция с job boards и LinkedIn

## Заключение

Интеграция MCP-сервера с Claude Desktop создает мощную синергию:
- **Интеллект Claude** для понимания контекста и генерации текста
- **Наши инструменты** для специализированного анализа карьеры
- **Ваши данные** для персонализированных рекомендаций

Это превращает Claude из общего ИИ-ассистента в персонального карьерного консультанта, который понимает вашу уникальную роль "Cognitive Systems Architect & AI Orchestrator" и помогает продвигать её на рынке труда.
