function Test-ArchCompassHealth {
    param([switch]$Detailed)

    $checks = @(
        @{
            Name        = 'CoreModules'
            Check       = { Test-Path 'src/core/utilities', 'src/core/validation', 'src/core/logging' }
            Description = 'All core submodules present'
            Severity    = 'Critical'
        },
        @{
            Name        = 'ConfigValidity'
            Check       = {
                $cfg = Get-Content 'config/settings.json' -Raw | ConvertFrom-Json -ErrorAction SilentlyContinue
                $null -ne $cfg
            }
            Description = 'Configuration file is valid JSON'
            Severity    = 'Critical'
        },
        @{
            Name        = 'ContractCompliance'
            Check       = {
                $result = Test-ModuleContract -ModulePath './ArchCompass.psm1' -ContractPath './src/core/contracts/IModule.psd1'
                $result.Passed
            }
            Description = 'Module implements declared contract'
            Severity    = 'High'
        },
        @{
            Name        = 'AiProviderConnection'
            Check       = {
                try {
                    $ai = Get-AiProvider -Name 'OpenAI' -Config @{ ApiKey = 'test' } -ErrorAction Stop
                    Test-Connection -Provider $ai -TimeoutSec 5
                }
                catch { $false }
            }
            Description = 'AI provider endpoint reachable'
            Severity    = 'Medium'
        }
    )

    $results = $checks | ForEach-Object {
        $passed = & $_.Check
        [PSCustomObject]@{
            Check       = $_.Name
            Status      = if ($passed) { '✅ PASS' } else { '❌ FAIL' }
            Description = $_.Description
            Severity    = $_.Severity
            Timestamp   = (Get-Date -Format 'o')
        }
    }

    if ($Detailed) {
        return $results | Format-Table -AutoSize
    }

    $allPassed = ($results | Where-Object { $_.Status -like '*FAIL*' }).Count -eq 0
    return [PSCustomObject]@{
        Healthy      = $allPassed
        TotalChecks  = $checks.Count
        FailedChecks = ($results | Where-Object { $_.Status -like '*FAIL*' }).Count
        Timestamp    = (Get-Date -Format 'o')
    }
}
