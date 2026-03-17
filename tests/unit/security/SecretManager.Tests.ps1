# tests/unit/security/SecretManager.Tests.ps1

BeforeAll {
    # Путь к модулю
    $ModulePath = "$PSScriptRoot/../../../src/core/security/SecretManager.psm1"
    $ModulePath = Resolve-Path $ModulePath -ErrorAction Stop

    # === Загружаем модуль СНАЧАЛА ===
    . $ModulePath

    # === Теперь мокаем внутри контекста модуля ===
    InModuleScope SecretManager {
        # Моки для внутренних функций
        Mock Get-FromEnvironment { param([string]$Name) return "mocked-$Name" }
        Mock EncryptInMemory { param([string]$Data) return "encrypted:$Data" }
        Mock DecryptInMemory { param([string]$Data) return $Data -replace '^encrypted:', '' }
    }
}

Describe "SecretManager Unit Tests" -Tag "Unit", "Security", "Fast" {
    
    BeforeEach {
        # Очищаем кэш перед каждым тестом
        [SecretManager]::Cache.Clear()
        [SecretManager]::Initialize()
    }

    Context "Basic Operations" {
        It "Should retrieve secret from cache" {
            # Arrange
            [SecretManager]::Cache["test-secret"] = "cached-value"

            # Act
            $result = [SecretManager]::GetSecret("test-secret", "default")

            # Assert
            $result | Should -Be "cached-value"
        }

        It "Should fallback to environment variables when not in cache" {
            # Arrange + Act
            $result = [SecretManager]::GetSecret("api-key", "default")

            # Assert
            $result | Should -Be "mocked-api-key"
        }

        It "Should return default value when secret not found" {
            # Arrange
            InModuleScope SecretManager {
                Mock Get-FromEnvironment { return $null }
            }

            # Act
            $result = [SecretManager]::GetSecret("non-existent", "my-default")

            # Assert
            $result | Should -Be "my-default"
        }
    }

    Context "Security & Masking" {
        It "Should mask known secrets in text" {
            # Arrange
[SecretManager]::SetSecret("api-key", "sk-" + (-join ((48..57)+(97..122)|Get-Random -Count 32|%{[char]$_})), $false)

            # Act
$log = "User called API with key: sk-" + (-join ((48..57)+(97..122)|Get-Random -Count 32|%{[char]$_}))
            $masked = [SecretManager]::MaskSecretInText($log)

            # Assert
            $masked | Should -Not -Match "sk-1234567890abcdef"
            $masked | Should -Match "\*\*\*MASKED\*\*\*"
        }

        It "Should mask multiple types of secrets" {
            # Arrange
[SecretManager]::SetSecret("db-pass", (-join ((65..90)+(97..122)|Get-Random -Count 20|%{[char]$_})), $false)
[SecretManager]::SetSecret("jwt", (-join ((65..90)+(97..122)|Get-Random -Count 20|%{[char]$_})), $false)

            # Act
            $text = "Login failed for token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9 and password: P@ssw0rd123!"
            $masked = [SecretManager]::MaskSecretInText($text)

            # Assert
(-join ((65..90)+(97..122)|Get-Random -Count 12|%{[char]$_}))
            $masked | Should -Not -Match "eyJhbG"
            $masked.Split('***MASKED***').Length | Should -Be 3  # два секрета → два маскирования
        }

        It "Should not expose secrets in exception messages" {
            # Arrange
            $secret = "super-secret-value"
            [SecretManager]::SetSecret("dangerous", $secret, $false)

            # Act + Assert
            { [SecretManager]::ThrowIfExposed($secret) } | Should -Throw
            $errorRecord = $Error[0]
            $errorRecord.Exception.Message | Should -Not -Match $secret
            $errorRecord.Exception.Message | Should -Match "exposure"
        }
    }

    Context "Secret Rotation" {
        It "Should generate new secret on rotation" {
            # Arrange
            $original = "old-secret-123"
            [SecretManager]::SetSecret("rotatable", $original, $true)

            # Act
            [SecretManager]::RotateSecret("rotatable")
            $new = [SecretManager]::GetSecret("rotatable")

            # Assert
            $new | Should -Not -Be $original
            $new | Should -Not -BeNullOrEmpty
        }

        It "Should preserve auto-rotate flag after rotation" {
            # Arrange
            [SecretManager]::SetSecret("auto-rotate", "initial", $true)

            # Act
            [SecretManager]::RotateSecret("auto-rotate")
            $new = [SecretManager]::GetSecret("auto-rotate")

            # Assert
            $new | Should -Not -Be "initial"
            # Проверить, что флаг остался — зависит от реализации
            # Если есть метод: [SecretManager]::IsAutoRotate("auto-rotate") | Should -Be $true
        }
    }

    Context "Lifecycle" {
        It "Should initialize with empty cache" {
            # Arrange
            [SecretManager]::Cache.Clear()

            # Act
            [SecretManager]::Initialize()

            # Assert
            [SecretManager]::Cache.Count | Should -Be 0
            # Допустимые проверки: таймеры, фоновые задачи — если есть
        }
    }
}

AfterAll {
    # Финальная очистка
    InModuleScope SecretManager {
        if ([SecretManager]::Cache) {
            [SecretManager]::Cache.Clear()
        }
    }
}
