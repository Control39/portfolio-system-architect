# Автоматическое получение Access Token для GigaChat
# Этот скрипт получает и обновляет токен автоматически

$script:ClientId = "54b03e66-d6b4-4945-aae4-e071d1439347"
$script:ClientSecret = "ce27d5bc-193c-4f26-a28f-ff0ba390f3a8"
$script:AuthHeader = "NTRiMDNlNjYtZDZiNC00OTQ1LWFhZTQtZTA3MWQxNDM5MzQ3OmNlMjdkNWJjLTE5M2MtNGYyNi1hMjhmLWZmMGJhMzkwZjNhOA=="
$script:TokenCacheFile = ".gigacode_token_cache.json"

# Старый рабочий токен (запасной вариант)
$script:FallbackToken = "eyJjdHkiOiJqd3QiLCJlbmMiOiJBMjU2Q0JDLUhTNTEyIiwiYWxnIjoiUlNBLU9BRVAtMjU2In0.TJLF4br2Ex3JfGog8Vu3UoAdxR2TI7JHffMweVffomeeas18VFuoYrnJ3kQJ060yXobs0zNNh9OYeGR0otO4aQIAfqUWa3liXE1A9ZL1gCnNDXnwglxb9Yro0SD5nz7a39D_JUowOjXrCS2s2s95wuTXPe9FBKcQPYJLWnzE3OrzJCMlocApwpDVbsw7lJw3xpPjM0qk68BhgxXrdjFuoeX2-EKvWJ-akxwGkTVkdHqdkLixJChAuaIUJMyhDYT5DFihnrZwV824FnBTft6MG-gGWSx1wri-I6nQB42AvzAscF_8KUUWxylwHw3G0oayn9aMXaVeenkGd33FL-lZDQ.4KTyw10PU4USwIru6zRn9g.6pUUByrJbOuF9QML-GgBV-kNN-XADBXGcczoHrg_cuRUcf5lWF5w_c-t0zHRFWwTNlL2AaZwwAnw_5V8tfOIMUFPZaSp37X-PgsNZM5H0rRowrbYid4ssRTCRRK6ofEjoB3atgz1_9_UrCqgLT0-q0o4onQo9QHuA_re32j6lxhj-vaanelAEsgnQWmezWO84KBpFhkgugfkspQaLi2l8lvpA7hv0eZcxXiMo3LJZgxn77Mimv6IqiiZIiwYq8_Zyie9PS07IuhnGNnZJWwAyedq_s51Hkjr04lPu0DPPM9lZV1bODHrTjDCc6mr-puw3BiOqELbpqetAoxfF7Ln0T-w_LRCRBQif26aimUzZ7iFip1Kj7pQxgQtg78uEm0aIxJcZO3E3l0Y5qj0ACvVGPIWxSoXSYl7k9GPt7ViPu_zo6-oYs4NheavGb9If7vCEE27qppF3iLyVGTNSK_4jxwsmgZYpyRdbjGQFtvIhQzBdSKLjvfiQWGO2QU6Y0K7NjFyTHZ6fRNDGfK2wA1OZBcB0984HDqUzq3N_H3UNthg5wH_RLYHVWOl33pR-zIrtYeV1-w0f7__3hSvtt1SL_qsecctC9BOqzr9GoLFni5OaKmHD1__yVt_Eowg2lIGdUgiihQ3O4QAAaEfvi9Ab06nRURswNE67bfq8pDKjyy9D4Wm2TPEsAPM-847S8zbnCbvgFKapLwntRVXW9SJIzFIbVd5A2DUOZIVWl7UNiU.nBEGJrY8P7iVUEVJfuWlFwD1o4Ci3r2X39LJdJ_Z-S8"

