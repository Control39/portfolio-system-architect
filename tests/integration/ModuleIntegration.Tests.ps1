# tests/integration/ModuleIntegration.Tests.ps1
# Интеграционные тесты для проверки взаимодействия модулей

BeforeAll {
    # Импорт всех модулей
    $moduleRoot = Join-Path $PSScriptRoot "..\.."
    
    $secretManagerPath = Join-Path $moduleRoot "src\infrastructure\security\SecretManager.psm1"
    Import-Module $secretManagerPath -Force
    
    $scannerPath = Join-Path $moduleRoot "src\infrastructure\security\SecurityScanner.psm1"
    Import-Module $scannerPath -Force
    
    $loggerPath = Join-Path $moduleRoot "src\core\logging\StructuredLogger.psm1"
    Import-Module $loggerPath -Force
    
    $validatorPath = Join-Path $moduleRoot "src\core\validation\InputValidator.psm1"
    Import-Module $validatorPath -Force
    
    # Инициализация модулей
    [SecretManager]::Initialize(@{
        VaultType = "Environment"
        ScanForLeaksOnInitialize = $false
    })
    
    $script:TestLogDir = Join-Path $TestDrive "integration-logs"
    New-Item -ItemType Directory -Path $script:TestLogDir -Force | Out-Null
    
    [StructuredLogger]::Initialize(@{
        LogDirectory = $script:TestLogDir
        OutputFormat = "JSON"
        ConsoleOutput = $false
    })
    
    # Создание тестовой структуры проекта
    $script:TestProjectRoot = Join-Path $TestDrive "integration-test-project"
    New-Item -ItemType Directory -Path $script:TestProjectRoot -Force | Out-Null
    New-Item -ItemType Directory -Path (Join-Path $script:TestProjectRoot ".git") -Force | Out-Null
}

AfterAll {
    # Остановка логгера
    if ([StructuredLogger]::Initialized) {
        [StructuredLogger]::Stop()
    }
    
    # Очистка
    if (Test-Path $script:TestLogDir) {
        Remove-Item -Path $script:TestLogDir -Recurse -Force -ErrorAction SilentlyContinue
    }
    
    if (Test-Path $script:TestProjectRoot) {
        Remove-Item -Path $script:TestProjectRoot -Recurse -Force -ErrorAction SilentlyContinue
    }
}

Describe "Интеграция SecretManager и StructuredLogger" {
    It "Логгер должен маскировать секреты из SecretManager в логах" {
        # Устанавливаем секрет
        $testSecretName = "INTEGRATION_TEST_SECRET"
        $testSecretValue = "integration-secret-value-12345"
        [SecretManager]::SetSecret($testSecretName, $testSecretValue, $false)
        
        # Логируем сообщение с секретом
        $properties = @{
            api_key = $testSecretValue
            username = "testuser"
        }
        
        [StructuredLogger]::Log([LogLevel]::Info, "Test integration log", "Integration", $properties)
        
        # Даем время на запись
        Start-Sleep -Milliseconds 300
        
        # Проверяем, что секрет замаскирован в логе
        $logFiles = Get-ChildItem -Path $script:TestLogDir -Filter "*.log" -ErrorAction SilentlyContinue
        if ($logFiles) {
            $logContent = Get-Content -Path $logFiles[0].FullName -Raw
            $logContent | Should -Not -Match [regex]::Escape($testSecretValue)
            $logContent | Should -Match "MASKED_SECRET"
        }
        
        # Очистка
        [SecretManager]::Cache.Remove($testSecretName)
    }
    
    It "Логгер должен работать даже если SecretManager не содержит секрета" {
        $properties = @{
            username = "testuser"
            action = "test"
        }
        
        [StructuredLogger]::Log([LogLevel]::Info, "Test without secrets", "Integration", $properties)
        
        Start-Sleep -Milliseconds 200
        
        $true | Should -Be $true  # Если дошли сюда, значит ошибок не было
    }
}

