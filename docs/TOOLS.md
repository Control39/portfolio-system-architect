# Инструменты разработки — Руководство

> **Версия:** 1.0.0  
> **Дата:** 18 мая 2026 г.  
> **Владелец:** Portfolio System Architect Team

---

## 📋 Обзор

Проект использует 4 основных инструмента ИИ-ассистирования:

| Инструмент | Назначение | Расположение | Статус |
|------------|------------|--------------|--------|
| **Koda** | IDE-интеграция (код-интеллект) | `.koda/` | 🟢 Active |
| **SourceCraft** | AI-агенты для автоматизации | `codeassistant/` | 🟢 Active |
| **Continue** | AI pair programming (VS Code) | `.vscode/` + `continue/` | 🟢 Active |
| **MCP Server** | Multi-Client Protocol | `codeassistant/mcp.json` | 🟢 Active |

---

## 1. Koda

### 🎯 Назначение

Koda — ИИ-ассистент для IDE, обеспечивающий:
- Анализ кода и архитектуры
- Генерацию кода по спецификациям
- Рефакторинг и оптимизацию
- Поиск и исправление багов
- Автономное выполнение задач

### 📁 Структура

```
.koda/
├── plans/              # Планы разработки
├── profiles/           # Профили конфигурации
├── rules/              # Правила поведения
└── skills/             # Навыки (опционально)
```

### ⚙️ Конфигурация

**Файлы конфигурации:**
- `.koda/profiles/default.yaml` — профиль по умолчанию
- `.koda/rules/*.md` — правила для разных сценариев

### 🛠️ Использование

**Триггеры:**
- Автоматический анализ при открытии проекта
- Генерация кода по запросу
- Рефакторинг по команде

**Примеры:**
```
/koda analyze — анализ проекта
/koda refactor <file> — рефакторинг файла
/koda generate <spec> — генерация кода
```

### 🔗 Интеграция

- **VS Code**: Расширение Koda
- **JetBrains**: Плагин Koda
- **CLI**: `koda-cli` утилита

---

## 2. SourceCraft

### 🎯 Назначение

SourceCraft — система управления ИИ-агентами для:
- Автоматического анализа кода
- Проверки качества и безопасности
- Аудита архитектуры
- Генерации отчётов

### 📁 Структура

```
codeassistant/
├── mcp.json            # Главный конфиг Multi-Client Protocol
├── ai-models.yaml      # Настройки моделей (GigaChat, OpenAI, Llama)
├── custom_modes.yaml   # Режимы: разработка, аудит, релиз
├── context.md          # Глобальный контекст агента
├── rules/              # Стандарты кода, безопасности, workflow
├── skills/             # 17 специализированных навыков
│   ├── architect-analize/
│   ├── code-security-auditor/
│   ├── devops-ci-cd/
│   ├── it-compass/
│   ├── career/
│   └── ... (ещё 12 навыков)
├── teacher/            # Гайды, шпаргалки, скрипты
└── tools/              # Вспомогательные утилиты
```

### 🧩 Ключевые навыки (Skills)

| Навык | Описание | Триггер |
|-------|----------|---------|
| **architect-analize** | Анализ архитектуры проекта | При открытии проекта |
| **code-security-auditor** | Поиск уязвимостей, проверка секретов | При коммите / по запросу |
| **devops-ci-cd** | Анализ воркфлоу, оптимизация деплоя | При изменении `.github/` |
| **it-compass** | Применение методологии системного мышления | При проектировании |
| **career** | Анализ прогресса, рекомендации по развитию | По запросу |
| **knowledge** | RAG-поиск по документации | При вопросах |
| **seo** | Анализ SEO-оптимизации | При изменениях в client/ |
| **personal-branding** | Генерация контента для портфолио | По запросу |
| **job-market** | Анализ рынка труда | По запросу |
| **teacher** | Обучение и наставничество | При запросах "как сделать" |

### ⚙️ Конфигурация

