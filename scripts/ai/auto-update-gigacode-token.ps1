# Автоматическое получение Access Token для GigaChat
# Этот скрипт получает и обновляет токен автоматически
#
# =============================================================================
# НАСТРОЙКА:
# =============================================================================
# 1. Скопируйте .env.example в .env:
#    Copy-Item .env.example .env
#
# 2. Заполните .env своими данными:
#    GIGACHAT_CLIENT_ID=ваш-client-id
#    GIGACHAT_CLIENT_SECRET=ваш-client-secret
#
# 3. Установите переменные окружения (в PowerShell):
#    $env:GIGACHAT_CLIENT_ID = (Get-Content .env | Select-String "GIGACHAT_CLIENT_ID" | Split-String -Part "=" | Select-Object -Last 1)
#    $env:GIGACHAT_CLIENT_SECRET = (Get-Content .env | Select-String "GIGACHAT_CLIENT_SECRET" | Split-String -Part "=" | Select-Object -Last 1)
#
# 4. Запустите скрипт:
#    .\scripts\ai\auto-update-gigacode-token.ps1
#
# =============================================================================
# ПРИМЕЧАНИЕ:
# - Токен кэшируется в .gigacode_token_cache.json (игнорируется в Git)
# - Токен действует 1 час и обновляется автоматически
# =============================================================================

# ⚠️ ВАЖНО: Установите переменные окружения перед запуском:
# $env:GIGACHAT_CLIENT_ID = "ваш-client-id"
# $env:GIGACHAT_CLIENT_SECRET = "ваш-client-secret"

$script:ClientId = $env:GIGACHAT_CLIENT_ID
$script:ClientSecret = $env:GIGACHAT_CLIENT_SECRET

if ([string]::IsNullOrEmpty($script:ClientId) -or [string]::IsNullOrEmpty($script:ClientSecret)) {
    Write-Error "❌ Ошибка: Не установлены переменные окружения GIGACHAT_CLIENT_ID и GIGACHAT_CLIENT_SECRET"
    Write-Host "ℹ️  Установите их перед запуском:" -ForegroundColor Yellow
    Write-Host "  `$env:GIGACHAT_CLIENT_ID = 'ваш-client-id'" -ForegroundColor Yellow
    Write-Host "  `$env:GIGACHAT_CLIENT_SECRET = 'ваш-client-secret'" -ForegroundColor Yellow
    exit 1
}

# Генерируем AuthHeader из ClientId и ClientSecret
$authString = "$($script:ClientId):$($script:ClientSecret)"
$script:AuthHeader = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes($authString))

$script:TokenCacheFile = ".gigacode_token_cache.json"

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
        Write-Error "❌ Не удалось получить токен. Проверьте ClientId и ClientSecret"
        exit 1
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
        Write-Error "❌ Не удалось получить токен"
        exit 1
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
