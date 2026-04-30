# src/core/validation/InputValidator.psm1
# InputValidator - валидация входных данных

class ValidationResult {
    [bool] $IsValid
    [string[]] $Errors
    [string[]] $Warnings

    ValidationResult([bool]$isValid, [string[]]$errors = @(), [string[]]$warnings = @()) {
        $this.IsValid = $isValid
        $this.Errors = $errors
        $this.Warnings = $warnings
    }
}

class InputValidator {
    # Валидация имени репозитория
    static [ValidationResult] ValidateRepoName([string]$repoName) {
        $errors = @()
        $warnings = @()

        if ([string]::IsNullOrWhiteSpace($repoName)) {
            $errors += "Имя репозитория не может быть пустым"
            return [ValidationResult]::new($false, $errors)
        }

        # Длина
        if ($repoName.Length -lt 3) {
            $errors += "Имя репозитория должно содержать минимум 3 символа"
        }

        if ($repoName.Length -gt 100) {
            $errors += "Имя репозитория не должно превышать 100 символов"
        }

        # Паттерн: буквы, цифры, дефисы, подчеркивания
        if ($repoName -notmatch '^[a-zA-Z0-9_-]+$') {
            $errors += "Имя репозитория может содержать только буквы, цифры, дефисы и подчеркивания"
        }

        # Запрещенные имена
        $forbiddenNames = @('con', 'prn', 'aux', 'nul', 'com1', 'com2', 'com3', 'com4', 'com5', 'com6', 'com7', 'com8', 'com9', 'lpt1', 'lpt2', 'lpt3', 'lpt4', 'lpt5', 'lpt6', 'lpt7', 'lpt8', 'lpt9')
        if ($forbiddenNames -contains $repoName.ToLower()) {
            $errors += "Имя репозитория не может быть зарезервированным именем Windows"
        }

        # Предупреждения
        if ($repoName -match '^[0-9]') {
            $warnings += "Имя репозитория не должно начинаться с цифры"
        }

        if ($repoName -match '[-_]$') {
            $warnings += "Имя репозитория не должно заканчиваться дефисом или подчеркиванием"
        }

        return [ValidationResult]::new($errors.Count -eq 0, $errors, $warnings)
    }

    # Валидация Azure Subscription ID
    static [ValidationResult] ValidateAzureSubscription([string]$subscriptionId) {
        $errors = @()

        if ([string]::IsNullOrWhiteSpace($subscriptionId)) {
            $errors += "Subscription ID не может быть пустым"
            return [ValidationResult]::new($false, $errors)
        }

        # GUID формат
        $guidPattern = '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$'
        if ($subscriptionId -notmatch $guidPattern) {
            $errors += "Subscription ID должен быть в формате GUID (например: 12345678-1234-1234-1234-123456789012)"
        }

        return [ValidationResult]::new($errors.Count -eq 0, $errors)
    }

    # Валидация API ключа
    static [ValidationResult] ValidateApiKey([string]$apiKey, [string]$provider = '') {
        $errors = @()

        if ([string]::IsNullOrWhiteSpace($apiKey)) {
            $errors += "API ключ не может быть пустым"
            return [ValidationResult]::new($false, $errors)
        }

        # Минимальная длина
        if ($apiKey.Length -lt 10) {
            $errors += "API ключ слишком короткий (минимум 10 символов)"
        }

        # Проверка формата в зависимости от провайдера
        switch ($provider.ToLower()) {
            'openai' {
                if ($apiKey -notmatch '^sk-[a-zA-Z0-9]{32,}$') {
                    $errors += "OpenAI API ключ должен начинаться с 'sk-' и содержать минимум 32 символа"
                }
            }
            'anthropic' {
                if ($apiKey -notmatch '^sk-ant-[a-zA-Z0-9\-_]{95,}$') {
                    $errors += "Anthropic API ключ должен начинаться с 'sk-ant-' и содержать минимум 95 символов"
                }
            }
            'azure' {
                if ($apiKey.Length -lt 32) {
                    $errors += "Azure API ключ должен содержать минимум 32 символа"
                }
            }
        }

        # Проверка на потенциально слабый ключ (только цифры или только буквы)
        if ($apiKey -match '^[0-9]+$' -or $apiKey -match '^[a-zA-Z]+$') {
            $errors += "API ключ не должен состоять только из цифр или только из букв"
        }

        return [ValidationResult]::new($errors.Count -eq 0, $errors)
    }

