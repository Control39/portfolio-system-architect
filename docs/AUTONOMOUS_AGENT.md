# 🤖 Autonomous Cognitive Agent

## 🎯 Обзор

**Автономный когнитивный агент** — AI-ассистент, который:
- ✅ Запускается автоматически при открытии проекта в VS Code
- ✅ Работает в фоновом режиме
- ✅ Сканирует код и архитектуру каждые 5 минут
- ✅ Анализирует проблемы и предлагает улучшения
- ✅ Использует GigaChat или Ollama (автоматическое переключение)

## 🏗️ Архитектура

```
VS Code Project Opened
        ↓
[Auto-start Agent]
        ↓
[Background Loop]
    ├─ Scan Project (every 5 min)
    ├─ Detect Issues
    ├─ Generate Recommendations
    └─ Save Results
        ↓
[AI Provider Manager]
    ├─ Primary: GigaChat
    └─ Fallback: Ollama
```

## 🚀 Установка

### 1. Установить зависимости

```bash
# Убедись, что Ollama установлена
.\scripts\setup-ollama.ps1

# Установи Python зависимости
pip install -r requirements.txt
```

### 2. Настроить автозапуск

**Вариант A: Автоматически при открытии проекта**

VS Code автоматически запустит агент при открытии папки проекта (задача `Cognitive Agent: Auto-start on open`).

**Вариант B: Вручную через Tasks**

```
Ctrl+Shift+P → Tasks: Run Task → Cognitive Agent: Start
```

**Вариант C: Через терминал**

```bash
# Запуск в фоне
python -m apps.cognitive_agent.autonomous_agent --start

# Запуск в foreground (для отладки)
python -m apps.cognitive_agent.autonomous_agent --start --foreground
```

## 💡 Использование

### Через VS Code Tasks

| Команда | Описание |
|---------|----------|
| `Cognitive Agent: Start` | Запустить агента |
| `Cognitive Agent: Stop` | Остановить агента |
| `Cognitive Agent: Status` | Показать статус |
| `Cognitive Agent: Scan` | Запустить сканирование |

**Как выполнить:**
```
Ctrl+Shift+P → Tasks: Run Task → [выбрать команду]
```

### Через CLI

```bash
# Запуск
python -m apps.cognitive_agent.autonomous_agent --start

# Остановка
python -m apps.cognitive_agent.autonomous_agent --stop

# Статус
python -m apps.cognitive_agent.autonomous_agent --status

# Сканирование
python -m apps.cognitive_agent.autonomous_agent --scan
```

### Через код

```python
from apps.cognitive_agent.autonomous_agent import (
    get_agent,
    start_agent,
    stop_agent
)

# Запуск
agent = start_agent()

# Получить статус
status = agent.get_status()
print(status)

# Запустить сканирование
results = agent.scan_project()
print(f"Найдено проблем: {len(results['issues'])}")

# Остановить
stop_agent()
```

## 📊 Что делает агент

### 1. Сканирование проекта

**Анализирует:**
- Количество файлов и директорий
- Языки программирования
- Используемые фреймворки
- Потенциальные проблемы

**Пример вывода:**
```
🔍 Scanning project: C:\repo
✅ Scan completed in 2.34s
   Files: 1234
   Languages: 5
   Issues: 12
   Recommendations: 8
```

### 2. Обнаружение проблем

**Типы проблем:**
- Большие файлы (>1MB)
- TODO комментарии
- Устаревшие зависимости
- Неоптимальный код
- Отсутствие тестов

**Пример:**
```json
{
  "type": "large_file",
  "path": "apps/legacy/old_module.py",
  "message": "Файл слишком большой: 2.3 MB"
}
```

### 3. Генерация рекомендаций

**Использует AI для:**
- Анализа архитектуры
- Предложений по улучшению
- Рекомендаций по рефакторингу
- Планов оптимизации

**Пример:**
```json
{
  "priority": "high",
  "category": "code_quality",
  "message": "Раздели большой модуль на подмодули"
}
```

## 🔍 Результаты

### Где хранить результаты

```
cognitive_agent/
├── scans/
│   ├── scan_20260527_120000.json
│   ├── scan_20260527_120500.json
│   └── last_scan.json
└── logs/
    └── cognitive_agent.log
```

