# Автоматическое обновление токена GigaCode каждые 30 минут
# Запускается в фоновом режиме

$scriptPath = "$PSScriptRoot\auto-update-gigacode-token.ps1"
$taskName = "GigaCodeTokenAutoUpdate"

Write-Host "🔧 Настройка автоматического обновления токена..." -ForegroundColor Cyan

# Проверяем, запущен ли уже планировщик
$existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue

if ($existingTask) {
    Write-Host "⚠️  Планировщик уже существует. Пересоздаю..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
}

# Создаём задачу планировщика
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" `
    -Argument "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$scriptPath`""

$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 30)

$settings = New-ScheduledTaskSettingsSet -Hidden -StartWhenAvailable -RunOnlyIfNetworkAvailable

$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Least

# Создаём задачу
Register-ScheduledTask -TaskName $taskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Principal $principal `
    -Description "Автоматическое обновление токена GigaCode каждые 30 минут" `
    -ErrorAction Stop

Write-Host "✅ Планировщик задач настроен!" -ForegroundColor Green
Write-Host "  - Задача: $taskName" -ForegroundColor Gray
Write-Host "  - Интервал: каждые 30 минут" -ForegroundColor Gray
Write-Host "  - Запуск: при входе в систему" -ForegroundColor Gray

Write-Host "`n💡 Запустить немедленно?" -ForegroundColor Cyan
$runNow = Read-Host "Нажмите Y для запуска сейчас, Enter для пропуска"

if ($runNow -eq "Y" -or $runNow -eq "y") {
    Start-ScheduledTask -TaskName $taskName
    Write-Host "✅ Задача запущена" -ForegroundColor Green
}

Write-Host "`nℹ️  Управление планировщиком:" -ForegroundColor Yellow
Write-Host "  Запустить: Start-ScheduledTask -TaskName $taskName" -ForegroundColor Gray
Write-Host "  Остановить: Stop-ScheduledTask -TaskName $taskName" -ForegroundColor Gray
Write-Host "  Удалить: Unregister-ScheduledTask -TaskName $taskName" -ForegroundColor Gray
Write-Host "  Статус: Get-ScheduledTask -TaskName $taskName" -ForegroundColor Gray
