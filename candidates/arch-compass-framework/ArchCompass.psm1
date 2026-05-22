# ArchCompass.psm1 - главный модуль
$ErrorActionPreference = 'Stop'
$ModuleRoot = $PSScriptRoot

# агрузка подмодулей
$modules = @(
    "src\\core\\utilities\\ConfigurationManager.psm1"
    "src\\infrastructure\\security\\SecretManager.psm1"
    "src\\infrastructure\\security\\SecurityScanner.psm1"
    "src\\core\\logging\\StructuredLogger.psm1"
    "src\\core\\validation\\InputValidator.psm1"
    "src\\ai\\providers\\OpenAIIntegration.psm1"
    "src\\core\\commands\\CommandFactory.psm1"
)

foreach ($module in $modules) {
    $path = Join-Path $ModuleRoot $module
    if (Test-Path $path) {
        Write-Verbose "агрузка: $module"
        Import-Module $path -Force -ErrorAction Stop
    } else {
        Write-Warning "одуль не найден: $path"
    }
}

# сновная команда
function Start-ArchCompass {
    param(
        [string]$Environment = "default",
        [switch]$RunSecurityTests,
        [switch]$Help
    )

    if ($Help) {
        Write-Host @"
🧭 Arch-Compass Framework
спользование: Start-ArchCompass [-Environment <имя>] [-RunSecurityTests]
оступные окружения: development, staging, production
"@
        return
    }

    Write-Host "✅ Arch-Compass запущен в режиме: $Environment" -ForegroundColor Green
    if ($RunSecurityTests) {
        Write-Host "🔍 апуск тестов безопасности..." -ForegroundColor Yellow
        # десь будет вызов Invoke-SecurityScan
    }
}

Export-ModuleMember -Function Start-ArchCompass
