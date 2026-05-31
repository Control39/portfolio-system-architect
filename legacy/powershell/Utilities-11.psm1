# src/core/utilities/Utilities.psm1

function Main {
    # ... инициализация ...

    [SecretManager]::Initialize()
    [StructuredLogger]::Initialize()

    # === КЛЮЧЕВАЯ СТРОКА: подключаем маскирование ===
    [StructuredLogger]::SetMasker([SecretManager]::GetSecretMasker())

    # === Проверка на утечки ===
    Write-Log "Running self-security check..." -Level "INFO"
    $leaks = [SecurityScanner]::ScanForSecretManagerLeaks((Get-Location).Path)
    if ($leaks.Count -gt 0) {
        foreach ($leak in $leaks) {
            Write-Log $leak -Level "ERROR"
        }
        throw "CRITICAL: SecretManager detected self-leaks! Aborting."
    }

    # ... остальная логика ...
}
