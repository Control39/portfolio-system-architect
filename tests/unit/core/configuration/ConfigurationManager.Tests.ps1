Import-Module (Resolve-Path "$PSScriptRoot\..\..\src\core\configuration\ConfigurationManager.psm1") -Force

Describe 'ConfigurationManager' {
    BeforeAll {
        # Load module
        $global:ConfigMgr = [ConfigurationManager]::GetInstance()
    }

    Context 'Instance Management' {
        It 'Returns singleton instance' {
            $instance1 = [ConfigurationManager]::GetInstance()
            $instance2 = [ConfigurationManager]::GetInstance()
            $instance1 | Should -Be $instance2
        }
    }

    Context 'Default Configuration' {
        It 'Has expected default values' {
            $lang = $global:ConfigMgr.GetValue('App.Language')
            $lang | Should -Be 'en-US'
            
            $provider = $global:ConfigMgr.GetValue('Cloud.Provider')
            $provider | Should -Be 'azure'
        }
        
        It 'Handles non-existent keys with default' {
            $value = $global:ConfigMgr.GetValue('Non.Existent', 'default')
            $value | Should -Be 'default'
        }
    }

    Context 'SetValue and GetValue' {
        It 'Sets and gets simple value' {
            $global:ConfigMgr.SetValue('Test.Key', 'value')
            $value = $global:ConfigMgr.GetValue('Test.Key')
            $value | Should -Be 'value'
        }
        
        It 'Sets nested value' {
            $global:ConfigMgr.SetValue('Test.Nested.Sub', 42)
            $value = $global:ConfigMgr.GetValue('Test.Nested.Sub')
            $value | Should -Be 42
        }
    }

    Context 'LoadConfiguration' {
        It 'Loads JSON config' -Pending {
            # Create temp JSON
            $tempJson = "$env:TEMP\test-config.json"
            $testConfig = @{
                App = @{ Language = 'ru-RU' }
                Test = @{ Value = 'loaded' }
            } | ConvertTo-Json -Depth 10
            $testConfig | Out-File $tempJson -Encoding UTF8
            
            $global:ConfigMgr.LoadConfiguration($tempJson)
            $lang = $global:ConfigMgr.GetValue('App.Language')
            $lang | Should -Be 'ru-RU'
            
            Remove-Item $tempJson -Force
        }
    }
}
