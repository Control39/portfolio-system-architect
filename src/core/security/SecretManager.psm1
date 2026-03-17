# src/core/security/SecretManager.psm1

using namespace System.Collections.Concurrent
using namespace System.Security.Cryptography
using namespace System.Text

# Класс для результата проверки на утечки
class HardcodedSecretCheckResult {
    [bool] $HasLeaks
    [System.Collections.Generic.List[hashtable]] $Leaks

    HardcodedSecretCheckResult() {
        $this.HasLeaks = $false
        $this.Lees = [System.Collections.Generic.List[hashtable]]::new()
    }
}

class SecretManager {
    hidden static [ConcurrentDictionary[string, string]] $Cache = [ConcurrentDictionary[string, string]]::new()
    hidden static [datetime] $LastCacheRefresh = [datetime]::UtcNow
    hidden static [int] $CacheTTLSeconds = 300
    hidden static [hashtable] $Config = @{}
    hidden static [bool] $Initialized = $false
    hidden static [string] $VaultType = "Environment"  # Environment, AzureKeyVault, HashiCorpVault

    # --- Инициализация ---
    static [void] Initialize([hashtable]$config) {
        if ([SecretManager]::$Initialized) {
            [SecretManager]::WriteDebugLog("SecretManager already initialized.")
            return
        }

        [SecretManager]::$Config = $config.Clone()
        [SecretManager]::$VaultType = $config.VaultType ?? "Environment"
        [SecretManager]::$CacheTTLSeconds = $config.CacheTTL ?? 300

        [SecretManager]::WriteInfoLog("SecretManager initialized. Vault: $([SecretManager]::$VaultType), CacheTTL: $([SecretManager]::$CacheTTLSeconds)s")
        [SecretManager]::$Initialized = $true

        # Запуск сканирования (если возможно)
        [SecretManager]::RunInitialLeakScan()
    }

    # --- Зависимый логгер (чтобы не сломался без StructuredLogger) ---
    hidden static [void] WriteInfoLog([string]$Message) {
        if (Get-Command Write-Log -ErrorAction SilentlyContinue) {
            Write-Log $Message -Level "INFO"
        } else {
            Write-Host "[SecretManager:INFO] $Message"
        }
    }

    hidden static [void] WriteDebugLog([string]$Message) {
        if (Get-Command Write-Log -ErrorAction SilentlyContinue) {
            Write-Log $Message -Level "DEBUG"
        }
    }

    hidden static [void] WriteErrorLog([string]$Message) {
        if (Get-Command Write-Log -ErrorAction SilentlyContinue) {
            Write-Log $Message -Level "ERROR"
        } else {
            Write-Warning "[SecretManager:ERROR] $Message"
        }
    }

    # --- Получение секрета ---
    static [string] GetSecret([string]$Name, [string]$DefaultValue = $null) {
        if (-not [SecretManager]::$Initialized) {
            throw "SecretManager not initialized. Call [SecretManager]::Initialize(config) first."
        }

        [SecretManager]::WriteDebugLog("Getting secret: $Name")

        # 1. Проверка кэша
        if ([SecretManager]::IsCacheValid()) {
            if ([SecretManager]::$Cache.TryGetValue($Name, [ref]$value)) {
                [SecretManager]::WriteDebugLog("Secret '$Name' retrieved from cache.")
                return $value
            }
        } else {
            [SecretManager]::WriteDebugLog("Cache expired. Clearing.")
            [SecretManager]::$Cache.Clear()
            [SecretManager]::$LastCacheRefresh = [datetime]::UtcNow
        }

        # 2. Получение из источника
        $value = [SecretManager]::GetValueFromSource($Name)

        # 3. Fallback
        if (-not $value) {
            [SecretManager]::WriteDebugLog("Secret '$Name' not found. Using default.")
            $value = $DefaultValue
        }

        # 4. Кэширование
        if ($value) {
            [SecretManager]::$Cache[$Name] = $value
            [SecretManager]::WriteDebugLog("Secret '$Name' cached.")
        }

        return $value
    }

    # --- Установка секрета ---
    static [void] SetSecret([string]$Name, [string]$Value, [bool]$Persist = $false) {
        if (-not [SecretManager]::$Initialized) {
            throw "SecretManager not initialized."
        }

        [SecretManager]::WriteDebugLog("Setting secret: $Name")
        $encryptedValue = [SecretManager]::EncryptInMemory($Value)
        [SecretManager]::$Cache[$Name] = $encryptedValue

        if ($Persist) {
            [SecretManager]::WriteWarningLog("Persistence for '$Name' not implemented yet. Vault: $([SecretManager]::$VaultType)")
            # Здесь будет вызов Azure Key Vault / HashiCorp и т.д.
        }
    }

