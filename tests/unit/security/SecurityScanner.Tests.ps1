# tests/unit/security/SecurityScanner.Tests.ps1

BeforeAll {
    # Путь к модулю
    $ModulePath = "$PSScriptRoot/../../../src/infrastructure/security/SecurityScanner.psm1"
    $ModulePath = Resolve-Path $ModulePath -ErrorAction Stop

    # Тестовая директория
    $TestDir = Join-Path $env:TEMP "security-test-$(Get-Random)"
    $null = New-Item -ItemType Directory -Path $TestDir -Force
    $null = New-Item -ItemType Directory -Path "$TestDir/.git" -Force

    # === Создание тестовых файлов ===

    # Файл с секретами
    @"
password = "super_secret_123"
api_key = "sk-1234567890"
connection_string = "Server=.;Database=test;User=sa;Password=P@ssw0rd!"
auth_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
"@ | Out-File "$TestDir/config.py" -Encoding UTF8

    # .gitignore
    @"
.env
*.log
secrets.json
*.pfx
*.key
"@ | Out-File "$TestDir/.gitignore" -Encoding UTF8

    # Файл, который НЕ в .gitignore
    "SECRET=123" | Out-File "$TestDir/secrets.local" -Encoding UTF8

    # Импорт модуля
    . $ModulePath
}

Describe "SecurityScanner Unit Tests" -Tag "Unit", "Security", "Fast" {
    
    Context "Secret Detection Engine" {
        It "Should detect hardcoded secrets in source files" {
            # Act
            $results = Invoke-SecurityScan -TargetPath $TestDir -ScanForSecrets:$true

            # Assert: есть подозрительные файлы
            $results.SuspiciousFiles | Should -Not -BeNullOrEmpty
            $results.SuspiciousFiles[0].FilePath | Should -Be (Join-Path $TestDir "config.py")
        }

        It "Should categorize findings with correct severity and type" {
            # Act
            $results = Invoke-SecurityScan -TargetPath $TestDir -ScanForSecrets:$true

            # Assert: есть high-severity findings
            $highFindings = $results.Findings | Where-Object { $_.Severity -eq "High" }
            $highFindings | Should -Not -BeNullOrEmpty

            # Проверим структуру одного finding
            $first = $highFindings[0]
            $first | Should -Not -BeNullOrEmpty
            $first.Type | Should -BeIn "API Key", "Password", "Connection String", "JWT"
            $first.LineNumber | Should -BeGreaterThan 0
            $first.FilePath | Should -Match "\.py$"
        }
    }

    Context ".gitignore Analysis" {
        It "Should identify files missing from .gitignore" {
            # Act
            $results = Invoke-SecurityScan -TargetPath $TestDir -CheckGitignore:$true

            # Assert
            $results.GitignoreIssues | Should -Not -BeNullOrEmpty
            $results.GitignoreIssues[0].FilePath | Should -Be (Join-Path $TestDir "secrets.local")
            $results.GitignoreIssues[0].Recommendation | Should -Match "Add to .gitignore"
        }
    }

    Context "External Tools Integration" {
        It "Should gracefully handle missing external tools" {
            # Arrange: мокаем Get-Command
            Mock Get-Command {
                param([string]$Name)
                if ($Name -in @('bandit', 'gitleaks', 'safety')) {
                    return $null  # имитируем отсутствие
                }
                return & "Get-Command" -Name $Name -ErrorAction SilentlyContinue
            }

            # Act
            $results = Invoke-SecurityScan -TargetPath $TestDir -RunExternalTools:$true

            # Assert
            $results.ExternalToolResults | Should -BeNullOrEmpty
            $results.Warnings | Where-Object { $_.Message -match "bandit|gitleaks" } | Should -Not -BeNullOrEmpty
        }

        It "Should capture results when external tools are available" {
            # Arrange: мокаем внешние инструменты
            Mock Get-Command {
                param([string]$Name)
                if ($Name -in @('bandit', 'gitleaks')) {
                    return [PSCustomObject]@{ Name = $Name; CommandType = 'Application' }
                }
                return & "Get-Command" -Name $Name -ErrorAction SilentlyContinue
            }

            Mock Invoke-Expression {
                param([string]$Command)
                if ($Command -match "bandit") {
                    return '{
                        "results": [
                            { "issue_severity": "HIGH", "filename": "config.py", "line_number": 2 }
                        ]
                    }'
                }
                if ($Command -match "gitleaks") {
                    return '[{"description": "API Key", "severity": "high"}]'
                }
                return ""
            } -Verifiable

            # Act
            $results = Invoke-SecurityScan -TargetPath $TestDir -RunExternalTools:$true

            # Assert
            $results.ExternalToolResults.Bandit.Findings | Should -Not -BeNullOrEmpty
            $results.ExternalToolResults.Gitleaks.Findings | Should -Not -BeNullOrEmpty

            Assert-VerifiableMock
        }
    }

    Context "Scan Configuration" {
        It "Should respect scan flags" {
            # Act: только .gitignore, без секретов
            $results = Invoke-SecurityScan -TargetPath $TestDir -ScanForSecrets:$false -CheckGitignore:$true

            # Assert
            $results.Findings | Should -BeNullOrEmpty
            $results.GitignoreIssues | Should -Not -BeNullOrEmpty
        }
    }
}

AfterAll {
    # Очистка
    if (Test-Path $TestDir) {
        Remove-Item -Path $TestDir -Recurse -Force -ErrorAction SilentlyContinue
    }

    # Удаляем моки
    Remove-Item Function:\Get-Command -ErrorAction SilentlyContinue
}
