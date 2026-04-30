Import-Module (Resolve-Path "$PSScriptRoot\..\..\src\core\security\SecretManager.psm1") -Force

Describe 'SecretManager' {
    It 'Initializes without error' {
        $mgr = [SecretManager]::new()
        $mgr | Should -Not -BeNullOrEmpty
    }

    It 'Gets environment secret' -Pending {
        $value = [SecretManager]::GetSecret('TEST_SECRET', 'default')
        $value | Should -Be 'default'
    }
}
