# Pester tests for LocalLlmProvider

Import-Module "$PSScriptRoot\..\src\ai\providers\LocalLlmProvider.psm1" -Force

Describe "LocalLlmProvider" {
    
    Context "Initialize-Provider" {
        It "должен инициализировать провайдер с кастомным endpoint" {
            { Initialize-Provider -Endpoint "http://localhost:11434" -Model "llama3" } | Should -Not -Throw
        }
        
        It "должен использовать дефолтные значения без параметров" {
            { Initialize-Provider } | Should -Not -Throw
        }
    }
    
    Context "Get-ProviderInfo" {
        It "должен возвращать информацию о локальном провайдере" {
            Initialize-Provider
            $info = Get-ProviderInfo
            
            $info.Name | Should -Be "LocalLLM"
            $info.SupportsCompletion | Should -BeTrue
            $info.SupportsEmbeddings | Should -BeTrue
            $info.Offline | Should -BeTrue
            $info.Privacy | Should -Be "All data stays local"
        }
    }
    
    Context "Test-Connection" {
        It "должен вернуть false при недоступном endpoint" {
            # Тестируем с заведомо недоступным endpoint
            Initialize-Provider -Endpoint "http://localhost:9999"
            Test-Connection -TimeoutSec 2 | Should -BeFalse
        }
    }
    
    Context "Invoke-Completion" {
        It "должен выбрасывать ошибку при недоступном сервисе" {
            Initialize-Provider -Endpoint "http://localhost:9999"
            { Invoke-Completion -Prompt "test" } | Should -Throw "LocalLLM API call failed"
        }
    }
    
    Context "Invoke-Embedding" {
        It "должен выбрасывать ошибку при недоступном сервисе" {
            Initialize-Provider -Endpoint "http://localhost:9999"
            { Invoke-Embedding -Text "test" } | Should -Throw "LocalLLM Embedding API call failed"
        }
    }
}
