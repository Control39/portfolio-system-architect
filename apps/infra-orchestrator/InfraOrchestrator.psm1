# InfraOrchestrator.psm1 - главный модуль
$ErrorActionPreference = 'Stop'
$ModuleRoot = $PSScriptRoot

# Загрузка существующих подмодулей
$modules = @(
    "src\core\utilities\ConfigurationManager.psm1"
    "src\infrastructure\security\SecretManager.psm1"
    "src\infrastructure\security\SecurityScanner.psm1"
    "src\core\logging\StructuredLogger.psm1"
    "src\core\validation\InputValidator.psm1"
    "src\ai\providers\OpenAIIntegration.psm1"
    "src\core\commands\CommandFactory.psm1"
)

foreach ($module in $modules) {
    $path = Join-Path $ModuleRoot $module
    if (Test-Path $path) {
        Write-Verbose "Загрузка: $module"
        Import-Module $path -Force -ErrorAction Stop
    } else {
        Write-Warning "Модуль не найден: $path"
    }
}

# Загрузка новых модулей (архитектурное усиление)
$newModules = @(
    "src/ai/providers/AiProviderFactory.psm1"
    "src/core/diagnostics/HealthCheck.psm1"
    "src/core/diagnostics/ArchitectureReport.psm1"
    "src/core/integrations/CompassAudit.psm1"
)

foreach ($module in $newModules) {
    $path = Join-Path $ModuleRoot $module
    if (Test-Path $path) {
        Import-Module $path -Force -ErrorAction SilentlyContinue
        Write-Verbose "Загружено архитектурное расширение: $module"
    } else {
        Write-Warning "Архитектурный модуль не найден: $path"
    }
}

# Основная команда
function Start-InfraOrchestrator {
    param(
        [string]$Environment = "default",
        [switch]$RunSecurityTests,
        [switch]$Help,
        [switch]$Version,
        [switch]$Health,
        [switch]$Metrics,
        [switch]$Diagram
    )

    # Версия
    if ($Version) {
        $manifest = Import-PowerShellDataFile -Path "$PSScriptRoot/InfraOrchestrator.psd1" -ErrorAction SilentlyContinue
        $version = if ($manifest) { $manifest.ModuleVersion } else { "7.0.0" }
        Write-Host "🔧 Infra-Orchestrator Framework v$version"
        Write-Host "📦 Author: Ekaterina Kudelya (Cognitive Architect)"
        Write-Host "📜 License: CC BY-ND 4.0 (методология), MIT (код)"
        return
    }

    # Self-Audit (Health Check)
    if ($Health) {
        if (Get-Command Test-InfraOrchestratorHealth -ErrorAction SilentlyContinue) {
            return Test-InfraOrchestratorHealth -Detailed
        } else {
            Write-Warning "HealthCheck модуль не загружен. Проверьте путь: src/core/diagnostics/HealthCheck.psm1"
            return
        }
    }

    # Prometheus метрики
    if ($Metrics) {
        if (Get-Command Export-PrometheusMetrics -ErrorAction SilentlyContinue) {
            return Export-PrometheusMetrics
        } else {
            Write-Warning "MetricsExporter модуль не загружен"
            return
        }
    }

    # Генерация архитектурной диаграммы
    if ($Diagram) {
        if (Get-Command Export-ArchitectureDiagram -ErrorAction SilentlyContinue) {
            return Export-ArchitectureDiagram -Format Mermaid
        } else {
            Write-Warning "ArchitectureReport модуль не загружен"
            return
        }
    }

    # Help
    if ($Help) {
        Write-Host @"
🔧 Infra-Orchestrator Framework
Использование: Start-InfraOrchestrator [-Environment <имя>] [-RunSecurityTests] [-Version] [-Health] [-Metrics] [-Diagram]

Параметры:
  -Environment     : Окружение (development, staging, production)
  -RunSecurityTests: Запуск тестов безопасности
  -Version         : Показать версию фреймворка
  -Health          : Запустить self-audit (проверка всех модулей)
  -Metrics         : Экспортировать метрики в формате Prometheus
  -Diagram         : Сгенерировать Mermaid-диаграмму архитектуры
  -Help            : Показать эту справку

Примеры:
  Start-InfraOrchestrator -Environment production
  Start-InfraOrchestrator -Version
  Start-InfraOrchestrator -Health -Detailed
  Start-InfraOrchestrator -Metrics
  Start-InfraOrchestrator -Diagram
"@
        return
    }

    # Основной запуск
    Write-Host "✅ Infra-Orchestrator запущен в режиме: $Environment" -ForegroundColor Green

    if ($RunSecurityTests) {
        Write-Host "🔍 Запуск тестов безопасности..." -ForegroundColor Yellow
        if (Get-Command Invoke-SecurityScan -ErrorAction SilentlyContinue) {
            Invoke-SecurityScan
        } else {
            Write-Warning "SecurityScanner модуль не загружен"
        }
    }

    # Интеграция с IT-Compass (если нужна)
    Write-Host "💡 Совет: Для аудита компетенций выполните: Invoke-CompassAudit -CompassPath '../it-compass'" -ForegroundColor Cyan
}

# Экспорт функций
Export-ModuleMember -Function Start-InfraOrchestrator

# Дополнительные функции для прямого доступа (опционально)
if (Get-Command Test-InfraOrchestratorHealth -ErrorAction SilentlyContinue) {
    Export-ModuleMember -Function Test-InfraOrchestratorHealth
}

if (Get-Command Export-PrometheusMetrics -ErrorAction SilentlyContinue) {
    Export-ModuleMember -Function Export-PrometheusMetrics
}

if (Get-Command Export-ArchitectureDiagram -ErrorAction SilentlyContinue) {
    Export-ModuleMember -Function Export-ArchitectureDiagram
}

if (Get-Command Invoke-CompassAudit -ErrorAction SilentlyContinue) {
    Export-ModuleMember -Function Invoke-CompassAudit
}

Write-Verbose "🔧 Infra-Orchestrator Framework полностью загружен"