**mcp.json** — основной конфиг:
```json
{
  "agents": [
    {
      "name": "codeassistant",
      "model": "gpt-4",
      "skills": ["architect-analize", "code-security-auditor", "it-compass"]
    }
  ]
}
```

**ai-models.yaml** — настройки моделей:
```yaml
models:
  gpt-4:
    provider: "openai"
    temperature: 0.7
    max_tokens: 4096
  giga-chat:
    provider: "gigachat"
    temperature: 0.5
    max_tokens: 2048
```

### 🛠️ Использование

**Запуск агента:**
```bash
# Через MCP
mcp run codeassistant

# Через CLI
sourcecraft-cli run --mode=audit
```

**Примеры запросов:**
```
Проанализируй архитектуру проекта
Найди уязвимости в коде
Проверь CI/CD воркфлоу
Сгенерируй отчёт качества
```

### 🔗 Интеграция

- **VS Code**: Через MCP extension
- **CLI**: `sourcecraft-cli`
- **API**: REST API для интеграции с CI/CD

---

## 3. Continue

### 🎯 Назначение

Continue — AI pair programming для VS Code:
- Автодополнение кода
- Чат с ИИ по контексту проекта
- Рефакторинг
- Генерация тестов
- Объяснение кода

### 📁 Структура

```
.vscode/
├── settings.json       # Настройки VS Code
└── extensions.json     # Рекомендуемые расширения

continue/               # Конфигурация Continue
├── config.json         # Основной конфиг
├── models/             # Настройки моделей
└── rules/              # Правила для ИИ
```

### ⚙️ Конфигурация

**config.json**:
```json
{
  "models": [
    {
      "name": "GPT-4",
      "provider": "openai",
      "apiKey": "${env:OPENAI_API_KEY}"
    }
  ],
  "rules": [
    "Следуй стилю Black + isort",
    "Добавляй type hints",
    "Пиши тесты для новых функций"
  ]
}
```

### 🛠️ Использование

**Команды:**
- `Ctrl+L` — Открыть чат
- `Ctrl+I` — Инлайн-редактирование
- `Ctrl+Shift+P` → "Continue: Generate" — Генерация кода

**Примеры:**
```
/explain — объяснить выделенный код
/refactor — рефакторинг
/test — сгенерировать тесты
/doc — сгенерировать документацию
```

### 🔗 Интеграция

- **VS Code**: Расширение Continue (установить из marketplace)
- **Поддержка моделей**: OpenAI, Anthropic, локальные модели (Ollama)

---

## 4. MCP Server

### 🎯 Назначение

Multi-Client Protocol (MCP) — унифицированный протокол для взаимодействия с ИИ-агентами:
- Единый интерфейс для разных агентов
- Обмен контекстом между инструментами
- Управление сессиями
- Логирование взаимодействий

### 📁 Структура

```
codeassistant/mcp.json  # Конфигурация MCP
```

### ⚙️ Конфигурация

```json
{
  "version": "1.0.0",
  "agents": {
    "codeassistant": {
      "enabled": true,
      "tools": ["file_operations", "git_operations", "compass_integration"]
    }
  },
  "logging": {
    "level": "INFO",
    "path": "logs/mcp.log"
  }
}
```

### 🛠️ Использование

**Запуск:**
```bash
mcp-server --config=codeassistant/mcp.json
```

**CLI команды:**
```
mcp agent codeassistant status
mcp agent codeassistant invoke --task="анализ кода"
mcp log show --last=100
```

---

## 📊 Сравнение инструментов

| Функция | Koda | SourceCraft | Continue | MCP |
|---------|------|-------------|----------|-----|
| **IDE-интеграция** | ✅ | ✅ | ✅ | ❌ |
| **Автономные агенты** | ✅ | ✅ | ❌ | ✅ |
| **Анализ архитектуры** | ✅ | ✅ | ⚠️ | ✅ |
| **Генерация кода** | ✅ | ✅ | ✅ | ✅ |
| **Проверка безопасности** | ⚠️ | ✅ | ❌ | ✅ |
| **RAG-поиск** | ⚠️ | ✅ | ❌ | ✅ |
| **CI/CD интеграция** | ❌ | ✅ | ❌ | ✅ |
| **Локальные модели** | ✅ | ✅ | ✅ | ⚠️ |

