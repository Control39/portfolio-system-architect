# SecretManager.psm1 - Управление секретами с маскированием, кэшированием и ротацией

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
        $masked = $secretValue.Substring(0, [Math]::Min(4, $secretValue.Length)) + "****"
        return $text.Replace($secretValue, $masked)
    }
}

Export-ModuleMember -Variable SecretManager -Function GetSecret, SetSecret, Initialize