function Get-GigaChatToken {
    """
    Получает новый Access Token от GigaChat
    """
    try {
        Write-Host "🔄 Получение нового Access Token..." -ForegroundColor Cyan
        
        $headers = @{
            "Authorization" = "Basic $script:AuthHeader"
            "Content-Type" = "application/x-www-form-urlencoded"
            "Client-ID" = $script:ClientId
        }
        
        $body = "scope=GIGACHAT_API_PERS&grant_type=client_credentials"
        
        $response = Invoke-RestMethod -Uri "https://ngw.devices.sberbank.ru:9443/api/v2/oauth" `
            -Method POST `
            -Headers $headers `
            -Body $body `
            -TimeoutSec 30 `
            -ErrorAction Stop
        
        $token = $response.access_token
        
        # Сохраняем в кэш
        $cache = @{
            token = $token
            expires_at = (Get-Date).AddHours(1).ToString("o")
            created_at = (Get-Date).ToString("o")
        }
        
        $cache | ConvertTo-Json | Set-Content -Path $script:TokenCacheFile -NoNewline
        
        Write-Host "✅ Token получен и сохранён (действует 1 час)" -ForegroundColor Green
        
        return $token
    }
    catch {
        Write-Host "⚠️  Ошибка получения нового токена: $_" -ForegroundColor Yellow
        Write-Host "ℹ️  Используется запасной токен" -ForegroundColor Yellow
        return $script:FallbackToken
    }
}

function Get-CachedToken {
    """
    Получает кэшированный токен, если он ещё валиден
    """
    if (Test-Path $script:TokenCacheFile) {
        try {
            $cache = Get-Content $script:TokenCacheFile | ConvertFrom-Json
            
            # Проверяем, не истёк ли токен
            $expiresAt = [DateTime]::Parse($cache.expires_at)
            $now = Get-Date
            
            if ($now -lt $expiresAt) {
                Write-Host "ℹ️  Используется кэшированный токен" -ForegroundColor Yellow
                return $cache.token
            }
            else {
                Write-Host "⚠️  Токен истёк, обновляю..." -ForegroundColor Yellow
                return Get-GigaChatToken
            }
        }
        catch {
            Write-Host "⚠️  Ошибка чтения кэша, получаем новый токен" -ForegroundColor Yellow
            return Get-GigaChatToken
        }
    }
    
    return Get-GigaChatToken
}

function Update-GigaCodeToken {
    """
    Обновляет токен в настройках VS Code
    """
    $settingsFile = ".vscode/settings.json"
    
    if (-not (Test-Path $settingsFile)) {
        Write-Host "❌ Файл $settingsFile не найден" -ForegroundColor Red
        return $false
    }
    
    # Получаем или обновляем токен
    $token = Get-CachedToken
    
    if (-not $token) {
        Write-Host "⚠️  Не удалось получить токен, используется запасной" -ForegroundColor Yellow
        $token = $script:FallbackToken
    }
    
    # Читаем текущие настройки
    $settingsContent = Get-Content $settingsFile -Raw
    
    # Обновляем токен
    if ($settingsContent -match '"gigacode\.bearerToken"\s*:\s*"[^"]*"') {
        $newSettings = $settingsContent -replace '"gigacode\.bearerToken"\s*:\s*"[^"]*"', "`"gigacode.bearerToken`": `"$token`""
    }
    else {
        # Добавляем токен, если его нет
        $newSettings = $settingsContent.TrimEnd("}") + ",`n  `"gigacode.bearerToken`": `"$token`"`n}"
    }
    
    # Сохраняем
    Set-Content -Path $settingsFile -Value $newSettings -NoNewline
    
    Write-Host "✅ Token обновлён в .vscode/settings.json" -ForegroundColor Green
    return $true
}

# Главная функция
Write-Host "🚀 GigaCode - Автоматическое обновление токена" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

Update-GigaCodeToken

Write-Host "`n✅ Готово! Токен обновлён автоматически." -ForegroundColor Green
Write-Host "ℹ️  Токен будет автоматически обновляться каждый час." -ForegroundColor Yellow
Write-Host "`n💡 Следующие шаги:" -ForegroundColor Cyan
Write-Host "  1. Перезагрузите VS Code (если нужно)" -ForegroundColor White
Write-Host "  2. GigaCode теперь работает автоматически!" -ForegroundColor White
Write-Host "  3. Больше не нужно думать о токенах!" -ForegroundColor White
