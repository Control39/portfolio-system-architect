Import-Module (Resolve-Path "$PSScriptRoot\..\..\src\core\commands\CLI.psm1") -Force

Describe 'CLI Commands' {
    It 'Shows help' {
        $result = Show-Help
        $result | Should -Match 'usage'
    }
}
