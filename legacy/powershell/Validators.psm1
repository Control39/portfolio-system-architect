# src/core/validation/Validators.psm1

function Test-Dependencies {
    param(
        [string[]]$Commands,
        [hashtable]$ConditionalChecks = @{}
    )
    foreach ($cmd in $Commands) {
        if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) {
            Write-Log "Required command not found: $cmd" -Level "ERROR"
            return $false
        }
    }
    foreach ($check in $ConditionalChecks.Keys) {
        $test = $ConditionalChecks[$check]
        if (-not (& $test)) {
            Write-Log "Conditional check failed: $check" -Level "ERROR"
            return $false
        }
    }
    return $true
}

Export-ModuleMember -Function Test-Dependencies
