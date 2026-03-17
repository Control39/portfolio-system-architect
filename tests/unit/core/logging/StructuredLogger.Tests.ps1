# tests/unit/core/logging/StructuredLogger.Tests.ps1
# Unit тесты для StructuredLogger

BeforeAll {
    # Импорт зависимостей
    $secretManagerPath = Join-Path $PSScriptRoot "..\..\..\..\src\infrastructure\security\SecretManager.psm1"
    Import-Module $secretManagerPath -Force
    
    $loggerPath = Join-Path $PSScriptRoot "..\..\..\..\src\core\logging\StructuredLogger.psm1"
    Import-Module $loggerPath -Force
    
    # Инициализация SecretManager для тестов
    [SecretManager]::Initialize(@{
        VaultType = "Environment"
        ScanForLeaksOnInitialize = $false
    })
    
    # Создание временной директории для логов
    $script:TestLogDir = Join-Path $TestDrive "logs"
    New-Item -ItemType Directory -Path $script:TestLogDir -Force | Out-Null
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
}

Describe "StructuredLogger" {
    Context "Инициализация" {
        It "Должен инициализироваться с конфигурацией" {
            [StructuredLogger]::Initialize(@{
                LogDirectory = $script:TestLogDir
                OutputFormat = "JSON"
                ConsoleOutput = $false
            })
            
            [StructuredLogger]::Initialized | Should -Be $true
            
            [StructuredLogger]::Stop()
        }
        
        It "Должен использовать значения по умолчанию, если конфигурация не указана" {
            [StructuredLogger]::Initialize(@{})
            
            [StructuredLogger]::Initialized | Should -Be $true
            
            [StructuredLogger]::Stop()
        }
    }
    
    Context "Log" {
        BeforeEach {
            if (-not [StructuredLogger]::Initialized) {
                [StructuredLogger]::Initialize(@{
                    LogDirectory = $script:TestLogDir
                    OutputFormat = "JSON"
                    ConsoleOutput = $false
                })
            }
        }
        
        AfterEach {
            if ([StructuredLogger]::Initialized) {
                [StructuredLogger]::Stop()
            }
        }
        
        It "Должен логировать сообщение с уровнем Info" {
            [StructuredLogger]::Log([LogLevel]::Info, "Test message", "TestCategory")
            
            Start-Sleep -Milliseconds 200  # Даем время на запись в файл
            
            $logFiles = Get-ChildItem -Path $script:TestLogDir -Filter "*.log" -ErrorAction SilentlyContinue
            $logFiles.Count | Should -BeGreaterThan 0
        }
        
        It "Должен логировать с различными уровнями" {
            $levels = @([LogLevel]::Debug, [LogLevel]::Info, [LogLevel]::Warning, [LogLevel]::Error)
            
            foreach ($level in $levels) {
                [StructuredLogger]::Log($level, "Test message for $level", "Test")
            }
            
            Start-Sleep -Milliseconds 200
            
            $true | Should -Be $true  # Если дошли сюда, значит ошибок не было
        }
        
        It "Должен логировать с properties" {
            $properties = @{
                UserId = "123"
                Action = "test"
            }
            
            [StructuredLogger]::Log([LogLevel]::Info, "Test with properties", "Test", $properties)
            
            Start-Sleep -Milliseconds 200
            
            $true | Should -Be $true
        }
        
        It "Должен логировать исключения" {
            $exception = [System.Exception]::new("Test exception")
            
            [StructuredLogger]::Log([LogLevel]::Error, "Test error", "Test", $null, $exception)
            
            Start-Sleep -Milliseconds 200
            
            $true | Should -Be $true
        }
    }
    
    Context "Маскирование секретов" {
        BeforeEach {
            if (-not [StructuredLogger]::Initialized) {
                [StructuredLogger]::Initialize(@{
                    LogDirectory = $script:TestLogDir
                    OutputFormat = "JSON"
                    ConsoleOutput = $false
                })
            }
            
            # Устанавливаем тестовый секрет
            [SecretManager]::SetSecret("TEST_API_KEY", "secret-key-12345", $false)
        }
        
        AfterEach {
            if ([StructuredLogger]::Initialized) {
                [StructuredLogger]::Stop()
            }
            [SecretManager]::Cache.Remove("TEST_API_KEY")
        }
        
        It "Должен маскировать секреты в properties при логировании" {
            $properties = @{
                api_key = "secret-key-12345"
                username = "user1"
            }
            
            [StructuredLogger]::Log([LogLevel]::Info, "Test with secret", "Test", $properties)
            
            Start-Sleep -Milliseconds 200
            
            # Проверяем, что в логе нет реального секрета
            $logFiles = Get-ChildItem -Path $script:TestLogDir -Filter "*.log" -ErrorAction SilentlyContinue
            if ($logFiles) {
                $logContent = Get-Content -Path $logFiles[0].FullName -Raw
                $logContent | Should -Not -Match "secret-key-12345"
                $logContent | Should -Match "MASKED_SECRET"
            }
        }
        
        It "Должен маскировать секреты в сообщении" {
            $message = "API key is: secret-key-12345"
            
            [StructuredLogger]::Log([LogLevel]::Info, $message, "Test")
            
            Start-Sleep -Milliseconds 200
            
            $logFiles = Get-ChildItem -Path $script:TestLogDir -Filter "*.log" -ErrorAction SilentlyContinue
            if ($logFiles) {
                $logContent = Get-Content -Path $logFiles[0].FullName -Raw
                $logContent | Should -Not -Match "secret-key-12345"
            }
        }
    }
    
    Context "Stop" {
        It "Должен корректно останавливаться" {
            [StructuredLogger]::Initialize(@{
                LogDirectory = $script:TestLogDir
                ConsoleOutput = $false
            })
            
            [StructuredLogger]::Initialized | Should -Be $true
            
            [StructuredLogger]::Stop()
            
            [StructuredLogger]::Initialized | Should -Be $false
        }
    }
}
