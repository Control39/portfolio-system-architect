# Скрипт установки pre-commit хуков
# Использование: .\scripts\install-pre-commit.ps1

Write-Host "
═══════════════════════════════════════════════════════════════
         🔧 УСТАНОВКА PRE-COMMIT ХУКОВ
═══════════════════════════════════════════════════════════════
" -ForegroundColor Cyan

# Проверка Python
Write-Host "1. Проверка Python..." -ForegroundColor Yellow
if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "  ❌ .venv не найдено! Создайте виртуальное окружение." -ForegroundColor Red
    exit 1
}
Write-Host "  ✅ Python найден" -ForegroundColor Green
$PYTHON = ".venv\Scripts\python.exe"

# Установка pre-commit
Write-Host "2. Установка pre-commit..." -ForegroundColor Yellow
& $PYTHON -m pip install pre-commit
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✅ pre-commit установлен" -ForegroundColor Green
} else {
    Write-Host "  ❌ Ошибка установки pre-commit" -ForegroundColor Red
    exit 1
}

# Установка хуков
Write-Host "3. Установка git hooks..." -ForegroundColor Yellow
& $PYTHON -m pre-commit install
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✅ Git hooks установлены" -ForegroundColor Green
} else {
    Write-Host "  ❌ Ошибка установки git hooks" -ForegroundColor Red
    exit 1
}

# Установка хуков для commit-msg
Write-Host "4. Установка commit-msg hooks..." -ForegroundColor Yellow
& $PYTHON -m pre-commit install --hook-type commit-msg
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✅ Commit-msg hooks установлены" -ForegroundColor Green
} else {
    Write-Host "  ⚠️ Предупреждение: commit-msg hooks не установлены" -ForegroundColor Yellow
}

Write-Host "
═══════════════════════════════════════════════════════════════
         ✅ ГОТОВО!
═══════════════════════════════════════════════════════════════

Теперь pre-commit будет автоматически проверять код при каждом коммите.

Для ручной проверки всех файлов:
  pre-commit run --all-files

Для пропуска проверки (не рекомендуется):
  git commit --no-verify
" -ForegroundColor Green
