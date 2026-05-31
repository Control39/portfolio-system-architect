# GigaCode Token Auto-Refresh Setup (без пробелов в имени)
# Автоматическое создание задачи в Планировщике задач Windows

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Настройка автообновления токена GigaCode" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$taskName = "GigaCodeTokenRefresh"
$pythonExe = "C:\repo\.venv\Scripts\python.exe"
$scriptPath = "C:\repo\tools\devtools\.devtools\.gigacode\update_vscode_token.py"

# Проверка существования файлов
if (-not (Test-Path $pythonExe)) {
    Write-Host "❌ Ошибка: Python не найден по пути: $pythonExe" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $scriptPath)) {
    Write-Host "❌ Ошибка: Скрипт не найден по пути: $scriptPath" -ForegroundColor Red
    exit 1
}

# Удаление старой задачи (если есть)
Write-Host "`n🔄 Проверка существующей задачи..." -ForegroundColor Yellow
try {
    $existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
    if ($existingTask) {
        Write-Host "⚠️  Задача '$taskName' уже существует. Удаляю..." -ForegroundColor Yellow
        Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
        Write-Host "✅ Старая задача удалена" -ForegroundColor Green
    }
} catch {
    Write-Host "ℹ️  Задача не найдена (это нормально)" -ForegroundColor Gray
}

# Создание новой задачи
Write-Host "`n📝 Создание новой задачи..." -ForegroundColor Yellow

$action = New-ScheduledTaskAction -Execute $pythonExe -Argument "`"$scriptPath`""
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 25) -RepetitionDuration (New-TimeSpan -Days 365)
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -RunOnlyIfNetworkAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Highest

try {
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description "Автоматическое обновление Access Token для GigaCode VS Code Extension (каждые 25 минут)" -ErrorAction Stop
    
    Write-Host "`n✅ Задача успешно создана!" -ForegroundColor Green
    Write-Host "`n📋 Настройки задачи:" -ForegroundColor Cyan
    Write-Host "  Имя: $taskName" -ForegroundColor White
    Write-Host "  Интервал: каждые 25 минут" -ForegroundColor White
    Write-Host "  Пользователь: $env:USERNAME" -ForegroundColor White
    Write-Host "  Старт: немедленно" -ForegroundColor White
    
    Write-Host "`n💡 Управление задачей:" -ForegroundColor Cyan
    Write-Host "  Просмотр: taskschd.msc" -ForegroundColor White
    Write-Host "  Запустить вручную: schtasks /Run /TN $taskName" -ForegroundColor White
    Write-Host "  Остановить: schtasks /End /TN $taskName" -ForegroundColor White
    Write-Host "  Удалить: schtasks /Delete /TN $taskName /F" -ForegroundColor White
    
    Write-Host "`n✅ Готово! Токен будет обновляться автоматически." -ForegroundColor Green
    
} catch {
    Write-Host "`n❌ Ошибка при создании задачи: $_" -ForegroundColor Red
    Write-Host "`n💡 Попробуйте запустить PowerShell от имени администратора" -ForegroundColor Yellow
    exit 1
}
