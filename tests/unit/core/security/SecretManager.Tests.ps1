# tests/unit/core/security/SecretManager.Tests.ps1
# Unit тесты для SecretManager

BeforeAll {
    # Импорт модуля
    $modulePath = Join-Path $PSScriptRoot "..\..\..\..\src\infrastructure\security\SecretManager.psm1"
    Import-Module $modulePath -Force
    
    # Очистка кэша перед тестами
    [SecretManager]::Cache.Clear()
}

Describe "SecretManager" {
    Context "Инициализация" {
        It "Должен инициализироваться с конфигурацией" {
            [SecretManager]::Initialize(@{
                VaultType = "Environment"
                CacheTTL = 1800
            })
            
            # Проверка, что инициализация прошла без ошибок
            $true | Should -Be $true
        }
    }
    
    Context "GetSecret" {
        BeforeEach {
            [SecretManager]::Cache.Clear()
        }
        
        It "Должен получить секрет из переменной окружения" {
            $testSecretName = "TEST_SECRET_$(Get-Random)"
            $testSecretValue = "test-value-123"
            
            [Environment]::SetEnvironmentVariable($testSecretName, $testSecretValue, "Process")
            
            $result = [SecretManager]::GetSecret($testSecretName)
            
            $result | Should -Be $testSecretValue
            
            # Очистка
            [Environment]::SetEnvironmentVariable($testSecretName, $null, "Process")
        }
        
        It "Должен использовать значение по умолчанию, если секрет не найден" {
            $testSecretName = "NONEXISTENT_SECRET_$(Get-Random)"
            $defaultValue = "default-value"
            
            $result = [SecretManager]::GetSecret($testSecretName, $defaultValue)
            
            $result | Should -Be $defaultValue
        }
        
        It "Должен кэшировать секрет после первого получения" {
            $testSecretName = "CACHE_TEST_$(Get-Random)"
            $testSecretValue = "cached-value"
            
            [Environment]::SetEnvironmentVariable($testSecretName, $testSecretValue, "Process")
            
            # Первое получение
            $result1 = [SecretManager]::GetSecret($testSecretName)
            
            # Удаляем из окружения
            [Environment]::SetEnvironmentVariable($testSecretName, $null, "Process")
            
            # Второе получение должно вернуть из кэша
            $result2 = [SecretManager]::GetSecret($testSecretName)
            
            $result2 | Should -Be $testSecretValue
            
            # Очистка
            [SecretManager]::Cache.Remove($testSecretName)
        }
    }
    
    Context "SetSecret" {
        It "Должен установить секрет в кэш" {
            $testSecretName = "SET_TEST_$(Get-Random)"
            $testSecretValue = "set-value"
            
            [SecretManager]::SetSecret($testSecretName, $testSecretValue, $false)
            
            $cached = [SecretManager]::GetSecret($testSecretName)
            $cached | Should -Be $testSecretValue
            
            # Очистка
            [SecretManager]::Cache.Remove($testSecretName)
        }
    }
    
    Context "MaskSecret" {
        It "Должен замаскировать секрет в строке" {
            $secretValue = "my-secret-key-12345"
            $text = "API key is: $secretValue"
            
            $masked = [SecretManager]::MaskSecret($text, $secretValue)
            
            $masked | Should -Match '^\*\*\*MASKED_SECRET\*\*\*$' -Not
            $masked | Should -Not -Match [regex]::Escape($secretValue)
            $masked | Should -Match '\*\*\*MASKED_SECRET\*\*\*'
        }
        
        It "Должен вернуть исходную строку, если секрет не найден" {
            $text = "No secrets here"
            $secretValue = "nonexistent"
            
            $masked = [SecretManager]::MaskSecret($text, $secretValue)
            
            $masked | Should -Be $text
        }
    }
    
    Context "MaskSecretsInObject" {
        It "Должен замаскировать секреты в hashtable" {
            $secretValue = "secret-password-123"
            [SecretManager]::SetSecret("TEST_PASSWORD", $secretValue, $false)
            
            $obj = @{
                username = "user1"
                password = $secretValue
                api_key = "key-123"
            }
            
            $masked = [SecretManager]::MaskSecretsInObject($obj)
            
            $masked.password | Should -Be "***MASKED_SECRET***"
            $masked.api_key | Should -Be "***MASKED_SECRET***"
            $masked.username | Should -Be "user1"
            
            # Очистка
            [SecretManager]::Cache.Remove("TEST_PASSWORD")
        }
        
        It "Должен замаскировать секреты в строке" {
            $secretValue = "my-secret"
            [SecretManager]::SetSecret("TEST_SECRET", $secretValue, $false)
            
            $text = "Secret is: $secretValue"
            
            $masked = [SecretManager]::MaskSecretsInObject($text)
            
            $masked | Should -Not -Match [regex]::Escape($secretValue)
            
            # Очистка
            [SecretManager]::Cache.Remove("TEST_SECRET")
        }
    }
    
    Context "CheckForHardcodedSecrets" {
        It "Должен обнаружить хардкод секрета в файле" {
            $testSecretName = "HARDCODED_TEST_$(Get-Random)"
            $testSecretValue = "hardcoded-secret-value-12345"
            
            [SecretManager]::SetSecret($testSecretName, $testSecretValue, $false)
            
            # Создаем временный файл с хардкод секретом
            $tempFile = [System.IO.Path]::GetTempFileName()
            Set-Content -Path $tempFile -Value "api_key = `"$testSecretValue`""
            
            $violations = [SecretManager]::CheckForHardcodedSecrets(@($tempFile))
            
            $violations.Count | Should -BeGreaterThan 0
            $violations[0].SecretName | Should -Be $testSecretName
            
            # Очистка
            Remove-Item $tempFile -Force
            [SecretManager]::Cache.Remove($testSecretName)
        }
        
        It "Не должен находить секреты в файле без хардкода" {
            $tempFile = [System.IO.Path]::GetTempFileName()
            Set-Content -Path $tempFile -Value "api_key = `"some-other-value`""
            
            $violations = [SecretManager]::CheckForHardcodedSecrets(@($tempFile))
            
            $violations.Count | Should -Be 0
            
            # Очистка
            Remove-Item $tempFile -Force
        }
    }
    
    Context "RotateSecret" {
        It "Должен успешно ротировать секрет" {
            $testSecretName = "ROTATE_TEST_$(Get-Random)"
            $oldValue = "old-secret"
            $newValue = "new-secret"
            
            [SecretManager]::SetSecret($testSecretName, $oldValue, $false)
            
            $result = [SecretManager]::RotateSecret($testSecretName, $newValue)
            
            $result | Should -Be $true
            
            $retrieved = [SecretManager]::GetSecret($testSecretName)
            $retrieved | Should -Be $newValue
            
            # Очистка
            [SecretManager]::Cache.Remove($testSecretName)
        }
    }
    
    Context "GetCurrentSecretPatterns" {
        It "Должен вернуть список известных паттернов секретов" {
            $patterns = [SecretManager]::GetCurrentSecretPatterns()
            
            $patterns | Should -Not -BeNullOrEmpty
            $patterns.Count | Should -BeGreaterThan 0
        }
    }
}
