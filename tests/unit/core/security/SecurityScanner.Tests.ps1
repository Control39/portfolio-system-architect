# tests/unit/core/security/SecurityScanner.Tests.ps1
# Unit тесты для SecurityScanner

BeforeAll {
    # Импорт зависимостей
    $secretManagerPath = Join-Path $PSScriptRoot "..\..\..\..\src\infrastructure\security\SecretManager.psm1"
    Import-Module $secretManagerPath -Force
    
    $scannerPath = Join-Path $PSScriptRoot "..\..\..\..\src\infrastructure\security\SecurityScanner.psm1"
    Import-Module $scannerPath -Force
    
    # Инициализация SecretManager
    [SecretManager]::Initialize(@{
        VaultType = "Environment"
        ScanForLeaksOnInitialize = $false
    })
    
    # Создание временной структуры проекта для тестов
    $script:TestProjectRoot = Join-Path $TestDrive "test-project"
    New-Item -ItemType Directory -Path $script:TestProjectRoot -Force | Out-Null
    New-Item -ItemType Directory -Path (Join-Path $script:TestProjectRoot ".git") -Force | Out-Null
}

AfterAll {
    if (Test-Path $script:TestProjectRoot) {
        Remove-Item -Path $script:TestProjectRoot -Recurse -Force -ErrorAction SilentlyContinue
    }
}

Describe "SecurityScanner" {
    Context "Invoke-SecurityScan" {
        It "Должен выполнить сканирование без ошибок" {
            $config = @{
                ProjectRoot = $script:TestProjectRoot
                UseExternalTools = $false
            }
            
            $results = [SecurityScanner]::Invoke-SecurityScan($config)
            
            $results | Should -Not -BeNullOrEmpty
        }
        
        It "Должен вернуть предупреждение, если корень проекта не найден" {
            $config = @{
                ProjectRoot = "nonexistent-path-12345"
                UseExternalTools = $false
            }
            
            $results = [SecurityScanner]::Invoke-SecurityScan($config)
            
            $results | Should -Not -BeNullOrEmpty
            $results | Where-Object { $_.Category -eq 'Configuration' } | Should -Not -BeNullOrEmpty
        }
    }
    
    Context "ScanForHardcodedSecrets" {
        It "Должен обнаружить хардкод секрета в файле" {
            # Устанавливаем тестовый секрет
            $testSecretName = "TEST_SECRET_SCAN"
$testSecretValue = (-join ((48..57)+(97..122)|Get-Random -Count 20|%{[char]$_}))
            [SecretManager]::SetSecret($testSecretName, $testSecretValue, $false)
            
            # Создаем файл с хардкод секретом
            $testFile = Join-Path $script:TestProjectRoot "test.psm1"
            Set-Content -Path $testFile -Value "`$apiKey = `"$testSecretValue`""
            
            $config = @{
                ProjectRoot = $script:TestProjectRoot
                UseExternalTools = $false
            }
            
            $results = [SecurityScanner]::Invoke-SecurityScan($config)
            
            $hardcodedResults = $results | Where-Object { $_.Category -eq 'HardcodedSecret' }
            $hardcodedResults.Count | Should -BeGreaterThan 0
            
            # Очистка
            Remove-Item $testFile -Force -ErrorAction SilentlyContinue
            [SecretManager]::Cache.Remove($testSecretName)
        }
    }
    
    Context "CheckGitIgnore" {
        It "Должен обнаружить отсутствие .gitignore" {
            $config = @{
                ProjectRoot = $script:TestProjectRoot
                UseExternalTools = $false
            }
            
            $results = [SecurityScanner]::Invoke-SecurityScan($config)
            
            $gitignoreResults = $results | Where-Object { $_.Category -eq 'GitIgnore' }
            $gitignoreResults | Should -Not -BeNullOrEmpty
        }
        
        It "Должен обнаружить отсутствие паттернов в .gitignore" {
            # Создаем .gitignore без нужных паттернов
            $gitignorePath = Join-Path $script:TestProjectRoot ".gitignore"
            Set-Content -Path $gitignorePath -Value "# Empty gitignore"
            
            $config = @{
                ProjectRoot = $script:TestProjectRoot
                UseExternalTools = $false
            }
            
            $results = [SecurityScanner]::Invoke-SecurityScan($config)
            
            $gitignoreResults = $results | Where-Object { 
                $_.Category -eq 'GitIgnore' -and 
                $_.Message -match 'паттерн'
            }
            $gitignoreResults | Should -Not -BeNullOrEmpty
            
            # Очистка
            Remove-Item $gitignorePath -Force -ErrorAction SilentlyContinue
        }
    }
    
    Context "ScanForSecretPatterns" {
        It "Должен обнаружить потенциальные секреты по паттернам" {
            # Создаем файл с потенциальным секретом
            $testFile = Join-Path $script:TestProjectRoot "config.ps1"
@"
`$api_key = "sk-$(-join ((48..57)+(97..122)|Get-Random -Count 32|%{[char]$_}))"
`$password = "$(-join ((65..90)+(97..122)|Get-Random -Count 12|%{[char]$_}))"
"@
            
            $config = @{
                ProjectRoot = $script:TestProjectRoot
                UseExternalTools = $false
            }
            
            $results = [SecurityScanner]::Invoke-SecurityScan($config)
            
            $patternResults = $results | Where-Object { 
                $_.Category -in @('APIKey', 'Password', 'Secret', 'KnownSecret')
            }
            $patternResults.Count | Should -BeGreaterThan 0
            
            # Очистка
            Remove-Item $testFile -Force -ErrorAction SilentlyContinue
        }
    }
    
    Context "GetScanResults" {
        It "Должен вернуть результаты сканирования" {
            $config = @{
                ProjectRoot = $script:TestProjectRoot
                UseExternalTools = $false
            }
            
            [SecurityScanner]::Invoke-SecurityScan($config) | Out-Null
            
            $results = [SecurityScanner]::GetScanResults()
            
            $results | Should -Not -BeNullOrEmpty
        }
    }
    
    Context "ExportResultsToJson" {
        It "Должен экспортировать результаты в JSON" {
            $config = @{
                ProjectRoot = $script:TestProjectRoot
                UseExternalTools = $false
            }
            
            [SecurityScanner]::Invoke-SecurityScan($config) | Out-Null
            
            $json = [SecurityScanner]::ExportResultsToJson()
            
            $json | Should -Not -BeNullOrEmpty
            $json | Should -Match 'Severity'
            $json | Should -Match 'Category'
        }
    }
}

Describe "Exported Functions" {
    It "Invoke-SecurityScan должна работать" {
        $config = @{
            ProjectRoot = $script:TestProjectRoot
            UseExternalTools = $false
        }
        
        $results = Invoke-SecurityScan -Config $config
        
        $results | Should -Not -BeNullOrEmpty
    }
    
    It "Get-SecurityScanResults должна работать" {
        $results = Get-SecurityScanResults
        
        $results | Should -Not -BeNullOrEmpty
    }
}
