# Pester tests for AiProviderFactory

Import-Module "$PSScriptRoot\..\src\ai\providers\AiProviderFactory.psm1" -Force

Describe "AiProviderFactory" {

    Context "Get-AiProvider" {
        It "должен загрузить OpenAI провайдер" {
            { Get-AiProvider -Name 'OpenAI' -Config @{ ApiKey = 'test' } } | Should -Not -Throw
        }

        It "должен загрузить LocalLLM провайдер" {
            { Get-AiProvider -Name 'LocalLLM' -Config @{ } } | Should -Not -Throw
        }

        It "должен загрузить YandexGPT провайдер" {
            { Get-AiProvider -Name 'YandexGPT' -Config @{ ApiKey = 'test'; FolderId = 'test' } } | Should -Not -Throw
        }

        It "должен выбросить ошибку для несуществующего провайдера" {
            { Get-AiProvider -Name 'InvalidProvider' -Config @{} } | Should -Throw "Provider not found"
        }

        It "должен выбросить ошибку для пустого имени" {
            { Get-AiProvider -Name '' -Config @{} } | Should -Throw
        }
    }

    Context "Provider Validation" {
        BeforeAll {
            $validProviders = @('OpenAI', 'YandexGPT', 'LocalLLM')
        }

        It "должен принимать все валидные провайдеры" {
            foreach ($provider in $validProviders) {
                $config = switch ($provider) {
                    'OpenAI' { @{ ApiKey = 'test' } }
                    'YandexGPT' { @{ ApiKey = 'test'; FolderId = 'test' } }
                    'LocalLLM' { @{} }
                }
                { Get-AiProvider -Name $provider -Config $config } | Should -Not -Throw
            }
        }
    }
}
