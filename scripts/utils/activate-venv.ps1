# Автоматическая активация виртуального окружения для проекта Portfolio System Architect
# Используйте: .\activate-venv.ps1

$venvPath = Join-Path $PSScriptRoot ".venv"
$activateScript = Join-Path $venvPath "Scripts\Activate.ps1"

if (Test-Path $activateScript) {
    & $activateScript
    Write-Host "✓ Виртуальное окружение активировано: $venvPath" -ForegroundColor Green
} else {
    Write-Host "✗ Файл активации не найден: $activateScript" -ForegroundColor Red
    Write-Host "Создайте виртуальное окружение: python -m venv .venv" -ForegroundColor Yellow
}
