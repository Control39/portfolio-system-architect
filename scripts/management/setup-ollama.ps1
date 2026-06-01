# Настройка Ollama для локальных AI моделей (Windows)

Write-Host "🚀 Настройка Ollama для локальных AI моделей" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

# Проверка установки Ollama
try {
    $ollamaVersion = ollama --version 2>&1
    Write-Host "✅ Ollama уже установлен: $ollamaVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Ollama не установлен. Устанавливаю..." -ForegroundColor Yellow

    # Скачивание установщика
    $installerUrl = "https://ollama.com/download/ollama-windows-amd64.zip"
    $installerPath = "$env:TEMP\ollama-windows-amd64.zip"

    Write-Host "  • Скачивание установщика..." -ForegroundColor Gray
    Invoke-WebRequest -Uri $installerUrl -OutFile $installerPath

    Write-Host "  • Распаковка..." -ForegroundColor Gray
    Expand-Archive -Path $installerPath -DestinationPath "$env:ProgramFiles\Ollama" -Force

    Write-Host "  • Добавление в PATH..." -ForegroundColor Gray
    $env:Path += ";$env:ProgramFiles\Ollama"
    [Environment]::SetEnvironmentVariable("Path", $env:Path, [EnvironmentVariableTarget]::User)

    Write-Host "✅ Ollama установлен" -ForegroundColor Green
}

# Запуск Ollama
Write-Host "`n🔄 Запуск Ollama..." -ForegroundColor Cyan
Start-Process ollama -ArgumentList "serve" -WindowStyle Hidden -NoNewline

Start-Sleep -Seconds 5

# Проверка доступности
try {
    $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -TimeoutSec 10
    Write-Host "✅ Ollama запущен" -ForegroundColor Green
} catch {
    Write-Host "❌ Не удалось запустить Ollama" -ForegroundColor Red
    exit 1
}

# Список доступных моделей
Write-Host "`n📦 Проверка доступных моделей..." -ForegroundColor Cyan
ollama list

# Проверка количества моделей
$models = ollama list 2>&1 | Select-String -Pattern "^[a-z]"
$modelsCount = ($models | Measure-Object).Count

if ($modelsCount -lt 2) {
    Write-Host "`n📥 Скачивание локальных моделей..." -ForegroundColor Cyan

    Write-Host "  • llama3.2 (7B, быстрый)" -ForegroundColor Gray
    ollama pull llama3.2

    Write-Host "  • mistral (7B, сбалансированный)" -ForegroundColor Gray
    ollama pull mistral

    Write-Host "  • codellama (7B, для кода)" -ForegroundColor Gray
    ollama pull codellama

    Write-Host "`n✅ Модели скачаны" -ForegroundColor Green
} else {
    Write-Host "`n✅ Модели уже скачаны" -ForegroundColor Green
}

# Проверка
Write-Host "`n📊 Итоговые модели:" -ForegroundColor Cyan
ollama list

Write-Host "`n✅ Ollama готов к работе!" -ForegroundColor Green
Write-Host "`nКоманды:" -ForegroundColor Cyan
Write-Host "  ollama run llama3.2     - Запустить модель" -ForegroundColor White
Write-Host "  ollama list             - Список моделей" -ForegroundColor White
Write-Host "  ollama pull <model>     - Скачать модель" -ForegroundColor White
Write-Host "  ollama rm <model>       - Удалить модель" -ForegroundColor White
Write-Host "`nAPI эндпоинт: http://localhost:11434" -ForegroundColor White
