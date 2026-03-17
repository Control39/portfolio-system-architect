# ArchCompass.psm1

# === Определяем корень модуля ===
$ModuleRoot = $PSScriptRoot

# === Вспомогательная функция для импорта ===
function Import-ModuleFile {
    param([string]$Path)
    $FullPath = Join-Path $ModuleRoot $Path
    if (Test-Path $FullPath) {
        . $FullPath
    } else {
        throw "Module file not found: $FullPath"
    }
}

# === Импорт модулей в правильном порядке ===

# 1. Конфигурация — ДОЛЖНА БЫТЬ ПЕРВАЯ
Import-ModuleFile "src/core/configuration/ConfigurationManager.psm1"

# 2. Безопасность — до логгера и других
Import-ModuleFile "src/core/security/SecretManager.psm1"
Import-ModuleFile "src/core/security/SecurityScanner.psm1"

# 3. Логирование
Import-ModuleFile "src/core/logging/StructuredLogger.psm1"  # ранее AsyncLogger

# 4. Валидация
Import-ModuleFile "src/core/validation/Validators.psm1"

# 5. Остальные core-модули
Import-ModuleFile "src/core/rollback/RollbackManager.psm1"
Import-ModuleFile "src/core/localization/Localization.psm1"
Import-ModuleFile "src/core/utilities/Utilities.psm1"

# 6. Инфраструктура
Import-ModuleFile "src/infrastructure/creation/FileCreator.psm1"
Import-ModuleFile "src/infrastructure/monitoring/Metrics.psm1"
Import-ModuleFile "src/infrastructure/git/GitHelper.psm1"
Import-ModuleFile "src/infrastructure/deployment/Cloud.psm1"

# 7. AI
Import-ModuleFile "src/ai/OpenAIIntegration.psm1"

# 8. Очереди
Import-ModuleFile "src/queues/RabbitMQClient.psm1"

# === Экспорт всех нужных функций ===
# Предположим, Utilities.psm1 экспортирует Main и другие
Export-ModuleMember -Function Main, Write-Log, Get-LocalizedString, Test-Dependencies
