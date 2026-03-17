# tests/integration/EndToEnd.Tests.ps1
Describe "Arch-Compass Integration Tests" -Tag "Integration", "Slow" {
    BeforeAll {
        # Импорт модулей
        $srcPath = "$PSScriptRoot/../../src"

        Import-Module "$srcPath/core/logging/StructuredLogger.psm1" -Force
        Import-Module "$srcPath/core/security/SecretManager.psm1" -Force
        Import-Module "$srcPath/core/validation/InputValidator.psm1" -Force

        # Тестовый корень
        $TestRoot = Join-Path $env:TEMP "arch-compass-integration-$(Get-Date -Format 'yyyyMMddHHmmss')"
        $LogDir = Join-Path $TestRoot "logs"
        $SecretStore = Join-Path $TestRoot "secrets.json"

        New-Item -ItemType Directory -Path $TestRoot, $LogDir -Force

        # Инициализация
        [StructuredLogger]::Initialize(@{ LogDirectory = $LogDir })
        [SecretManager]::Initialize(@{ StorePath = $SecretStore })
    }

    Context "Module Integration" {
        It "Should integrate SecretManager with StructuredLogger without leaking secrets" {
            # Arrange
            [SecretManager]::SetSecret("test-key", "test-value", $false)

            # Act
            # Логируем только ключ, а не значение
            [StructuredLogger]::Log("Accessing secret", "INFO", @{ SecretKey = "test-key" })

            # Assert: убеждаемся, что значение не в логах
            $logFile = Get-ChildItem "$LogDir/*.log" -ErrorAction SilentlyContinue | Select-Object -First 1
            $logContent = if ($logFile) { Get-Content $logFile -Raw } else { "" }

            $logContent | Should -Not -Match "test-value"
            $logContent | Should -Match "test-key"
        }

        It "Should validate input before processing" {
            # Arrange + Act + Assert
            Test-RepoName -Name "valid-repo-name" | Should -Be $true
            Test-RepoName -Name "my-app" | Should -Be $true

            { Test-RepoName -Name "../invalid" } | Should -Throw
            { Test-RepoName -Name "invalid|name" } | Should -Throw
            { Test-RepoName -Name "" } | Should -Throw
        }
    }

    Context "Security Integration" {
        It "Should detect and mask secrets in generated files" -Tag "Security" {
            # Arrange
            $testFile = Join-Path $TestRoot "test-config.json"
            $secret = "sk-1234567890abcdef"

            @"
{
    "api_key": "$secret",
    "password": "P@ssw0rd123"
}
"@ | Out-File $testFile -Encoding utf8

            # Act
            $scanResult = Invoke-SecurityScan -TargetPath $TestRoot -ScanForSecrets:$true

            # Assert
            $scanResult.Findings.Count | Should -BeGreaterThan 0
            ($scanResult.Findings | Where-Object { $_.Type -eq "API Key" }).Count | Should -BeGreaterThan 0

            # Логируем результат сканирования (без прямого значения)
            [StructuredLogger]::Log("Security scan completed", "WARN", @{
                File = $testFile
                IssueCount = $scanResult.Findings.Count
                SampleType = $scanResult.Findings[0].Type
            })

            $logFile = Get-ChildItem "$LogDir/*.log" | Select-Object -First 1 -ErrorAction SilentlyContinue
            $logContent = if ($logFile) { Get-Content $logFile -Raw } else { "" }

            # Ensure no raw secret leaked
            $logContent | Should -Not -Match $secret
        }
    }

    AfterAll {
        # Очистка
        [StructuredLogger]::Stop()
        Remove-Item -Path $TestRoot -Recurse -Force -ErrorAction SilentlyContinue
    }
}
