# setup_profile.ps1 - Настройка автоматической активации виртуального окружения

$profilePath = "C:\Users\Z\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1"

# Создаем профиль, если не существует
$dir = Split-Path $profilePath
if (!(Test-Path $dir)) {
    New-Item -Path $dir -ItemType Directory -Force | Out-Null
}

if (!(Test-Path $profilePath)) {
    New-Item -Path $profilePath -ItemType File -Force | Out-Null
    Write-Host "✓ Профиль создан: $profilePath" -ForegroundColor Green
}

# Формируем содержимое профиля
$content = @"
# PowerShell Profile - Автоматическая активация виртуального окружения

# Активация венв в репозитории C:\repo (если существует)
$venvPath = 'C:\repo\.venv\Scripts\Activate.ps1'
if (Test-Path $venvPath) {
    & $venvPath
    Write-Host '✓ Виртуальное окружение активировано' -ForegroundColor Green
}

# Активация венв в любом репозитории (если .venv найден в текущей директории)
$venvLocal = '.venv\Scripts\Activate.ps1'
if ((Test-Path $venvLocal) -and (-not (Test-Path function:\deactivate))) {
    & $venvLocal
    Write-Host '✓ Виртуальное окружение активировано' -ForegroundColor Green
}
"@

# Записываем содержимое
Set-Content -Path $profilePath -Value $content -Encoding UTF8

Write-Host "✓ Профиль обновлён успешно!" -ForegroundColor Green
Write-Host ""
Write-Host "Следующие шаги:" -ForegroundColor Cyan
Write-Host "1. Закройте и откройте новый терминал PowerShell"
Write-Host "2. Виртуальное окружение активируется автоматически"
Write-Host "3. Проверьте: (Get-Command python).Source должна указывать на .venv"
