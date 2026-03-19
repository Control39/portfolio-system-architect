Import-Module (Resolve-Path "$PSScriptRoot\..\..\src\core\logging\StructuredLogger.psm1") -Force

Describe 'StructuredLogger' {
    It 'Logs info message' {
        $log = [StructuredLogger]::new()
        { $log.Info('Test message', @{key='value'}) } | Should -Not -Throw
    }
    
    It 'Has expected structure' {
        # Mock Write-Output or file
        # Test JSON structure
        $result = $log.Log('Test', 'INFO', @{data=1})
        $result | Should -Not -BeNullOrEmpty
    }
}
