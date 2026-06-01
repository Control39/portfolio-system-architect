# scripts/fix_config_paths.ps1
# Массовое исправление путей к REPO_ROOT во всех config_integration.py

$ErrorActionPreference = "Stop"

Write-Host "🔧 Начало исправления путей к конфигурации..." -ForegroundColor Cyan

# Найти все config_integration.py в apps/
$files = Get-ChildItem -Path "apps" -Recurse -Filter "config_integration.py"
$fixedCount = 0
$skippedCount = 0

foreach ($file in $files) {
    $content = Get-Content -Path $file.FullName -Raw -Encoding UTF8

    # Паттерн для исправления: 3 уровня parent → 4 уровня
    $oldPattern = 'REPO_ROOT = Path\(__file__\)\.parent\.parent\.parent'
    $newLine = 'REPO_ROOT = Path(__file__).parent.parent.parent.parent  # корень проекта (на уровень выше apps/)'

    if ($content -match [regex]::Escape($oldPattern)) {
        $content = $content -replace [regex]::Escape($oldPattern), $newLine
        Set-Content -Path $file.FullName -Value $content -Encoding UTF8 -NoNewline
        Write-Host "✅ Исправлен: $($file.FullName)" -ForegroundColor Green
        $fixedCount++
    } else {
        Write-Host "⏭️  Пропущен (уже исправлен или другой паттерн): $($file.FullName)" -ForegroundColor Yellow
        $skippedCount++
    }
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Исправлено: $fixedCount файлов" -ForegroundColor Green
Write-Host "Пропущено: $skippedCount файлов" -ForegroundColor Yellow
Write-Host "================================" -ForegroundColor Cyan

# Проверка, что конфиг существует
$configPath = "config\ai-config.yaml"
if (Test-Path $configPath) {
    Write-Host "✅ Конфигурация найдена: $configPath" -ForegroundColor Green
    $configSize = (Get-Item $configPath).Length
    Write-Host "   Размер: $configSize байт" -ForegroundColor Gray
} else {
    Write-Host "⚠️  Конфигурация НЕ найдена: $configPath" -ForegroundColor Red
    Write-Host "   Создаём базовый конфиг..." -ForegroundColor Yellow

    $configDir = "config"
    if (-not (Test-Path $configDir)) {
        New-Item -ItemType Directory -Path $configDir -Force | Out-Null
        Write-Host "📁 Создана директория: $configDir" -ForegroundColor Green
    }

    @"
# AI Config Manager - глобальная конфигурация
# Генерируется автоматически, редактируется через UI
services:
  cognitive_agent:
    scanner_interval: 60
    planner_interval: 120
    learning_interval: 300
    autonomy_level: medium
  job_search:
    base_url: http://localhost:8006
    timeout: 30
  infra_orchestrator:
    port: 8200
  monitoring:
    enabled: true
  decision_engine:
    database_url: postgresql://postgres:postgres@localhost:5432/portfolio
    rag_enabled: true
"@ | Set-Content -Path $configPath -Encoding UTF8 -NoNewline

    Write-Host "✅ Создан базовый конфиг: $configPath" -ForegroundColor Green
}

Write-Host ""
Write-Host "Готово! Запусти проверку:" -ForegroundColor Cyan
Write-Host "python -c `"from apps.cognitive_agent.src.config_integration import get_config; print('✅ is_available():', get_config().is_available())`""
