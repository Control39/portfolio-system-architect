# GigaCode Helper Module
# Автоматическое управление токенами и настройками

$ExportedFunctions = @(
    'Get-GigaChatToken',
    'Get-CachedToken',
    'Update-GigaCodeToken',
    'Start-GigaCodeAutoUpdate',
    'Stop-GigaCodeAutoUpdate',
    'Test-GigaCodeConnection',
    'Get-GigaCodeStatus'
)

function Get-GigaChatToken {
    """
    Получает новый Access Token от GigaChat
    """
    $ClientId = "54b03e66-d6b4-4945-aae4-e071d1439347"
    $ClientSecret = "ce27d5bc-193c-4f26-a28f-ff0ba390f3a8"
    $AuthHeader = "NTRiMDNlNjYtZDZiNC00OTQ1LWFhZTQtZTA3MWQxNDM5MzQ3OmNlMjdkNWJjLTE5M2MtNGYyNi1hMjhmLWZmMGJhMzkwZjNhOA=="
    
    try {
        $headers = @{
            "Authorization" = "Basic $AuthHeader"
            "Content-Type" = "application/x-www-form-urlencoded"
        }
        
        $body = "scope=GIGACHAT_API_PERS&grant_type=client_credentials"
        
        $response = Invoke-RestMethod -Uri "https://ngw.devices.sberbank.ru:9443/api/v2/oauth" `
            -Method POST `
            -Headers $headers `
            -Body $body `
            -TimeoutSec 30 `
            -ErrorAction Stop
        
        return $response.access_token
    }
    catch {
        Write-Error "Ошибка получения токена: $_"
        return $null
    }
}

function Get-CachedToken {
    """
    Получает кэшированный токен или обновляет его
    """
    $TokenCacheFile = ".gigacode_token_cache.json"
    
    if (Test-Path $TokenCacheFile) {
        try {
            $cache = Get-Content $TokenCacheFile | ConvertFrom-Json
            
            $expiresAt = [DateTime]::Parse($cache.expires_at)
            $now = Get-Date
            
            if ($now -lt $expiresAt) {
                return $cache.token
            }
        }
        catch {}
    }
    
    $token = Get-GigaChatToken
    
    if ($token) {
        $cache = @{
            token = $token
            expires_at = (Get-Date).AddHours(1).ToString("o")
            created_at = (Get-Date).ToString("o")
        }
        
        $cache | ConvertTo-Json | Set-Content -Path $TokenCacheFile -NoNewline
    }
    
    return $token
}

function Update-GigaCodeToken {
    """
    Обновляет токен в настройках VS Code
    """
    $settingsFile = ".vscode/settings.json"
    
    if (-not (Test-Path $settingsFile)) {
        Write-Error "Файл $settingsFile не найден"
        return $false
    }
    
    $token = Get-CachedToken
    
    if (-not $token) {
        Write-Error "Не удалось получить токен"
        return $false
    }
    
    $settingsContent = Get-Content $settingsFile -Raw
    
    if ($settingsContent -match '"gigacode\.bearerToken"\s*:\s*"[^"]*"') {
        $newSettings = $settingsContent -replace '"gigacode\.bearerToken"\s*:\s*"[^"]*"', "`"gigacode.bearerToken`": `"$token`""
    }
    else {
        $newSettings = $settingsContent.TrimEnd("}") + ",`n  `"gigacode.bearerToken`": `"$token`"`n}"
    }
    
    Set-Content -Path $settingsFile -Value $newSettings -NoNewline
    
    return $true
}

function Start-GigaCodeAutoUpdate {
    """
    Запускает фоновую задачу для автоматического обновления токена
    """
    $taskName = "GigaCodeTokenAutoUpdate"
    
    if (Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue) {
        Write-Host "✅ Планировщик уже активен" -ForegroundColor Green
        return $true
    }
    
    $scriptPath = Join-Path $PSScriptRoot "auto-update-gigacode-token.ps1"
    
    $action = New-ScheduledTaskAction -Execute "PowerShell.exe" `
        -Argument "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$scriptPath`""
    
    $trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 30)
    
    $settings = New-ScheduledTaskSettingsSet -Hidden -StartWhenAvailable -RunOnlyIfNetworkAvailable
    
    $principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Least
    
    try {
        Register-ScheduledTask -TaskName $taskName `
            -Action $action `
            -Trigger $trigger `
            -Settings $settings `
            -Principal $principal `
            -ErrorAction Stop
        
        Write-Host "✅ Планировщик настроен: обновление каждые 30 минут" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Error "Не удалось создать планировщик: $_"
        return $false
    }
}

function Stop-GigaCodeAutoUpdate {
    """
    Останавливает автоматическое обновление токена
    """
    $taskName = "GigaCodeTokenAutoUpdate"
    
    if (Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue) {
        Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
        Write-Host "✅ Планировщик отключён" -ForegroundColor Green
        return $true
    }
    
    Write-Host "ℹ️  Планировщик не активен" -ForegroundColor Yellow
    return $true
}

function Test-GigaCodeConnection {
    """
    Проверяет подключение к GigaChat
    """
    $token = Get-CachedToken
    
    if (-not $token) {
        Write-Host "❌ Не удалось получить токен" -ForegroundColor Red
        return $false
    }
    
    $headers = @{
        "Authorization" = "Bearer $token"
        "Content-Type" = "application/json"
    }
    
    try {
        $response = Invoke-RestMethod -Uri "https://gigachat.devices.sberbank.ru/api/v1/health" `
            -Method GET `
            -Headers $headers `
            -TimeoutSec 10 `
            -ErrorAction Stop
        
        Write-Host "✅ GigaChat доступен" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "❌ GigaChat недоступен: $_" -ForegroundColor Red
        return $false
    }
}

function Get-GigaCodeStatus {
    """
    Показывает статус GigaCode
    """
    Write-Host "📊 Статус GigaCode" -ForegroundColor Cyan
    Write-Host "==================" -ForegroundColor Cyan
    
    $settingsFile = ".vscode/settings.json"
    $taskName = "GigaCodeTokenAutoUpdate"
    
    # Проверка настроек
    if (Test-Path $settingsFile) {
        $settings = Get-Content $settingsFile -Raw
        if ($settings -match '"gigacode\.bearerToken"') {
            Write-Host "✅ Настройки GigaCode: найдены" -ForegroundColor Green
        }
        else {
            Write-Host "⚠️  Настройки GigaCode: отсутствуют" -ForegroundColor Yellow
        }
    }
    else {
        Write-Host "⚠️  Файл настроек не найден" -ForegroundColor Yellow
    }
    
    # Проверка планировщика
    if (Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue) {
        Write-Host "✅ Автообновление токена: активно" -ForegroundColor Green
    }
    else {
        Write-Host "⚠️  Автообновление токена: не настроено" -ForegroundColor Yellow
    }
    
    # Проверка подключения
    Test-GigaCodeConnection | Out-Null
}

# Автоматическая инициализация при импорте модуля
if ($env:GIGACODE_AUTO_INIT -eq "true") {
    Write-Host "🔄 Автоматическая инициализация GigaCode..." -ForegroundColor Cyan
    Update-GigaCodeToken
    Start-GigaCodeAutoUpdate
    Write-Host "✅ GigaCode готов к работе!" -ForegroundColor Green
}