### Формат результатов

```json
{
  "timestamp": "2026-05-27T12:00:00",
  "agent_id": "agent-20260527-120000",
  "project_path": "C:\\repo",
  "files": 1234,
  "directories": 156,
  "languages": {
    "Python": 800,
    "JSON": 200,
    "YAML": 100
  },
  "frameworks": ["Docker", "Pytest", "FastAPI"],
  "issues": [...],
  "recommendations": [...]
}
```

## 🎯 Команды агента

### Выполнение задач

```python
# Выполнить задачу
result = agent.execute_task("Добавь логирование во все модули")

# С автоподтверждением
result = agent.execute_task("Добавь логирование", auto_approve=True)
```

**AI сгенерирует план:**
```json
{
  "status": "success",
  "task": "Добавь логирование во все модули",
  "plan": {
    "steps": [
      "Анализ текущей структуры",
      "Добавление импортов logging",
      "Внедрение loggers в модули",
      "Тестирование"
    ],
    "estimated_time": "2 часа",
    "risk_level": "low"
  }
}
```

## 📈 Мониторинг

### Статус агента

```python
from apps.cognitive_agent.autonomous_agent import get_agent

agent = get_agent()
status = agent.get_status()

print(f"Agent: {status['agent_id']}")
print(f"Running: {status['running']}")
print(f"AI Provider: {status['ai_provider']}")
print(f"Last Scan: {status['last_scan']}")
print(f"Total Scans: {status['total_scans']}")
```

### Логи

```bash
# Просмотр логов
tail -f logs/cognitive_agent.log

# Или в VS Code:
# View → Output → Select "Python" или "Tasks"
```

## 🐛 Troubleshooting

### Проблема: Агент не запускается автоматически

**Решение:**
1. Проверь, что `.vscode/tasks.json` существует
2. Убедись, что задача `Cognitive Agent: Auto-start on open` есть
3. Перезагрузи VS Code

### Проблема: Ошибки при сканировании

**Решение:**
```bash
# Проверь логи
cat logs/cognitive_agent.log

# Запусти в foreground для отладки
python -m apps.cognitive_agent.autonomous_agent --start --foreground
```

### Проблема: AI недоступен

**Решение:**
```bash
# Проверь GigaChat
.\scripts\auto-update-gigacode-token.ps1

# Проверь Ollama
ollama list

# Перезапусти агента
python -m apps.cognitive_agent.autonomous_agent --stop
python -m apps.cognitive_agent.autonomous_agent --start
```

### Проблема: Много ложных срабатываний

**Решение:**
```python
# Настрой исключения в агенте
agent = get_agent()
agent._excluded_patterns = [
    "*.pyc",
    "node_modules/*",
    ".venv/*"
]
```

## ⚙️ Настройки

### Интервал сканирования

```python
agent = get_agent()
agent.scan_interval = 600  # 10 минут вместо 5
```

### Автоподтверждение задач

```python
# Включить автоподтверждение
agent = get_agent()
# Все задачи будут выполняться без подтверждения
```

### Логирование

```python
import logging

logging.getLogger("apps.cognitive_agent").setLevel(logging.DEBUG)
```

## 🎯 Best Practices

### 1. Держи агент запущенным

Агент работает в фоне и не мешает работе. Рекомендуется держать его запущенным для постоянного мониторинга.

### 2. Регулярно проверяй результаты

```bash
# Еженедельный отчёт
python -m apps.cognitive_agent.autonomous_agent --status
```

### 3. Используй рекомендации

AI генерирует практические рекомендации. Реализуй их постепенно.

### 4. Настрой исключения

Исключи ненужные директории для ускорения сканирования:

```python
agent._excluded_patterns.extend([
    "build/*",
    "dist/*",
    "*.min.js"
])
```

## 📚 Дополнительные ресурсы

- `apps/cognitive_agent/autonomous_agent.py` - Исходный код
- `docs/AI_PROVIDER_FAILOVER.md` - AI Provider Manager
- `docs/GIGACODE_QUICKSTART.md` - Настройка GigaCode
- `.vscode/tasks.json` - Задачи VS Code

---

**Версия:** 1.0.0  
**Дата:** 2026-05-27  
**Статус:** ✅ Автономный агент готов
