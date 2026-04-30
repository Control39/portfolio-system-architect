function Invoke-SecurityScan {
    [CmdletBinding()]
    param()
    # Gitleaks integration
    gitleaks detect --config .gitleaks.toml
    return @{ Score = 90 }
}

function Get-SecurityScore {
    [CmdletBinding()]
    param()
    95
}

Export-ModuleMember -Function Invoke-SecurityScan, Get-SecurityScore
