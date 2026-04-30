function Deploy-ToAzure {
    param([string]$ResourceGroup)
    # Deploy stub
    Write-Output "Deployed to $ResourceGroup"
}

Export-ModuleMember -Function Deploy-ToAzure
