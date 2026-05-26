# Скрипт настройки GigaCode для Windows PowerShell
# Автор: SourceCraft Code Assistant
# Дата: 2026-04-10

param(
    [string]$ApiKey,
    [switch]$NoAutoInstall,
    [string]$ProjectRoot = "."
)

function Write-Header {
    param([string]$Title)
    Write-Host "=" * 60 -ForegroundColor Cyan
    Write-Host $Title -ForegroundColor Cyan
    Write-Host "=" * 60 -ForegroundColor Cyan
}

function Test-VSCodeInstalled {
    try {
        $result = code --version 2>$null
        return $LASTEXITCODE -eq 0
    }
    catch {
        return $false
    }
}

function Test-GigaCodeExtension {
    try {
        $extensions = code --list-extensions 2>$null
        return $extensions -contains "GigaCode.gigacode-vscode"
    }
    catch {
        return $false
    }
}

function Install-GigaCodeExtension {
    try {
        Write-Host "Установка расширения GigaCode..." -ForegroundColor Yellow
        code --install-extension GigaCode.gigacode-vscode 2>$null
        return $LASTEXITCODE -eq 0
    }
    catch {
        return $false
    }
}

function Get-CurrentSettings {
    $settingsFile = Join-Path $ProjectRoot ".vscode\settings.json"
    if (Test-Path $settingsFile) {
        try {
            $content = Get-Content $settingsFile -Raw -Encoding UTF8
            return $content | ConvertFrom-Json
        }
        catch {
            return @{}
        }
    }
    return @{}
}

function Create-GigaCodeConfig {
    param([string]$ApiKey)
    
    $config = @{
        "gigacode.enabled" = $true
        "gigacode.model" = "GigaChat"
        "gigacode.maxTokens" = 4000
        "gigacode.temperature" = 0.7
        "gigacode.enableCodeCompletion" = $true
        "gigacode.enableChat" = $true
        "gigacode.language" = "ru"
        "gigacode.autoSuggest" = $true
        "gigacode.suggestDelay" = 300
        "gigacode.contextWindow" = 8000
        
        # Настройки для языков
        "gigacode.python.enabled" = $true
        "gigacode.typescript.enabled" = $true
        "gigacode.javascript.enabled" = $true
        "gigacode.yaml.enabled" = $true
        "gigacode.markdown.enabled" = $true
        
        # Интеграция
        "gigacode.integrateWithCopilot" = $false
        "gigacode.fallbackToSourceCraft" = $true
        "gigacode.showTokenUsage" = $true
        
        # Экономия токенов
        "gigacode.useForSimpleTasks" = $false
        "gigacode.cacheResponses" = $true
        "gigacode.dailyUsageLimit" = 1000
        
        # Уведомления
        "gigacode.notifyOnLowTokens" = $true
        "gigacode.lowTokenThreshold" = 50
        "gigacode.notifyOnFallback" = $true
    }
    
    if ($ApiKey) {
        $config["gigacode.apiKey"] = $ApiKey
    }
    
    return $config
}

function Merge-Settings {
    param($CurrentSettings, $GigaCodeConfig)
    
    $merged = @{}
    
    # Копируем текущие настройки
    if ($CurrentSettings) {
        $CurrentSettings.PSObject.Properties | ForEach-Object {
            $merged[$_.Name] = $_.Value
        }
    }
    
    # Добавляем настройки GigaCode
    $GigaCodeConfig.GetEnumerator() | ForEach-Object {
        $merged[$_.Key] = $_.Value
    }
    
    return $merged
}

function Save-Settings {
    param($Settings)
    
    $vscodeDir = Join-Path $ProjectRoot ".vscode"
    $settingsFile = Join-Path $vscodeDir "settings.json"
    
    try {
        if (-not (Test-Path $vscodeDir)) {
            New-Item -ItemType Directory -Path $vscodeDir -Force | Out-Null
        }
        
        $Settings | ConvertTo-Json -Depth 10 | Out-File $settingsFile -Encoding UTF8
        return $true
    }
    catch {
        return $false
    }
}

function Create-EnvExample {
    $envExample = Join-Path $ProjectRoot ".env.example"
    
    $content = @"
# Настройки GigaCode
# Скопируйте этот файл в .env и заполните значения

# Токен GigaCode (получить на https://gigachat.cloud)
GIGACODE_API_KEY=ваш_токен_здесь

# Настройки модели
GIGACODE_MODEL=GigaChat
GIGACODE_MAX_TOKENS=4000
GIGACODE_TEMPERATURE=0.7

# Язык интерфейса
GIGACODE_LANGUAGE=ru

# Настройки для экономии токенов
GIGACODE_DAILY_LIMIT=1000
GIGACODE_USE_FOR_SIMPLE_TASKS=false

# Интеграция с SourceCraft
GIGACODE_FALLBACK_TO_SOURCECRAFT=true
"@
    
    try {
        $content | Out-File $envExample -Encoding UTF8
        return $true
    }
    catch {
        return $false
    }
}

# Основной процесс настройки
Write-Header "НАСТРОЙКА GIGACODE ДЛЯ VS CODE"

$steps = @()

# Шаг 1: Проверка VS Code
Write-Host "`n1. Проверка установки VS Code..." -ForegroundColor Green
$vscodeInstalled = Test-VSCodeInstalled
$steps += @{
    Name = "Проверка VS Code"
    Success = $vscodeInstalled
    Message = if ($vscodeInstalled) { "VS Code установлен" } else { "VS Code не найден" }
}

if (-not $vscodeInstalled) {
    Write-Host "❌ VS Code не установлен. Установите VS Code и повторите." -ForegroundColor Red
    exit 1
}

