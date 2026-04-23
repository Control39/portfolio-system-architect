# Pester tests for YandexGptProvider

Import-Module "$PSScriptRoot\..\src\ai\providers\YandexGptProvider.psm1" -Force

Describe "YandexGptProvider" {
    
    Context "Initialize-Provider" {
        It "должен инициализировать провайдер с ключом и folderId" {
            { Initialize-Provider -ApiKey "test-key" -FolderId "test-folder" } | Should -Not -Throw
        }
        
        It "должен выбрасывать ошибку без ApiKey" {
            { Initialize-Provider -FolderId "test-folder" } | Should -Throw
        }
        
        It "должен выбрасывать ошибку без FolderId" {
            { Initialize-Provider -ApiKey "test-key" } | Should -Throw
        }
    }
    
    Context "Get-ProviderInfo" {
        It "должен возвращать информацию о YandexGPT провайдере" {
            Initialize-Provider -ApiKey "test-key" -FolderId "test-folder"
            $info = Get-ProviderInfo
            
            $info.Name | Should -Be "YandexGPT"
            $info.SupportsCompletion | Should -BeTrue
            $info.SupportsEmbeddings | Should -BeFalse
            $info.Region | Should -Be "Russia (Yandex Cloud)"
            $info.Compliance | Should -Be "152-FZ compliant"
        }
    }
    
    Context "Test-Connection" {
        It "должен вернуть false без ключа" {
            $script:config = @{}
            Test-Connection | Should -BeFalse
        }
        
        It "должен вернуть false при неверном ключе" {
            Initialize-Provider -ApiKey "invalid-key" -FolderId "invalid-folder"
            Test-Connection -TimeoutSec 3 | Should -BeFalse
        }
    }
    
    Context "Invoke-Completion" {
        It "должен выбрасывать ошибку без инициализации" {
            $script:config = @{}
            { Invoke-Completion -Prompt "test" } | Should -Throw "YandexGPT API key not set"
        }
        
        It "должен выбрасывать ошибку при неверном ключе" {
            Initialize-Provider -ApiKey "invalid-key" -FolderId "invalid-folder"
            { Invoke-Completion -Prompt "test" } | Should -Throw "YandexGPT API call failed"
        }
    }
    
    Context "Invoke-Embedding" {
        It "должен выводить предупреждение о недоступности embeddings" {
            Initialize-Provider -ApiKey "test-key" -FolderId "test-folder"
            { Invoke-Embedding -Text "test" } | Should -WarnvMessage *not available*
        }
    }
}
