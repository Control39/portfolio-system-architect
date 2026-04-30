# src/infrastructure/security/SecretManager.psm1
# SecretManager - управление секретами с маскированием, кэшированием и ротацией

class SecretCacheEntry {
    [string] $Value
    [DateTime] $ExpiresAt
    [SecureString] $SecureValue

    SecretCacheEntry([string]$value, [int]$ttlSeconds = 3600) {
        $this.Value = $value
        $this.ExpiresAt = (Get-Date).AddSeconds($ttlSeconds)
        if ($value) {
            $this.SecureValue = ConvertTo-SecureString -String $value -AsPlainText -Force
        }
    }

    [bool] IsExpired() {
        return (Get-Date) -gt $this.ExpiresAt
    }
}

class SecretManager {
    hidden static [hashtable] $Cache = @{}
    hidden static [string] $VaultType = "Environment"
    hidden static [int] $DefaultTTL = 3600  # 1 час
    hidden static [hashtable] $KnownSecrets = @{}  # Имена известных секретов для сканирования

    static [void] Initialize([hashtable]$config) {
        [SecretManager]::VaultType = $config.VaultType
        if ($config.CacheTTL) {
            [SecretManager]::DefaultTTL = $config.CacheTTL
        }

        # Регистрация известных секретов для сканирования
        $knownSecretNames = @(
            'OPENAI_API_KEY',
            'ANTHROPIC_API_KEY',
            'AZURE_SUBSCRIPTION_ID',
            'AZURE_CLIENT_SECRET',
            'RABBITMQ_PASSWORD',
            'PROMETHEUS_PASSWORD',
            'KHOJ_ADMIN_PASSWORD',
            'KHOJ_DJANGO_SECRET_KEY'
        )

        foreach ($name in $knownSecretNames) {
            [SecretManager]::KnownSecrets[$name] = $true
        }

        # Выполнить сканирование на утечки при инициализации
        if ($config.ScanForLeaksOnInitialize -ne $false) {
            [SecretManager]::ScanForLeaksOnInitialize()
        }
    }

    static [string] GetSecret([string]$secretName, [string]$defaultValue = $null) {
        # Проверить кэш
        if ([SecretManager]::Cache.ContainsKey($secretName)) {
            $entry = [SecretManager]::Cache[$secretName]
            if (-not $entry.IsExpired()) {
                return $entry.Value
            } else {
                # Кэш истек, удаляем
                [SecretManager]::Cache.Remove($secretName)
            }
        }

        # Получить из переменных окружения
        $secretValue = [Environment]::GetEnvironmentVariable($secretName)

        # Если не найдено, использовать дефолт
        if (-not $secretValue) {
            $secretValue = $defaultValue
        }

        # Запомнить в кэше
        if ($secretValue) {
            $entry = [SecretCacheEntry]::new($secretValue, [SecretManager]::DefaultTTL)
            [SecretManager]::Cache[$secretName] = $entry
        }

        return $secretValue
    }

    static [void] SetSecret([string]$secretName, [string]$secretValue, [bool]$persist = $true) {
        $entry = [SecretCacheEntry]::new($secretValue, [SecretManager]::DefaultTTL)
        [SecretManager]::Cache[$secretName] = $entry

        if ($persist) {
            [Environment]::SetEnvironmentVariable($secretName, $secretValue, "User")
        }
    }

    # Маскирование секрета в строке
    static [string] MaskSecret([string]$text, [string]$secretValue) {
        if (-not $text -or -not $secretValue) {
            return $text
        }

        # Заменяем значение секрета на маскированное
        $masked = $text -replace [regex]::Escape($secretValue), '***MASKED_SECRET***'
        return $masked
    }

    # Маскирование всех известных секретов в объекте (для логирования)
    static [object] MaskSecretsInObject([object]$obj) {
        if ($null -eq $obj) {
            return $null
        }

        if ($obj -is [string]) {
            $result = $obj
            foreach ($secretName in [SecretManager]::KnownSecrets.Keys) {
                $secretValue = [SecretManager]::GetSecret($secretName)
                if ($secretValue) {
                    $result = [SecretManager]::MaskSecret($result, $secretValue)
                }
            }
            return $result
        }

        if ($obj -is [hashtable] -or $obj -is [PSCustomObject]) {
            $result = @{}
            foreach ($key in $obj.PSObject.Properties.Name) {
                $value = $obj.$key

                # Если ключ содержит "secret", "password", "key", "token" - маскируем
                if ($key -match '(?i)(secret|password|key|token|api[_-]?key)') {
                    $result[$key] = '***MASKED_SECRET***'
                } else {
                    # Рекурсивно обрабатываем вложенные объекты
                    $result[$key] = [SecretManager]::MaskSecretsInObject($value)
                }
            }
            return $result
        }

        if ($obj -is [array]) {
            return $obj | ForEach-Object { [SecretManager]::MaskSecretsInObject($_) }
        }

        return $obj
    }

    # Проверка на хардкод секретов в файлах
    static [array] CheckForHardcodedSecrets([string[]]$filePaths) {
        $violations = @()

        foreach ($filePath in $filePaths) {
            if (-not (Test-Path $filePath)) {
                continue
            }

            $content = Get-Content -Path $filePath -Raw -ErrorAction SilentlyContinue
            if (-not $content) {
                continue
            }

            foreach ($secretName in [SecretManager]::KnownSecrets.Keys) {
                $secretValue = [SecretManager]::GetSecret($secretName)
                if ($secretValue -and $content -match [regex]::Escape($secretValue)) {
                    $violations += @{
                        File = $filePath
                        SecretName = $secretName
                        Line = ($content -split "`n" | Select-String -Pattern [regex]::Escape($secretValue) | Select-Object -First 1).LineNumber
                    }
                }
            }
        }

        return $violations
    }

    # Получить список паттернов секретов для SecurityScanner
    static [string[]] GetCurrentSecretPatterns() {
        return [SecretManager]::KnownSecrets.Keys
    }

    # Ротация секрета
    static [bool] RotateSecret([string]$secretName, [string]$newValue) {
        try {
            [SecretManager]::SetSecret($secretName, $newValue, $true)

            # Инвалидировать старый кэш
            if ([SecretManager]::Cache.ContainsKey($secretName)) {
                [SecretManager]::Cache.Remove($secretName)
            }

            return $true
        } catch {
            return $false
        }
    }

    # Сканирование на утечки при инициализации
    hidden static [void] ScanForLeaksOnInitialize() {
        $projectRoot = $PSScriptRoot
        while ($projectRoot -and -not (Test-Path (Join-Path $projectRoot '.git'))) {
            $projectRoot = Split-Path $projectRoot -Parent
        }

        if (-not $projectRoot) {
            return
        }

        # Сканируем только .psm1 и .ps1 файлы
        $filesToScan = Get-ChildItem -Path $projectRoot -Include *.psm1,*.ps1 -Recurse -ErrorAction SilentlyContinue |
            Where-Object { $_.FullName -notmatch '\\node_modules\\|\\\.git\\|\\TestResults\\' } |
            Select-Object -ExpandProperty FullName

        if ($filesToScan) {
            $violations = [SecretManager]::CheckForHardcodedSecrets($filesToScan)
            if ($violations.Count -gt 0) {
                Write-Warning "⚠️  Обнаружены потенциальные хардкод секреты:"
                foreach ($violation in $violations) {
                    Write-Warning "   Файл: $($violation.File), Секрет: $($violation.SecretName), Строка: $($violation.Line)"
                }
            }
        }
    }
}