# Шаг 2: Проверка расширения GigaCode
Write-Host "`n2. Проверка расширения GigaCode..." -ForegroundColor Green
$gigacodeInstalled = Test-GigaCodeExtension
$steps += @{
    Name = "Проверка расширения GigaCode"
    Success = $gigacodeInstalled
    Message = if ($gigacodeInstalled) { "Расширение GigaCode установлено" } else { "Расширение GigaCode не установлено" }
}

# Шаг 3: Установка расширения
if (-not $gigacodeInstalled -and -not $NoAutoInstall) {
    Write-Host "`n3. Установка расширения GigaCode..." -ForegroundColor Green
    $installSuccess = Install-GigaCodeExtension
    $steps += @{
        Name = "Установка расширения GigaCode"
        Success = $installSuccess
        Message = if ($installSuccess) { "Расширение успешно установлено" } else { "Ошибка установки" }
    }
    
    if ($installSuccess) {
        $gigacodeInstalled = $true
    }
}
elseif (-not $gigacodeInstalled) {
    $steps += @{
        Name = "Установка расширения GigaCode"
        Success = $false
        Message = "Пропущено (NoAutoInstall)"
    }
}

if (-not $gigacodeInstalled) {
    Write-Host "❌ Расширение GigaCode не установлено." -ForegroundColor Red
    Write-Host "   Установите вручную: code --install-extension GigaCode.gigacode-vscode" -ForegroundColor Yellow
}

# Шаг 4: Загрузка текущих настроек
Write-Host "`n4. Загрузка текущих настроек VS Code..." -ForegroundColor Green
$currentSettings = Get-CurrentSettings
$steps += @{
    Name = "Загрузка текущих настроек"
    Success = $true
    Message = "Загружено $($currentSettings.Count) настроек"
}

# Шаг 5: Создание конфигурации GigaCode
Write-Host "`n5. Создание конфигурации GigaCode..." -ForegroundColor Green
$gigacodeConfig = Create-GigaCodeConfig -ApiKey $ApiKey
$steps += @{
    Name = "Создание конфигурации GigaCode"
    Success = $true
    Message = "Создано $($gigacodeConfig.Count) настроек"
}

# Шаг 6: Объединение настроек
Write-Host "`n6. Объединение настроек..." -ForegroundColor Green
$mergedSettings = Merge-Settings -CurrentSettings $currentSettings -GigaCodeConfig $gigacodeConfig
$steps += @{
    Name = "Объединение настроек"
    Success = $true
    Message = "Итоговых настроек: $($mergedSettings.Count)"
}

# Шаг 7: Сохранение настроек
Write-Host "`n7. Сохранение настроек..." -ForegroundColor Green
$saveSuccess = Save-Settings -Settings $mergedSettings
$steps += @{
    Name = "Сохранение настроек"
    Success = $saveSuccess
    Message = if ($saveSuccess) { "Сохранено в .vscode\settings.json" } else { "Ошибка сохранения" }
}

# Шаг 8: Создание .env.example
Write-Host "`n8. Создание .env.example..." -ForegroundColor Green
$envSuccess = Create-EnvExample
$steps += @{
    Name = "Создание .env.example"
    Success = $envSuccess
    Message = if ($envSuccess) { "Создан файл .env.example" } else { "Ошибка создания" }
}

# Генерация отчета
Write-Host "`n" + ("=" * 60) -ForegroundColor Cyan
Write-Host "ОТЧЕТ О НАСТРОЙКЕ GIGACODE" -ForegroundColor Cyan
Write-Host ("=" * 60) -ForegroundColor Cyan

$successCount = 0
foreach ($step in $steps) {
    $status = if ($step.Success) { "✅ УСПЕХ" } else { "❌ ОШИБКА" }
    Write-Host "$status: $($step.Name)" -ForegroundColor $(if ($step.Success) { "Green" } else { "Red" })
    Write-Host "   $($step.Message)" -ForegroundColor Gray
    
    if ($step.Success) {
        $successCount++
    }
}

Write-Host "`n" + ("=" * 60) -ForegroundColor Cyan
Write-Host "ИТОГ: $successCount/$($steps.Count) шагов выполнено успешно" -ForegroundColor Cyan

if ($successCount -eq $steps.Count) {
    Write-Host "🎉 Настройка GigaCode завершена успешно!" -ForegroundColor Green
}
elseif ($successCount -ge [math]::Round($steps.Count * 0.7)) {
    Write-Host "⚠️ Настройка завершена с предупреждениями" -ForegroundColor Yellow
}
else {
    Write-Host "❌ Настройка завершена с ошибками" -ForegroundColor Red
}

Write-Host ("=" * 60) -ForegroundColor Cyan

# Сохранение отчета
$reportDir = Join-Path $ProjectRoot ".codeassistant\reports"
$reportFile = Join-Path $reportDir "gigacode_setup_report_ps.md"

try {
    if (-not (Test-Path $reportDir)) {
        New-Item -ItemType Directory -Path $reportDir -Force | Out-Null
    }
    
    $reportContent = @"
# Отчет о настройке GigaCode (PowerScript)
Дата: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
Проект: $(Split-Path $ProjectRoot -Leaf)

## Результаты
$($steps | ForEach-Object { "- $($_.Name): $(if ($_.Success) { '✅' } else { '❌' }) $($_.Message)" } | Out-String)

## Итог
Успешно: $successCount/$($steps.Count) шагов
"@
    
    $reportContent | Out-File $reportFile -Encoding UTF8
    Write-Host "`n📄 Отчет сохранен в: $reportFile" -ForegroundColor Cyan
}
catch {
    Write-Host "`n⚠️ Не удалось сохранить отчет: $_" -ForegroundColor Yellow
}

# Возвращаем код выхода
if ($successCount -ge [math]::Round($steps.Count * 0.8)) {
    exit 0
}
else {
    exit 1
}