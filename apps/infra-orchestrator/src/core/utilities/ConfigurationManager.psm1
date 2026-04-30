function Get-Configuration {
    param([string]$Path = 'config/default.yaml')
    # Load YAML config
    if (Test-Path $Path) { Get-Content $Path | ConvertFrom-Yaml } else { @{ } }
}

Export-ModuleMember -Function Get-Configuration
