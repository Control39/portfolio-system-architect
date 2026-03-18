# src/infrastructure/deployment/Cloud.psm1

function Deploy-ToAzure {
    param([string]$ResourceGroup, [string]$SubscriptionId)
    Write-Log "Deploying to Azure..." -Level "INFO"
    $ctx = az account set --subscription $SubscriptionId
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to set Azure subscription"
    }
    Write-Log "Azure deployment simulated" -Level "INFO"
}

Export-ModuleMember -Function Deploy-ToAzure
