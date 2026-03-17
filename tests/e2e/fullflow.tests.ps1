# tests/e2e/FullFlow.Tests.ps1
Describe "Arch-Compass End-to-End Tests" -Tag "E2E", "Slow", "RequiresAzure" {
    BeforeAll {
        # Мокаем Get-Command для имитации CLI
        Mock Get-Command {
            param([string]$Name)
            if ($Name -in @('az', 'git', 'python', 'docker')) {
                return [PSCustomObject]@{ Name = $Name; CommandType = 'Application' }
            }
            return & "Get-Command" -Name $Name -ErrorAction SilentlyContinue
        }

        # Импортируем основной скрипт
        $scriptPath = "$PSScriptRoot/../../Initialize-ArchCompass-Ultimate.ps1"
        if (-not (Test-Path $scriptPath)) {
            throw "Main script not found at $scriptPath"
        }
        . $scriptPath
    }

    AfterAll {
        # Гарантируем очистку
        Get-ChildItem $env:TEMP -Directory -Filter "ArchCompass-E2E-*" -ErrorAction SilentlyContinue |
            Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    }

    Context "Repository Initialization" {
        It "Should create a full repository structure" -Timeout 120 {
            # Arrange
            $tempDir = Join-Path $env:TEMP "ArchCompass-E2E-$(Get-Random)"
            $testRepo = "$tempDir/test-init-repo"
            New-Item -ItemType Directory -Path $tempDir -Force

            # Act
            $result = & "$PSScriptRoot/../../Initialize-ArchCompass-Ultimate.ps1" -Command init -RepoName $testRepo -Force

            # Assert
            $result | Should -Not -BeNullOrEmpty
            Test-Path $testRepo | Should -Be $true

            @("src", "tests", "config", "docs", "scripts", ".github") | ForEach-Object {
                Test-Path "$testRepo/$_" | Should -Be $true
            }

            Test-Path "$testRepo/README.md" | Should -Be $true
            Test-Path "$testRepo/.gitignore" | Should -Be $true

            # Cleanup
            Remove-Item $tempDir -Recurse -Force -ErrorAction SilentlyContinue
        }
    }

    Context "Security Validation" {
        It "Should pass security scan on generated repo" -Timeout 180 {
            # Arrange
            $tempDir = Join-Path $env:TEMP "ArchCompass-E2E-$(Get-Random)"
            $testRepo = "$tempDir/test-security-repo"
            New-Item -ItemType Directory -Path $tempDir -Force

            & "$PSScriptRoot/../../Initialize-ArchCompass-Ultimate.ps1" -Command init -RepoName $testRepo -Force

            # Act
            $securityResult = Invoke-SecurityScan -TargetPath $testRepo

            # Assert
            $securityResult | Should -Not -BeNullOrEmpty
            $securityResult.Score | Should -BeGreaterThan 80
            $securityResult.CriticalFindings | Should -Be 0
            $securityResult.Findings | Should -Not -Contain { $_.Severity -eq "Critical" }

            # Cleanup
            Remove-Item $tempDir -Recurse -Force -ErrorAction SilentlyContinue
        }
    }
}
