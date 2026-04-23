$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
Import-Module Pester -Force
Import-Module (Join-Path $Here '..\\InfraOrchestrator.psm1') -Force

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    Write-Host "[$Level] $Message"
}

function Run-Tests {
    param([string]$Path, [hashtable]$ConfigOverrides)

    $Config = @{
        Runspace = @{ Culture = 'en-US' }
        Output = @{ Verbosity = 'Detailed' }
        Filter = @{ Tag = '.*' }
    }

    Invoke-Pester -Path $Path -Configuration $Config
    Invoke-SecurityScan  # From SecurityScanner
}

Run-Tests -Path $Here

