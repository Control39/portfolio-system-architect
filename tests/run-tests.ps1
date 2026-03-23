# tests/run-tests.ps1
# Скрипт для запуска тестов разных типов

param(
    [Parameter(Mandatory = $false)]
    [ValidateSet('Unit', 'Integration', 'E2E', 'All')]
    [string]$TestType = 'All',
    
    [Parameter(Mandatory = $false)]
    [switch]$CodeCoverage,
    
    [Parameter(Mandatory = $false)]
    [string[]]$Tag,
    
    [Parameter(Mandatory = $false)]
    [string[]]$ExcludeTag
)
# Run all test types

$ErrorActionPreference = 'Stop'

# Проверка наличия Pester
if (-not (Get-Module -ListAvailable -Name Pester)) {
    Write-Host "❌ Pester не установлен. Устанавливаю..." -ForegroundColor Yellow
    Install-Module -Name Pester -Force -Scope CurrentUser -SkipPublisherCheck
    Import-Module Pester -MinimumVersion 5.0.0
}

# Определение путей тестов
$testPaths = @{}
$testPaths['Unit'] = "$PSScriptRoot\unit"
$testPaths['Integration'] = "$PSScriptRoot\integration"
$testPaths['E2E'] = "$PSScriptRoot\e2e"

# Определение пути для запуска
$pathsToRun = @()
if ($TestType -eq 'All') {
    $pathsToRun = $testPaths.Values
} else {
    $pathsToRun = $testPaths[$TestType]
}

if (-not $pathsToRun) {
    Write-Host "❌ Неверный тип тестов: $TestType" -ForegroundColor Red
    exit 1
}

# Создание директории для результатов
$resultsDir = "$PSScriptRoot\TestResults"
if (-not (Test-Path $resultsDir)) {
    New-Item -ItemType Directory -Path $resultsDir -Force | Out-Null
}

Write-Host "`n🧪 Запуск тестов типа: $TestType" -ForegroundColor Cyan
Write-Host "   Пути: $($pathsToRun -join ', ')" -ForegroundColor Gray

# Параметры для Invoke-Pester
$config = [Pester.Configuration]::Default
$config.Run.Path = $pathsToRun
$config.Output.Verbosity = 'Detailed'
$config.TestResult.OutputFormat = 'NUnitXml'
$config.TestResult.OutputPath = "$resultsDir/testResults_$(Get-Date -Format 'yyyyMMdd_HHmmss').xml"

if ($CodeCoverage) {
    $config.CodeCoverage.Enabled = $true
    $config.CodeCoverage.Path = @(
        "$PSScriptRoot\..\src\**\*.psm1",
        "$PSScriptRoot\..\src\**\*.psm1"
    )
}
$pesterParams = @{ Configuration = $config }

if ($Tag) {
    $pesterParams['Tag'] = $Tag
}

if ($ExcludeTag) {
    $pesterParams['ExcludeTag'] = $ExcludeTag
}

# Запуск тестов
try {
    $results = Invoke-Pester @pesterParams
    
    # Вывод результатов
    Write-Host "`n📊 Результаты тестирования:" -ForegroundColor Cyan
    Write-Host "   Всего тестов: $($results.TotalCount)" -ForegroundColor White
    Write-Host "   Успешно: $($results.PassedCount)" -ForegroundColor Green
    Write-Host "   Провалено: $($results.FailedCount)" -ForegroundColor $(if ($results.FailedCount -gt 0) { 'Red' } else { 'Green' })
    Write-Host "   Пропущено: $($results.SkippedCount)" -ForegroundColor Yellow
    
    if ($CodeCoverage -and $results.CodeCoverage) {
        $coverage = $results.CodeCoverage.CoveragePercent
        Write-Host "`n📈 Покрытие кода: $([math]::Round($coverage, 2))%" -ForegroundColor $(if ($coverage -ge 80) { 'Green' } elseif ($coverage -ge 60) { 'Yellow' } else { 'Red' })
    }
    
    # Сохранение результатов в XML (Pester config handles NUnitXml)
    $xmlPath = $config.TestResult.OutputPath
    Write-Host "`n💾 Результаты сохранены: $xmlPath" -ForegroundColor Gray
    
    # Выход с кодом ошибки, если есть проваленные тесты
    if ($results.FailedCount -gt 0) {
        exit 1
    }
    
    exit 0
    
} catch {
    Write-Host "`n❌ Ошибка при выполнении тестов: $_" -ForegroundColor Red
    Write-Host $_.ScriptStackTrace -ForegroundColor Gray
    exit 1
}
