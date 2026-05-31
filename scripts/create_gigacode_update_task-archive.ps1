# Создание задачи для автоматического обновления токена GigaCode
# Запускается каждые 25 минут

$taskName = "GigaCodeTokenUpdate"
$scriptPath = "C:\repo\scripts\update_gigacode_token.py"
$pythonPath = "C:\repo\.venv\Scripts\python.exe"

# Проверка существования задачи
$existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue

if ($existingTask) {
    Write-Host "Задача '$taskName' уже существует. Обновляю..."
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
}

# Создание задачи
$action = New-ScheduledTaskAction -Execute $pythonPath -Argument "`"$scriptPath`""
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 25) -RepetitionDuration (New-TimeSpan -Days 365)
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -RunOnlyIfNetworkAvailable
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType S4U -RunLevel Highest

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal

Write-Host "✅ Задача '$taskName' создана!"
Write-Host "   - Запускается каждые 25 минут"
Write-Host "   - Первый запуск: сразу после создания"
Write-Host "   - Управление: taskschd.msc → GigaCodeTokenUpdate"
