# Настройка PowerShell для автоматической активации виртуального окружения

## Проблема

PowerShell по умолчанию блокирует выполнение скриптов из соображений безопасности. Это мешает автоматической активации виртуального окружения.

## Решение

### Вариант 1: Автоматическая активация при запуске PowerShell (рекомендуется)

Добавьте следующую строку в ваш профиль PowerShell:

```powershell
# Откройте профиль для редактирования
notepad $PROFILE

# Добавьте в конец файла:
$projectPath = "C:\repo"
if (Test-Path "$projectPath\.venv\Scripts\Activate.ps1") {
    & "$projectPath\.venv\Scripts\Activate.ps1"
    Write-Host "✓ Виртуальное окружение проекта активно" -ForegroundColor Green
}
```

**Важно:** Перед этим нужно разрешить выполнение скриптов (одноразово):

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

### Вариант 2: Использовать alias в профиле

Добавьте в профиль alias для быстрого активации:

```powershell
# Alias для активации венв
function Activate-Venv {
    & "C:\repo\.venv\Scripts\Activate.ps1"
    Write-Host "✓ Виртуальное окружение активировано" -ForegroundColor Green
}

# Или alias с именем (venv)
Set-Alias venv Activate-Venv
```

Используйте: `Activate-Venv` или `venv`

### Вариант 3: Использовать созданный скрипт

В корне проекта создан `activate-venv.ps1`:

```powershell
# Разрешить выполнение скриптов (одноразово)
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned

# Запуск скрипта активации
.\activate-venv.ps1
```

### Вариант 4: Обход политики выполнения (без изменения настроек)

Используйте bat-файл вместо ps1:

```cmd
.venv\Scripts\activate.bat
```

Или создайте `activate.bat` в корне проекта:

```batch
@echo off
call .venv\Scripts\activate.bat
echo Виртуальное окружение активировано
```

## Проверка

После активации проверьте:

```powershell
python --version
where python
```

Путь должен указывать на `C:\repo\.venv\Scripts\python.exe`

## Устранение проблем

### Ошибка: "authorization_failed"

PowerShell запрещает выполнение скриптов. Решение:

```powershell
# Разрешить скрипты только для текущего пользователя
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

### Ошибка: "Activate.ps1 не найден"

Создайте виртуальное окружение:

```powershell
python -m venv .venv
```

## Примечание

Если вы используете Windows Terminal, можно настроить автоматическое активирование для каждой новой вкладки:

```json
// В settings.json Windows Terminal:
{
    "commandline": "powershell -NoExit -Command \"cd C:\\repo; .\\activate-venv.ps1\"",
    "name": "PS with Venv"
}
```
