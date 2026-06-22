# fix_profile.ps1 - Восстановление профиля PowerShell

$profilePath = "C:\Users\Z\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1"

# Создаем директорию, если не существует
$dir = Split-Path $profilePath
if (!(Test-Path $dir)) {
    New-Item -Path $dir -ItemType Directory -Force | Out-Null
}

# Корректное содержимое профиля
$content = @'
# PowerShell Profile - Автоматическая активация виртуального окружения

$venvPath = 'C:\repo\.venv\Scripts\Activate.ps1'
if (Test-Path $venvPath) {
    & $venvPath
    Write-Host '✓ Виртуальное окружение активировано' -ForegroundColor Green
}

$venvLocal = '.venv\Scripts\Activate.ps1'
if ((Test-Path $venvLocal) -and (-not (Test-Path function:\deactivate))) {
    & $venvLocal
    Write-Host '✓ Виртуальное окружение активировано' -ForegroundColor Green
}
'@

Set-Content -Path $profilePath -Value $content -Encoding UTF8

Write-Host "✓ Профиль восстановлен: $profilePath" -ForegroundColor Green
Write-Host "Теперь можно запустить: powershell -NoProfile -Command 'Get-Process'"