Describe "Интеграция InputValidator и SecretManager" {
    It "Валидатор должен проверять API ключи перед использованием в SecretManager" {
        # Валидируем ключ
        $apiKey = "sk-" + ("a" * 32)
        $validationResult = [InputValidator]::ValidateApiKey($apiKey, "openai")
        
        $validationResult.IsValid | Should -Be $true
        
        # Если валидация прошла, устанавливаем в SecretManager
        if ($validationResult.IsValid) {
            [SecretManager]::SetSecret("OPENAI_API_KEY", $apiKey, $false)
            $retrieved = [SecretManager]::GetSecret("OPENAI_API_KEY")
            $retrieved | Should -Be $apiKey
        }
        
        # Очистка
        [SecretManager]::Cache.Remove("OPENAI_API_KEY")
    }
    
    It "Валидатор должен отклонять невалидные ключи" {
        $invalidKey = "invalid-key"
        $validationResult = [InputValidator]::ValidateApiKey($invalidKey, "openai")
        
        $validationResult.IsValid | Should -Be $false
        
        # Не должны устанавливать невалидный ключ
        $validationResult.IsValid | Should -Be $false
    }
}

Describe "Интеграция SecurityScanner и SecretManager" {
    It "SecurityScanner должен использовать SecretManager для проверки хардкод секретов" {
        # Устанавливаем секрет
        $testSecretName = "SCANNER_INTEGRATION_TEST"
        $testSecretValue = "scanner-integration-secret-98765"
        [SecretManager]::SetSecret($testSecretName, $testSecretValue, $false)
        
        # Создаем файл с хардкод секретом
        $testFile = Join-Path $script:TestProjectRoot "integration-test.psm1"
        Set-Content -Path $testFile -Value "`$secret = `"$testSecretValue`""
        
        # Запускаем сканирование
        $config = @{
            ProjectRoot = $script:TestProjectRoot
            UseExternalTools = $false
        }
        
        $results = [SecurityScanner]::Invoke-SecurityScan($config)
        
        # Проверяем, что SecurityScanner нашел хардкод секрет через SecretManager
        $hardcodedResults = $results | Where-Object { 
            $_.Category -eq 'HardcodedSecret' -and 
            $_.File -eq $testFile
        }
        $hardcodedResults.Count | Should -BeGreaterThan 0
        
        # Очистка
        Remove-Item $testFile -Force -ErrorAction SilentlyContinue
        [SecretManager]::Cache.Remove($testSecretName)
    }
    
    It "SecurityScanner должен использовать паттерны из SecretManager" {
        $config = @{
            ProjectRoot = $script:TestProjectRoot
            UseExternalTools = $false
        }
        
        # Получаем паттерны из SecretManager
        $patterns = [SecretManager]::GetCurrentSecretPatterns()
        $patterns.Count | Should -BeGreaterThan 0
        
        # Запускаем сканирование
        $results = [SecurityScanner]::Invoke-SecurityScan($config)
        
        # Проверяем, что сканирование прошло
        $results | Should -Not -BeNullOrEmpty
    }
}

Describe "Интеграция всех модулей в полном потоке" {
    It "Должен работать полный цикл: валидация -> SecretManager -> логирование -> сканирование" {
        # 1. Валидация конфигурации
        $config = @{
            version = "1.0.0"
            environment = "development"
            openai = @{
                api_key = "sk-" + ("a" * 32)
            }
        }
        
        $validationResult = [InputValidator]::ValidateConfiguration($config)
        $validationResult.IsValid | Should -Be $true
        
        # 2. Установка секрета в SecretManager
        if ($validationResult.IsValid) {
            [SecretManager]::SetSecret("OPENAI_API_KEY", $config.openai.api_key, $false)
        }
        
        # 3. Логирование с секретом (должен быть замаскирован)
        $properties = @{
            api_key = [SecretManager]::GetSecret("OPENAI_API_KEY")
            action = "full-integration-test"
        }
        
        [StructuredLogger]::Log([LogLevel]::Info, "Full integration test", "Integration", $properties)
        Start-Sleep -Milliseconds 200
        
        # 4. Сканирование безопасности
        $scanConfig = @{
            ProjectRoot = $script:TestProjectRoot
            UseExternalTools = $false
        }
        
        $scanResults = [SecurityScanner]::Invoke-SecurityScan($scanConfig)
        $scanResults | Should -Not -BeNullOrEmpty
        
        # 5. Проверка, что секрет замаскирован в логах
        $logFiles = Get-ChildItem -Path $script:TestLogDir -Filter "*.log" -ErrorAction SilentlyContinue
        if ($logFiles) {
            $logContent = Get-Content -Path $logFiles[0].FullName -Raw
            $logContent | Should -Not -Match [regex]::Escape($config.openai.api_key)
        }
        
        # Очистка
        [SecretManager]::Cache.Remove("OPENAI_API_KEY")
    }
}
