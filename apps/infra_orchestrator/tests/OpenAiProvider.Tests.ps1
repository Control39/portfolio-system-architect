# Pester tests for OpenAiProvider

Import-Module "$PSScriptRoot\..\src\ai\providers\OpenAiProvider.psm1" -Force

Describe "OpenAiProvider" {

    Context "Initialize-Provider" {
        It "должен инициализировать провайдер с ключом" {
            { Initialize-Provider -ApiKey "test-key-123" -Model "gpt-4" } | Should -Not -Throw
        }

        It "должен выбрасывать ошибку без ключа" {
            { Initialize-Provider } | Should -Throw
        }

        It "должен использовать дефолтные значения" {
            { Initialize-Provider -ApiKey "test-key" } | Should -Not -Throw
            $info = Get-ProviderInfo
            $info.Model | Should -Be "gpt-4o"
        }
    }

    Context "Get-ProviderInfo" {
        It "должен возвращать информацию о провайдере после инициализации" {
            Initialize-Provider -ApiKey "test-key"
            $info = Get-ProviderInfo

            $info.Name | Should -Be "OpenAI"
            $info.SupportsCompletion | Should -BeTrue
            $info.SupportsEmbeddings | Should -BeTrue
            $info.RateLimit | Should -Be "30000 requests/minute (enterprise)"
        }
    }

    Context "Test-Connection" {
        It "должен вернуть false без ключа" {
            $script:config = @{}
            Test-Connection | Should -BeFalse
        }

        It "должен вернуть false при неверном ключе" {
            Initialize-Provider -ApiKey "invalid-key"
            Test-Connection -TimeoutSec 3 | Should -BeFalse
        }
    }

    Context "Invoke-Completion" {
        It "должен выбрасывать ошибку без инициализации" {
            $script:config = @{}
            { Invoke-Completion -Prompt "test" } | Should -Throw "OpenAI API key not set"
        }

        It "должен выбрасывать ошибку при неверном ключе" {
            Initialize-Provider -ApiKey "invalid-key"
            { Invoke-Completion -Prompt "test" } | Should -Throw "OpenAI API call failed"
        }
    }

    Context "Invoke-Embedding" {
        It "должен выбрасывать ошибку без инициализации" {
            $script:config = @{}
            { Invoke-Embedding -Text "test" } | Should -Throw "OpenAI API key not set"
        }

        It "должен выбрасывать ошибку при неверном ключе" {
            Initialize-Provider -ApiKey "invalid-key"
            { Invoke-Embedding -Text "test" } | Should -Throw "OpenAI Embedding API call failed"
        }
    }
}
