Import-Module -Force ./InfraOrchestrator.psm1

Describe 'InfraOrchestrator Functions' {
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
