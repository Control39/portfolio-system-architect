# src/core/validation/InputValidator.psm1

# Класс для результата валидации
class ValidationResult {
    [bool] $IsValid
    [hashtable] $Errors
    [hashtable] $Warnings

    ValidationResult() {
        $this.IsValid = $true
        $this.Errors = @{}
        $this.Warnings = @{}
    }

    [void] AddError([string]$Field, [string]$Message) {
        $this.Errors[$Field] = $Message
        $this.IsValid = $false
    }

    [void] AddWarning([string]$Field, [string]$Message) {
        $this.Warnings[$Field] = $Message
    }

    [string] ToString() {
        $parts = @()
        if (-not $this.IsValid) {
            $parts += "Errors: $($this.Errors.Count)"
        }
        if ($this.Warnings.Count -gt 0) {
            $parts += "Warnings: $($this.Warnings.Count)"
        }
        return "ValidationResult ($($parts -join ', '))"
    }
}

# Основной класс валидации
class InputValidator {
    # Правила для имени репозитория
    static [ValidationResult] ValidateRepoName([string]$Name) {
        $result = [ValidationResult]::new()

        if ([string]::IsNullOrWhiteSpace($Name)) {
            $result.AddError("Repository.Name", "Cannot be null or empty")
            return $result
        }

        # Trim and check length
        $Name = $Name.Trim()

        if ($Name.Length -lt 1) {
            $result.AddError("Repository.Name", "Must be at least 1 character long")
        }
        if ($Name.Length -gt 100) {
            $result.AddError("Repository.Name", "Must be 100 characters or less")
        }

        if ($Name -notmatch '^[a-zA-Z0-9._-]+$') {
            $result.AddError("Repository.Name", "Can only contain letters, numbers, dots (.), underscores (_), and hyphens (-)")
        }

        if ($Name.Contains("..")) {
            $result.AddError("Repository.Name", "Cannot contain '..'")
        }
        if ($Name.Contains("/")) {
            $result.AddError("Repository.Name", "Cannot contain '/'")
        }
        if ($Name.StartsWith(".")) {
            $result.AddError("Repository.Name", "Cannot start with '.'")
        }
        if ($Name.StartsWith("-")) {
            $result.AddError("Repository.Name", "Cannot start with '-'")
        }
        if ($Name.EndsWith(".")) {
            $result.AddError("Repository.Name", "Cannot end with '.'")
        }
        if ($Name.EndsWith("-")) {
            $result.AddError("Repository.Name", "Cannot end with '-'")
        }

        return $result
    }

    # Валидация Azure Subscription ID
    static [ValidationResult] ValidateAzureSubscription([string]$SubscriptionId) {
        $result = [ValidationResult]::new()

        if ([string]::IsNullOrWhiteSpace($SubscriptionId)) {
            $result.AddError("Azure.SubscriptionId", "Cannot be empty")
            return $result
        }

        $guidPattern = '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$'
        if ($SubscriptionId -notmatch $guidPattern) {
            $result.AddError("Azure.SubscriptionId", "Must be a valid GUID")
        }

        return $result
    }

    # Валидация API ключа
    static [ValidationResult] ValidateApiKey([string]$ApiKey, [string]$Provider = "OpenAI") {
        $result = [ValidationResult]::new()
        $provider = $Provider.ToLower().Trim()

        if ([string]::IsNullOrWhiteSpace($ApiKey)) {
            $result.AddError("ApiKey", "Cannot be empty")
            return $result
        }

        switch ($provider) {
            "openai" {
                if ($ApiKey -notmatch '^sk-[a-zA-Z0-9]{48,}$') {
                    $result.AddError("ApiKey", "Invalid OpenAI API key format")
                }
            }
            "anthropic" {
                if ($ApiKey -notmatch '^sk-ant-[a-zA-Z0-9]{48,}$') {
                    $result.AddError("ApiKey", "Invalid Anthropic API key format")
                }
            }
            "azure" {
                if ($ApiKey -notmatch '^[a-zA-Z0-9]{32,}$') {
                    $result.AddError("ApiKey", "Azure API key must be at least 32 alphanumeric characters")
                }
            }
            default {
                if ($ApiKey.Length -lt 16) {
                    $result.AddWarning("ApiKey", "API key is short (<16 chars) — consider using a stronger key")
                }
            }
        }

        return $result
    }

    # Валидация всей конфигурации
    static [ValidationResult] ValidateConfiguration([hashtable]$Config) {
        $result = [ValidationResult]::new()

        if ($null -eq $Config) {
            $result.AddError("Config", "Configuration cannot be null")
            return $result
        }

        # Обязательные секции
        $requiredSections = @("App", "Repository")
        foreach ($section in $requiredSections) {
            if (-not $Config.ContainsKey($section)) {
                $result.AddError("Config.$section", "Missing required section")
            }
        }

        # Проверка уровня логирования
        if ($Config.ContainsKey("Logging") -and $null -ne $Config.Logging) {
            if ($Config.Logging.ContainsKey("Level")) {
                $validLevels = @("DEBUG", "INFO", "WARN", "ERROR", "CRITICAL")
                if ($Config.Logging.Level -notin $validLevels) {
                    $result.AddError("Logging.Level", "Invalid level. Valid: $($validLevels -join ', ')")
                }
            }
        }

        # Проверка таймаутов
        if ($Config.ContainsKey("Performance") -and $null -ne $Config.Performance) {
            if ($Config.Performance.ContainsKey("Timeouts") -and $null -ne $Config.Performance.Timeouts) {
                $timeouts = $Config.Performance.Timeouts
                if ($timeouts.ContainsKey("HttpRequest")) {
                    $value = $timeouts.HttpRequest
                    if ($value -lt 1 -or $value -gt 300) {
                        $result.AddError("Performance.Timeouts.HttpRequest", "Must be between 1 and 300 seconds")
                    }
                }
            }
        }

        # Можно расширить: проверка путей, облачных настроек и т.д.

        return $result
    }
}

# === Экспорт функций (обёртки для удобства CLI) ===

function Test-RepoName {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Name
    )
    $result = [InputValidator]::ValidateRepoName($Name)
    return $result.IsValid
}

function Test-AzureSubscription {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$SubscriptionId
    )
    $result = [InputValidator]::ValidateAzureSubscription($SubscriptionId)
    return $result.IsValid
}

function Test-ApiKey {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Key,
        [string]$Provider = "OpenAI"
    )
    $result = [InputValidator]::ValidateApiKey($Key, $Provider)
    return $result.IsValid
}

function Test-Configuration {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory, ValueFromPipeline)]
        [hashtable]$Config
    )
    process {
        return [InputValidator]::ValidateConfiguration($Config)
    }
}

# Экспортируем все полезные функции
Export-ModuleMember -Function Test-RepoName, Test-AzureSubscription, Test-ApiKey, Test-Configuration