---

## 🎯 Когда какой инструмент использовать

### Koda
- **Для**: Быстрого анализа кода, рефакторинга, генерации кода
- **Сценарии**:
  - "Помоги оптимизировать эту функцию"
  - "Создай тесты для этого модуля"
  - "Найди баги в этом файле"

### SourceCraft
- **Для**: Глубокого анализа, аудита, автоматизации
- **Сценарии**:
  - "Проанализируй архитектуру всего проекта"
  - "Сделай security audit"
  - "Сгенерируй отчёт качества кода"
  - "Проверь CI/CD воркфлоу"

### Continue
- **Для**: Pair programming, инлайн-помощи
- **Сценарии**:
  - "Объясни, что делает этот код"
  - "Рефакторинг этой функции"
  - "Дополни этот код"
  - "Сгенерируй документацию"

### MCP Server
- **Для**: Оркестрации агентов, CI/CD, логирования
- **Сценарии**:
  - "Запусти агента codeassistant в режиме audit"
  - "Получи логи взаимодействий"
  - "Интеграция с GitHub Actions"

---

## 🔧 Настройка окружения

### Предварительные требования

```bash
# Python 3.10+
python --version

# Node.js (для MCP)
node --version

# VS Code (для Continue)
code --version
```

### Установка

**Koda:**
```bash
pip install koda-cli
koda-cli install
```

**SourceCraft:**
```bash
# Скопировать конфигурацию в IDE
cp -r codeassistant ~/.codeassistant/

# Установить зависимости
cd codeassistant
pip install -r requirements.txt
```

**Continue:**
```bash
# Установить расширение в VS Code
# Marketplace: "Continue"
# Или CLI:
code --install-extension continue.continue
```

**MCP Server:**
```bash
pip install mcp-server
mcp-server --config=codeassistant/mcp.json
```

### Переменные окружения

`.env`:
```bash
# API ключи
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=...
GIGACHAT_API_KEY=...

# Настройки
KODA_LOG_LEVEL=INFO
MCP_LOG_PATH=logs/mcp.log
```

---

## 📚 Дополнительные ресурсы

### Документация

- [`codeassistant/README.md`](../codeassistant/README.md) — подробное руководство по SourceCraft
- [`codeassistant/context.md`](../codeassistant/context.md) — глобальный контекст агента
- [`codeassistant/ai-models.yaml`](../codeassistant/ai-models.yaml) — настройки моделей
- [Continue docs](https://docs.continue.dev) — официальная документация

### Примеры

- [`codeassistant/skills/`](../codeassistant/skills/) — примеры навыков
- [`codeassistant/teacher/`](../codeassistant/teacher/) — гайды и шпаргалки
- [`codeassistant/tools/`](../codeassistant/tools/) — вспомогательные утилиты

### Инструменты

- [`tools/repo_audit/`](../tools/repo_audit/) — инструмент аудита репозитория
- [`scripts/`](../scripts/) — скрипты автоматизации

---

## 🛠️ Устранение проблем

### Koda не запускается

```bash
# Проверить установку
koda-cli --version

# Переустановить
pip uninstall koda-cli
pip install koda-cli

# Проверить логи
tail -f ~/.koda/logs/koda.log
```

### SourceCraft не видит контекст проекта

```bash
# Проверить конфигурацию
cat codeassistant/mcp.json

# Перезапустить агента
mcp agent codeassistant restart

# Проверить логи
cat logs/mcp.log
```

### Continue не подключается к модели

```bash
# Проверить API ключ
echo $OPENAI_API_KEY

# Проверить конфиг
cat .continue/config.json

# Перезагрузить расширение
# VS Code: Ctrl+Shift+P → "Developer: Reload Window"
```

---

*Последнее обновление: 18 мая 2026 г.*
