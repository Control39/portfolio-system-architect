Import-Module -Force ./ArchCompass.psm1

Describe 'ArchCompass Functions' {
    It 'Tests Get-ArchPattern' {
        $result = Get-ArchPattern -Name 'Microservices'
        $result | Should -Not -BeNullOrEmpty
    }
    # Add tests for all exported functions
    It 'Throws on invalid pattern' {
        { Get-ArchPattern -Name 'Invalid' } | Should -Throw
    }
}

# Run with Invoke-Pester this file