    # Валидация конфигурации
    static [ValidationResult] ValidateConfiguration([hashtable]$config) {
        $errors = @()
        $warnings = @()

        if (-not $config) {
            $errors += "Конфигурация не может быть null"
            return [ValidationResult]::new($false, $errors)
        }

        # Обязательные поля
        $requiredFields = @('version', 'environment')
        foreach ($field in $requiredFields) {
            if (-not $config.ContainsKey($field)) {
                $errors += "Отсутствует обязательное поле: $field"
            }
        }

        # Валидация версии
        if ($config.ContainsKey('version')) {
            $version = $config.version
            if ($version -notmatch '^\d+\.\d+\.\d+$') {
                $errors += "Версия должна быть в формате X.Y.Z (например: 1.0.0)"
            }
        }

        # Валидация окружения
        if ($config.ContainsKey('environment')) {
            $validEnvironments = @('development', 'staging', 'production', 'default')
            if ($validEnvironments -notcontains $config.environment) {
                $warnings += "Неизвестное окружение: $($config.environment). Рекомендуемые: $($validEnvironments -join ', ')"
            }
        }

        # Валидация OpenAI конфигурации
        if ($config.ContainsKey('openai')) {
            $openaiConfig = $config.openai
            if ($openaiConfig -is [hashtable]) {
                if ($openaiConfig.ContainsKey('api_key') -and $openaiConfig.api_key) {
                    $apiKeyResult = [InputValidator]::ValidateApiKey($openaiConfig.api_key, 'openai')
                    if (-not $apiKeyResult.IsValid) {
                        $errors += "OpenAI API ключ невалиден: $($apiKeyResult.Errors -join ', ')"
                    }
                }
            }
        }

        return [ValidationResult]::new($errors.Count -eq 0, $errors, $warnings)
    }

    # Валидация URL
    static [ValidationResult] ValidateUrl([string]$url) {
        $errors = @()

        if ([string]::IsNullOrWhiteSpace($url)) {
            $errors += "URL не может быть пустым"
            return [ValidationResult]::new($false, $errors)
        }

        try {
            $uri = [System.Uri]::new($url)
            if (-not $uri.IsAbsoluteUri) {
                $errors += "URL должен быть абсолютным"
            }
            if ($uri.Scheme -notin @('http', 'https')) {
                $errors += "URL должен использовать протокол http или https"
            }
        } catch {
            $errors += "Некорректный формат URL: $_"
        }

        return [ValidationResult]::new($errors.Count -eq 0, $errors)
    }
}

# Экспорт функций для использования в скриптах
function Test-RepoName {
    param(
        [Parameter(Mandatory = $true)]
        [string]$RepoName
    )

    $result = [InputValidator]::ValidateRepoName($RepoName)
    return $result.IsValid
}

function Test-AzureSubscription {
    param(
        [Parameter(Mandatory = $true)]
        [string]$SubscriptionId
    )

    $result = [InputValidator]::ValidateAzureSubscription($SubscriptionId)
    return $result.IsValid
}

function Test-ApiKey {
    param(
        [Parameter(Mandatory = $true)]
        [string]$ApiKey,

        [string]$Provider = ''
    )

    $result = [InputValidator]::ValidateApiKey($ApiKey, $Provider)
    return $result.IsValid
}

Export-ModuleMember -Function Test-RepoName, Test-AzureSubscription, Test-ApiKey