    # --- Источник секретов ---
    hidden static [string] GetValueFromSource([string]$Name) {
        switch ([SecretManager]::$VaultType) {
            "Environment" {
                $envName = $Name.ToUpper() -replace '-', '_'
                return [Environment]::GetEnvironmentVariable($envName)
            }
            "AzureKeyVault" {
                # Заглушка
                [SecretManager]::WriteWarningLog("Azure Key Vault integration not implemented.")
                return $null
            }
            default {
                [SecretManager]::WriteWarningLog("Unknown vault type: $([SecretManager]::$VaultType)")
                return $null
            }
        }
    }

    # --- Потокобезопасная валидация кэша ---
    hidden static [bool] IsCacheValid() {
        $now = [datetime]::UtcNow
        $elapsed = $now - [SecretManager]::$LastCacheRefresh
        return $elapsed.TotalSeconds -lt [SecretManager]::$CacheTTLSeconds
    }

    # --- Маскирование секретов в тексте ---
    static [string] MaskSecretsInText([string]$Text) {
        if ([string]::IsNullOrWhiteSpace($Text)) { return $Text }

        $result = $Text
        foreach ($name in [SecretManager]::$Cache.Keys) {
            $value = [SecretManager]::DecryptInMemory([SecretManager]::$Cache[$name])
            if ($value -and $value.Length -ge 4) {
                $safeValue = [regex]::Escape($value)
                $result = $result -replace $safeValue, "***MASKED***"
            }
        }
        return $result
    }

    # --- Проверка на хардкод ---
    static [HardcodedSecretCheckResult] CheckForHardcodedSecrets([string]$TargetPath) {
        $result = [HardcodedSecretCheckResult]::new()
        $extensions = @('.ps1', '.py', '.json', '.yaml', '.yml', '.env', '.config', '.txt')

        $files = Get-ChildItem $TargetPath -File -Recurse -ErrorAction SilentlyContinue |
                 Where-Object { $_.Extension -in $extensions }

        foreach ($file in $files) {
            $content = $null
            try {
                $content = Get-Content $file.FullName -Raw -Encoding UTF8 -ErrorAction Stop
            } catch {
                [SecretManager]::WriteDebugLog("Cannot read file: $($file.FullName)")
                continue
            }

            foreach ($name in [SecretManager]::$Cache.Keys) {
                $value = [SecretManager]::DecryptInMemory([SecretManager]::$Cache[$name])
                if ($value -and $value.Length -ge 8 -and $content -match [regex]::Escape($value)) {
                    $result.HasLeaks = $true
                    $result.Lees.Add(@{
                        FilePath = $file.FullName
                        SecretName = $name
                        LineNumber = ($content.Substring(0, [Math]::Min($content.IndexOf($value), 1000)) -split '\n').Count
                    })

                    [SecretManager]::WriteErrorLog("Hardcoded secret '$name' found in $($file.FullName)")
                }
            }
        }

        return $result
    }

    # --- Запуск сканирования при инициализации ---
    hidden static [void] RunInitialLeakScan() {
        [SecretManager]::WriteInfoLog("Running initial leak scan...")

        if (Get-Command "Invoke-SecurityScan" -ErrorAction SilentlyContinue) {
            try {
                $checkResult = [SecretManager]::CheckForHardcodedSecrets((Get-Location).Path)
                if ($checkResult.HasLeaks) {
                    [SecretManager]::WriteErrorLog("Initial scan found hardcoded secrets! $($checkResult.Lees.Count) leaks detected.")
                }
            } catch {
                [SecretManager]::WriteWarningLog("Initial leak scan failed: $($_.Exception.Message)")
            }
        } else {
            [SecretManager]::WriteDebugLog("SecurityScanner not available. Skipping initial scan.")
        }
    }

    # --- Шифрование в памяти (упрощённое) ---
    hidden static [string] EncryptInMemory([string]$Data) {
        if (-not $Data) { return $Data }
        $bytes = [Text.Encoding]::UTF8.GetBytes($Data)
        $encrypted = [Convert]::ToBase64String($bytes)
        return "enc:$encrypted"
    }

    hidden static [string] DecryptInMemory([string]$Data) {
        if (-not $Data -or -not $Data.StartsWith("enc:")) { return $Data }
        try {
            $bytes = [Convert]::FromBase64String($Data.Substring(4))
            return [Text.Encoding]::UTF8.GetString($bytes)
        } catch {
            return $Data
        }
    }

    # --- Вспомогательные методы ---
    static [string[]] GetAllSecretNames() {
        return @([SecretManager]::$Cache.Keys)
    }

    static [hashtable] GetAllSecrets() {
        $all = @{}
        foreach ($name in [SecretManager]::$Cache.Keys) {
            $all[$name] = [SecretManager]::DecryptInMemory([SecretManager]::$Cache[$name])
        }
        return $all
    }

    hidden static [void] WriteWarningLog([string]$Message) {
        if (Get-Command Write-Log -ErrorAction SilentlyContinue) {
            Write-Log $Message -Level "WARN"
        } else {
            Write-Warning "[SecretManager:WARN] $Message"
        }
    }
}

Export-ModuleMember -Class SecretManager
