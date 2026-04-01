# Руководство по настройке MCP сервера и Continue

## Что такое MCP сервер

MCP (Model Context Protocol) сервер — это сервер, который предоставляет инструменты и ресурсы для ИИ-ассистентов через стандартизированный протокол. Ваш MCP сервер даёт доступ к специфическим инструментам проекта, позволяя ассистентам понимать контекст, работать с компонентами системы и предоставлять более релевантную помощь.

## Установленные инструменты MCP

Сервер [`tools/mcp_server.py`](tools/mcp_server.py) предоставляет 12 инструментов:

1. `get_project_context` — общий контекст проекта
2. `read_ai_context` — чтение `.ai-context.md`
3. `list_it_compass_domains` — список доменов IT-Compass
4. `get_professional_journey` — профессиональный путь автора
5. `list_project_files` — список файлов в проекте
6. `check_project_health` — проверка здоровья проекта
7. `read_project_file` — чтение любого файла проекта
8. `get_system_thinking_markers` — маркеры системного мышления
9. `get_rag_status` — статус RAG системы
10. `search_in_project` — поиск текста в файлах
11. `get_service_status` — статус сервисов проекта
12. `analyze_project_structure` — анализ структуры проекта

## Установка Continue как дополнительного клиента

### Шаг 1: Установите расширение Continue в VS Code

1. Откройте VS Code
2. Перейдите в раздел Extensions (Ctrl+Shift+X)
3. Найдите "Continue"
4. Установите расширение от "Continue.dev"

### Шаг 2: Настройка Continue

Расширение Continue автоматически использует конфигурацию из [`.continue/agents/new-config.yaml`](.continue/agents/new-config.yaml), которая уже содержит настройки для вашего MCP сервера.

### Шаг 3: Проверка установки

1. Перезапустите VS Code
2. Откройте панель Continue (Ctrl+Shift+P → "Continue: Open Continue")
3. Введите запрос, например: "Получи контекст проекта"
4. Continue должен использовать инструменты MCP для ответа

## Альтернативные клиенты MCP

Если вы предпочитаете другие клиенты, поддерживающие MCP:

### Claude Desktop
Добавьте в `%APPDATA%\Claude\claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "portfolio-mcp": {
      "command": "python",
      "args": ["tools/mcp_server.py"]
    }
  }
}
```

### Cursor
Создайте файл `.cursor/mcp.json`:
```json
{
  "mcpServers": {
    "portfolio-mcp": {
      "command": "python",
      "args": ["tools/mcp_server.py"]
    }
  }
}
```

## Проверка работоспособности MCP сервера

### Тест 1: Проверка установки зависимостей
```bash
python -c "import mcp; print('MCP установлен')"
```

### Тест 2: Запуск сервера вручную
```bash
python tools/mcp_server.py
```
Сервер должен вывести "Запуск MCP сервера для портфолио..." и остаться работать.

### Тест 3: Быстрая проверка инструментов
```bash
python -c "
import asyncio
from mcp import Client
import sys

async def test():
    async with Client('python', ['tools/mcp_server.py']) as client:
        tools = await client.list_tools()
        print(f'Доступно инструментов: {len(tools.tools)}')
        for tool in tools.tools[:3]:
            print(f'- {tool.name}: {tool.description}')

asyncio.run(test())
"
```

## Использование с SourceCraft

Вы можете продолжать использовать SourceCraft для общих задач, а Continue — для задач, требующих доступа к инструментам проекта:

- **SourceCraft**: Общие вопросы, управление репозиториями, архитектурные решения
- **Continue с MCP**: Специфические вопросы о проекте, работа с IT-Compass, проверка статуса RAG системы

## Устранение неполадок

### Проблема: Continue не видит инструменты MCP
**Решение:**
1. Убедитесь, что Python установлен и доступен в PATH
2. Проверьте установку библиотеки MCP: `pip list | findstr mcp`
3. Перезапустите VS Code

### Проблема: Ошибка импорта в MCP сервере
**Решение:**
```bash
pip install pydantic fastapi
```

### Проблема: Сервер не запускается
**Решение:**
Проверьте права доступа к файлам:
```bash
python tools/mcp_server.py 2>&1
```

## Дополнительные возможности

### Добавление новых инструментов
Чтобы добавить новые инструменты в MCP сервер, отредактируйте файл [`tools/mcp_server.py`](tools/mcp_server.py) и добавьте новые функции с декоратором `@self.server.tool()`.

### Интеграция с другими сервисами
MCP сервер можно расширить для интеграции с:
- Yandex Cloud Toolkit (уже есть в настройках)
- Базами данных проекта
- Внешними API
- Системами мониторинга

## Контакты и поддержка

- MCP сервер создан для проекта portfolio-system-architect
- Автор: Ekaterina Kudelya
- Обновления: через Git репозиторий

---

*Это руководство создано автоматически при настройке MCP сервера. Последнее обновление: 2026-03-31*
