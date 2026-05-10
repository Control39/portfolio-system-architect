# Чеклист: Активация и проверка виртуального окружения на Windows

> **Дата создания:** 10 мая 2026 г.  
> **Для проекта:** Portfolio System Architect

---

## 📌 Быстрый старт

### 1. Активация виртуального окружения

| Оболочка | Команда |
|----------|---------|
| **PowerShell** | `.\.venv\Scripts\Activate.ps1` |
| **PowerShell (с обходом политики)** | `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`<br>`.\.venv\Scripts\Activate.ps1` |
| **CMD** | `.venv\Scripts\activate.bat` |
| **Git Bash** | `source .venv/Scripts/activate` |
| **WSL** | `source .venv/bin/activate` |

**Ожидаемый результат:** Промпт начинается с `(.venv)`

---

### 2. Деактивация

| Оболочка | Команда |
|----------|---------|
| **Все** | `deactivate` |

**Ожидаемый результат:** `(.venv)` исчезает из промпта

---

## 🔍 Чеклист проверки (последовательно)

### Шаг 1: Проверка пути к Python

```bash
python --version
where python
```

**✅ Успех:**
```
Python 3.10.x
C:\Projects\portfolio-system-architect\.venv\Scripts\python.exe
```

**❌ Неудача:**
```
Python 3.10.x
C:\Python310\python.exe  # ← СИСТЕМНЫЙ, НЕ .venv
```

---

### Шаг 2: Проверка префикса окружения

```bash
python -c "import sys; print(sys.prefix)"
```

**✅ Успех:**
```
C:\Projects\portfolio-system-architect\.venv
```

**❌ Неудача:**
```
C:\Python310  # ← СИСТЕМНЫЙ PYTHON
```

---

### Шаг 3: Проверка установленных пакетов

```bash
pip list
```

**✅ Успех:** Видны пакеты проекта:
```
fastapi          0.136.1
pydantic         2.5.0
langchain        0.3.0
pytest           8.0.0
uvicorn          0.27.0
```

**❌ Неудача:** Пусто или только `pip`, `setuptools`

---

### Шаг 4: Проверка места установки пакетов

```bash
pip show fastapi
```

**✅ Успех:**
```
Location: C:\Projects\portfolio-system-architect\.venv\Lib\site-packages
```

**❌ Неудача:**
```
Location: C:\Python310\Lib\site-packages  # ← СИСТЕМНЫЙ
```

---

### Шаг 5: Тестовый импорт ключевых модулей

```bash
python -c "import fastapi; import pydantic; import langchain; print('✅ Все ключевые пакеты доступны')"
```

**✅ Успех:**
```
✅ Все ключевые пакеты доступны
```

**❌ Неудача:**
```
ModuleNotFoundError: No module named 'fastapi'
```

---

### Шаг 6: Проверка файлов виртуального окружения

```bash
dir .venv\Scripts\python.exe
dir .venv\Lib\site-packages\
```

**✅ Успех:**
- `python.exe` существует
- `site-packages` содержит пакеты (fastapi, pydantic и др.)

**❌ Неудача:**
- Файлы отсутствуют или папка пуста

---

## 🚨 Частые проблемы и решения

### Проблема 1: PowerShell запрещает выполнение скриптов

**Ошибка:**
```
Access to the path is denied.
Script 'Activate.ps1' cannot be run because...
```

**Решение:**
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

---

### Проблема 2: VS Code не использует виртуальное окружение

**Симптом:** В терминале VS Code промпт не показывает `(.venv)`

**Решение:**
1. `Ctrl+Shift+P` → `Python: Select Interpreter`
2. Выбрать `Python 3.10.x ('.venv': venv)`

---

### Проблема 3: Пакеты не устанавливаются в .venv

**Симптом:** `pip install` пишет о правах доступа

**Решение:**
```bash
# Убедитесь, что окружение активно
.\.venv\Scripts\Activate.ps1

# Затем установите
pip install -r requirements.txt
```

---

### Проблема 4: Git Bash не активирует окружение

**Симптом:** `source .venv/Scripts/activate` не работает

**Решение:**
```bash
# Используйте Windows-версию
.venv/Scripts/activate
# Или PowerShell
powershell -ExecutionPolicy Bypass -File .venv/Scripts/Activate.ps1
```

---

## 📋 Полный скрипт проверки (копируй и вставляй)

```powershell
# === ЧЕКЛИСТ ПРОВЕРКИ ВЕНВА ===

Write-Host "=== Шаг 1: Активация ===" -ForegroundColor Cyan
.\.venv\Scripts\Activate.ps1

Write-Host "`n=== Шаг 2: Версия Python ===" -ForegroundColor Cyan
python --version

Write-Host "`n=== Шаг 3: Путь к Python ===" -ForegroundColor Cyan
where python

Write-Host "`n=== Шаг 4: Префикс окружения ===" -ForegroundColor Cyan
python -c "import sys; print(sys.prefix)"

Write-Host "`n=== Шаг 5: Список пакетов ===" -ForegroundColor Cyan
pip list | Select-String "fastapi|pydantic|langchain|pytest"

Write-Host "`n=== Шаг 6: Тестовый импорт ===" -ForegroundColor Cyan
python -c "import fastapi; import pydantic; import langchain; print('✅ OK')"

Write-Host "`n=== Чеклист завершён ===" -ForegroundColor Green
```

---

## 🎯 Критерии успеха

| Критерий | Прошёл | Не прошёл |
|----------|--------|-----------|
| Промпт показывает `(.venv)` | ✅ | ❌ |
| `sys.prefix` = `.venv` | ✅ | ❌ |
| `pip list` показывает пакеты | ✅ | ❌ |
| Импорт работает без ошибок | ✅ | ❌ |

**Если все 4 критерия ✅** → Окружение рабочее, можно работать!

**Если есть ❌** → См. раздел "Частые проблемы и решения"

---

## 📞 Следующие шаги после активации

1. **Установка зависимостей:**
   ```bash
   pip install -r requirements-dev.txt
   ```

2. **Запуск линтинга:**
   ```bash
   make lint
   ```

3. **Запуск тестов:**
   ```bash
   make test
   ```

4. **Запуск среды разработки:**
   ```bash
   make dev
   ```

---

*Файл создан 10 мая 2026 г. для упрощения работы с виртуальным окружением на Windows.*