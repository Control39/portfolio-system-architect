# src/core/logging/AsyncLogger.psm1
# DEPRECATED: Этот модуль устарел. Используйте StructuredLogger.psm1
# Оставлен для обратной совместимости

Write-Warning "AsyncLogger.psm1 устарел. Используйте StructuredLogger.psm1"

function Write-Log {
    param(
        [string]$Message,
        [string]$Level = "Info"
    )
    
    Write-Warning "Write-Log из AsyncLogger устарел. Используйте Write-Log из StructuredLogger"
    Write-Host "[$Level] $Message"
}

Export-ModuleMember -Function Write-Log

