# tests/unit/core/validation/InputValidator.Tests.ps1
# Unit тесты для InputValidator

BeforeAll {
    $modulePath = Join-Path $PSScriptRoot "..\..\..\..\src\core\validation\InputValidator.psm1"
    Import-Module $modulePath -Force
}

Describe "InputValidator" {
    Context "ValidateRepoName" {
        It "Должен принять валидное имя репозитория" {
            $result = [InputValidator]::ValidateRepoName("my-repo-123")
            
            $result.IsValid | Should -Be $true
            $result.Errors.Count | Should -Be 0
        }
        
        It "Должен отклонить пустое имя" {
            $result = [InputValidator]::ValidateRepoName("")
            
            $result.IsValid | Should -Be $false
            $result.Errors.Count | Should -BeGreaterThan 0
        }
        
        It "Должен отклонить слишком короткое имя" {
            $result = [InputValidator]::ValidateRepoName("ab")
            
            $result.IsValid | Should -Be $false
            $result.Errors | Should -Contain "Имя репозитория должно содержать минимум 3 символа"
        }
        
        It "Должен отклонить слишком длинное имя" {
            $longName = "a" * 101
            $result = [InputValidator]::ValidateRepoName($longName)
            
            $result.IsValid | Should -Be $false
            $result.Errors | Should -Contain "Имя репозитория не должно превышать 100 символов"
        }
        
        It "Должен отклонить имя с недопустимыми символами" {
            $result = [InputValidator]::ValidateRepoName("my-repo@123")
            
            $result.IsValid | Should -Be $false
            $result.Errors | Should -Contain "Имя репозитория может содержать только буквы, цифры, дефисы и подчеркивания"
        }
        
        It "Должен предупредить, если имя начинается с цифры" {
            $result = [InputValidator]::ValidateRepoName("123repo")
            
            $result.Warnings.Count | Should -BeGreaterThan 0
            $result.Warnings | Should -Contain "Имя репозитория не должно начинаться с цифры"
        }
        
        It "Должен отклонить зарезервированные имена Windows" {
            $result = [InputValidator]::ValidateRepoName("con")
            
            $result.IsValid | Should -Be $false
            $result.Errors | Should -Contain "Имя репозитория не может быть зарезервированным именем Windows"
        }
    }
    
    Context "ValidateAzureSubscription" {
        It "Должен принять валидный GUID" {
            $validGuid = "12345678-1234-1234-1234-123456789012"
            $result = [InputValidator]::ValidateAzureSubscription($validGuid)
            
            $result.IsValid | Should -Be $true
        }
        
        It "Должен отклонить пустой Subscription ID" {
            $result = [InputValidator]::ValidateAzureSubscription("")
            
            $result.IsValid | Should -Be $false
        }
        
        It "Должен отклонить не-GUID формат" {
            $result = [InputValidator]::ValidateAzureSubscription("not-a-guid")
            
            $result.IsValid | Should -Be $false
            $result.Errors | Should -Contain "Subscription ID должен быть в формате GUID"
        }
    }
    
    Context "ValidateApiKey" {
        It "Должен принять валидный OpenAI API ключ" {\n            $validKey = "sk-" + (-join ((48..57)+(97..122)|Get-Random -Count 32|%{[char]$_}))\n            $result = [InputValidator]::ValidateApiKey($validKey, "openai")
            
            $result.IsValid | Should -Be $true
        }
        
        It "Должен отклонить OpenAI ключ без префикса sk-" {
"test-$(-join ((97..122)|Get-Random -Count 10|%{[char]$_}))"
            $result = [InputValidator]::ValidateApiKey($invalidKey, "openai")
            
            $result.IsValid | Should -Be $false
        }
        
        It "Должен отклонить слишком короткий ключ" {
            $shortKey = "short"
            $result = [InputValidator]::ValidateApiKey($shortKey)
            
            $result.IsValid | Should -Be $false
            $result.Errors | Should -Contain "API ключ слишком короткий"
        }
        
        It "Должен отклонить ключ только из цифр" {
            $numericKey = "12345678901234567890"
            $result = [InputValidator]::ValidateApiKey($numericKey)
            
            $result.IsValid | Should -Be $false
            $result.Errors | Should -Contain "API ключ не должен состоять только из цифр или только из букв"
        }
        
        It "Должен отклонить пустой ключ" {
            $result = [InputValidator]::ValidateApiKey("")
            
            $result.IsValid | Should -Be $false
        }
    }
    
    Context "ValidateConfiguration" {
        It "Должен принять валидную конфигурацию" {
            $config = @{\n                version = "1.0.0"\n                environment = "development"\n                openai = @{\n                    api_key = "sk-" + (-join ((48..57)+(97..122)|Get-Random -Count 32|%{[char]$_}))\n                    model = "gpt-4"
                }
            }
            
            $result = [InputValidator]::ValidateConfiguration($config)
            
            $result.IsValid | Should -Be $true
        }
        
        It "Должен отклонить конфигурацию без обязательных полей" {
            $config = @{
                openai = @{}
            }
            
            $result = [InputValidator]::ValidateConfiguration($config)
            
            $result.IsValid | Should -Be $false
            $result.Errors | Should -Contain "Отсутствует обязательное поле: version"
        }
        
        It "Должен отклонить невалидную версию" {
            $config = @{
                version = "invalid"
                environment = "development"
            }
            
            $result = [InputValidator]::ValidateConfiguration($config)
            
            $result.IsValid | Should -Be $false
            $result.Errors | Should -Contain "Версия должна быть в формате X.Y.Z"
        }
        
        It "Должен предупредить о неизвестном окружении" {
            $config = @{
                version = "1.0.0"
                environment = "unknown-env"
            }
            
            $result = [InputValidator]::ValidateConfiguration($config)
            
            $result.Warnings.Count | Should -BeGreaterThan 0
        }
        
        It "Должен отклонить null конфигурацию" {
            $result = [InputValidator]::ValidateConfiguration($null)
            
            $result.IsValid | Should -Be $false
            $result.Errors | Should -Contain "Конфигурация не может быть null"
        }
    }
    
    Context "ValidateUrl" {
        It "Должен принять валидный URL" {
            $result = [InputValidator]::ValidateUrl("https://example.com")
            
            $result.IsValid | Should -Be $true
        }
        
        It "Должен отклонить пустой URL" {
            $result = [InputValidator]::ValidateUrl("")
            
            $result.IsValid | Should -Be $false
        }
        
        It "Должен отклонить относительный URL" {
            $result = [InputValidator]::ValidateUrl("/path/to/resource")
            
            $result.IsValid | Should -Be $false
        }
        
        It "Должен отклонить URL с недопустимым протоколом" {
            $result = [InputValidator]::ValidateUrl("ftp://example.com")
            
            $result.IsValid | Should -Be $false
        }
    }
}

Describe "Exported Functions" {
    It "Test-RepoName должна работать" {
        $result = Test-RepoName "valid-repo-name"
        $result | Should -Be $true
    }
    
    It "Test-AzureSubscription должна работать" {
        $validGuid = "12345678-1234-1234-1234-123456789012"
        $result = Test-AzureSubscription $validGuid
        $result | Should -Be $true
    }
    
    It "Test-ApiKey должна работать" {
        $validKey = "sk-" + ("a" * 32)
        $result = Test-ApiKey $validKey "openai"
        $result | Should -Be $true
    }
}
