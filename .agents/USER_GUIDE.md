# Руководство по Cognitive Automation Agent

## 📋 Содержание

1. [Быстрый старт](#быстрый-старт)
2. [Режимы работы](#режимы-работы)
3. [Управление автозапуском](#управление-автозапуском)
4. [Мониторинг и управление](#мониторинг-и-управление)
5. [Оптимизация производительности](#оптимизация-производительности)
6. [Troubleshooting](#troubleshooting)

---

## 🚀 Быстрый старт

### Первый запуск

```powershell
# Из корня проекта
python -m agents.cognitive_agent --mode=full --verbose
```

### Проверка готовности

```powershell
# Проверка конфигурации
python .agents/launch_script.py --verify

# Проверка зависимостей
python .agents/launch_script.py --check-deps
```

---

## 🎯 Режимы работы

### Полный режим (full)

**Что делает:**
- Полное сканирование проекта
- Анализ архитектуры и зависимостей
- Генерация плана задач
- Автоматическое выполнение (в рамках доверенных паттернов)
- Создание отчётов

```powershell
python -m agents.cognitive_agent --mode=full
```

### Сканирование (scan)

**Что делает:**
- Определение технологического стека
- Поиск уязвимостей
- Анализ структуры проекта
- Генерация документации

```powershell
python -m agents.cognitive_agent --mode=scan
```

### Оптимизация (optimize)

**Что делает:**
- Обновление зависимостей
- Оптимизация конфигураций
- Удаление мусора
- Настройка производительности

```powershell
python -m agents.cognitive_agent --mode=optimize
```

### Исправление ошибок (fix)

```powershell
# Исправить конкретную проблему
python -m agents.cognitive_agent --mode=fix --issue="Ошибка импорта в module.py"

# Автоматический поиск и исправление ошибок
python -m agents.cognitive_agent --mode=fix --auto-detect
```

### Архитектурный анализ (architecture)

```powershell
python -m agents.cognitive_agent --mode=architecture --generate-diagrams
```

---

## ⚙️ Управление автозапуском

### Отключено по умолчанию

Автозапуск при открытии проекта **отключён** для экономии ресурсов.

### Включение автозапуска

1. Откройте `.agents/config/triggers.yaml`

2. Измените настройку:

```yaml
triggers:
  project_open:
    enabled: true  # Включить автозапуск
```

3. Перезагрузите VS Code

### Отключение автозапуска

```yaml
triggers:
  project_open:
    enabled: false  # Отключить (рекомендуется)
```

---

## 📊 Мониторинг и управление

### Просмотр логов

```powershell
# Последние 50 строк
Get-Content .agents/logs/agent.log -Tail 50

# Следить в реальном времени
Get-Content .agents/logs/agent.log -Wait

# Поиск по ошибке
Select-String -Path .agents/logs/*.log -Pattern "ERROR"
```

### Проверка процессов

```powershell
# Все процессы VS Code
Get-Process | Where-Object {$_.ProcessName -eq 'Code'} | 
    Select-Object Id, CPU, WorkingSet | 
    Sort-Object CPU -Descending

# Процессы агента
Get-Process | Where-Object {$_.ProcessName -like '*agent*' -or $_.ProcessName -like '*node*'}
```

### Остановка агента

```powershell
# Через VS Code: Закройте все окна проекта

# Принудительная остановка
Get-Process | Where-Object {$_.ProcessName -eq 'Code'} | Stop-Process

# Остановить конкретный процесс по ID
Stop-Process -Id <PID>
```

### Лимиты ресурсов

Настройка в `.agents/config/agent-config.yaml`:

```yaml
performance:
  resource_limits:
    max_memory_mb: 1024    # Максимум памяти (МБ)
    max_cpu_percent: 50    # Максимум CPU (%)
    max_disk_mb: 100       # Максимум диска (МБ/сек)
```

---

## 🚀 Оптимизация производительности

### Если ноутбук шумит

**Проблема:** Высокая нагрузка на CPU/память

**Решения:**

1. **Отключить автозапуск** (см. выше)

2. **Ограничить параллелизм:**

```yaml
# agent-config.yaml
task_planner:
  parallel_execution:
    enabled: true
    max_parallel_tasks: 2  # Уменьшить с 5 до 2
```

3. **Отключить глубокое сканирование:**

```yaml
scanning:
  levels:
    deep:
      enabled: false
```

4. **Использовать быстрый режим:**

```powershell
python -m agents.cognitive_agent --mode=scan --quick
```

### Рекомендации по ресурсам

| Сценарий | max_parallel_tasks | max_memory_mb | max_cpu_percent |
|----------|-------------------|---------------|-----------------|
| Ноутбук (8GB RAM) | 2 | 512 | 30 |
| Ноутбук (16GB RAM) | 3 | 1024 | 50 |
| Desktop (32GB+ RAM) | 5 | 2048 | 70 |

---

## 🔧 Troubleshooting

### Проблема: Агент не запускается

**Решение:**
```powershell
# Проверка Python
python --version  # Должна быть 3.8+

# Установка зависимостей
pip install -r .agents/requirements.txt

# Проверка конфигурации
python .agents/launch_script.py --verify
```

### Проблема: Высокая нагрузка на CPU

**Решение:**
1. Отключить автозапуск
2. Уменьшить `max_parallel_tasks`
3. Запустить с `--mode=scan --quick`
4. Проверить логи на ошибки

### Проблема: Не хватает памяти

**Решение:**
```yaml
# agent-config.yaml
performance:
  resource_limits:
    max_memory_mb: 512  # Уменьшить
```

### Проблема: Агент не завершает работу

**Решение:**
```powershell
# Принудительная остановка
Get-Process | Where-Object {$_.ProcessName -eq 'Code'} | Stop-Process -Force
```

---

## 📝 Чек-лист перед запуском

- [ ] Проверить конфигурацию (`.agents/config/agent-config.yaml`)
- [ ] Убедиться, что все зависимости установлены
- [ ] Проверить наличие свободного места на диске
- [ ] Закрыть ненужные приложения для экономии ресурсов
- [ ] При необходимости отключить автозапуск

---

## 🎓 Дополнительные ресурсы

- [Основная документация](README.md)
- [Конфигурация агента](config/agent-config.yaml)
- [Конфигурация триггеров](config/triggers.yaml)
- [Скиллы агента](skills/)
- [Журнал изменений](changelogs/)

---

*Документация обновлена: 2024*
*Версия агента: 2.0*
