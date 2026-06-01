# GigaCode Диагностика и Настройка
# PowerShell скрипт для проверки и восстановления работы GigaCode

Write-Host "🔍 Проверка GigaCode..." -ForegroundColor Cyan

# 1. Проверка установки расширения
Write-Host "`n📦 Проверка установленных расширений..." -ForegroundColor Yellow
$extensions = code --list-extensions
if ($extensions -match "gigacode") {
    Write-Host "✅ GigaCode установлен" -ForegroundColor Green
} else {
    Write-Host "❌ GigaCode не найден. Устанавливаю..." -ForegroundColor Red
    code --install-extension gigacode.gigacode-vscode
}

# 2. Проверка настроек
Write-Host "`n⚙️  Проверка настроек..." -ForegroundColor Yellow
if (Test-Path ".vscode/settings.json") {
    $settings = Get-Content ".vscode/settings.json" -Raw
    if ($settings -match "gigacode.enable") {
        Write-Host "✅ Настройки GigaCode найдены" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Настройки GigaCode отсутствуют" -ForegroundColor Yellow
    }

    if ($settings -match "gigacode.bearerToken") {
        Write-Host "✅ Bearer Token найден" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Bearer Token отсутствует" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ .vscode/settings.json не найден" -ForegroundColor Red
}

# 3. Проверка .koda/config.json
Write-Host "`n📁 Проверка .koda/config.json..." -ForegroundColor Yellow
if (Test-Path ".koda/config.json") {
    Write-Host "✅ .koda/config.json найден" -ForegroundColor Green
    $kodaConfig = Get-Content ".koda/config.json" -Raw | ConvertFrom-Json
    Write-Host "  - Model: $($kodaConfig.model)" -ForegroundColor Gray
    Write-Host "  - Max Tokens: $($kodaConfig.maxTokens)" -ForegroundColor Gray
    Write-Host "  - Agent Mode: $($kodaConfig.agentMode)" -ForegroundColor Gray
    Write-Host "  - Ask Mode: $($kodaConfig.askMode)" -ForegroundColor Gray
} else {
    Write-Host "❌ .koda/config.json не найден" -ForegroundColor Red
}

# 4. Проверка сети
Write-Host "`n🌐 Проверка подключения к GigaChat..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "https://gigachat.devices.sberbank.ru/api/v1/health" -Method GET -TimeoutSec 10 -ErrorAction Stop
    Write-Host "✅ GigaChat доступен (Status: $($response.StatusCode))" -ForegroundColor Green
} catch {
    Write-Host "⚠️  GigaChat недоступен: $_" -ForegroundColor Yellow
}

# 5. Предложения по оптимизации
Write-Host "`n💡 Рекомендации:" -ForegroundColor Cyan
Write-Host "  1. Перезагрузите VS Code для применения настроек" -ForegroundColor White
Write-Host "  2. Используйте Ctrl+Shift+P > 'GigaCode: Restart' для перезапуска расширения" -ForegroundColor White
Write-Host "  3. Проверьте логи: Output > GigaCode" -ForegroundColor White
Write-Host "  4. Для режима агента: используйте '@agent' в запросах" -ForegroundColor White
Write-Host "  5. Для режима ask: используйте '?' в начале запроса" -ForegroundColor White

Write-Host "`n✅ Готово!" -ForegroundColor Green
Write-Host "`nСледующие шаги:" -ForegroundColor Cyan
Write-Host "  1. Перезагрузите VS Code" -ForegroundColor White
Write-Host "  2. Откройте палету команд (Ctrl+Shift+P)" -ForegroundColor White
Write-Host "  3. Выберите 'GigaCode: Chat' или 'GigaCode: Agent'" -ForegroundColor White
