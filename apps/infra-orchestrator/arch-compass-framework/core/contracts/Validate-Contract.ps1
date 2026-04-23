function Test-ModuleContract {
    param(
        [string]$ModulePath,
        [string]$ContractPath
    )
    
    $contract = Import-PowerShellDataFile -Path $ContractPath
    $moduleInfo = Get-Module -ListAvailable -Name $ModulePath
    
    $results = @()
    foreach ($func in $contract.FunctionsToExport) {
        $exists = Get-Command -Name $func -Module $moduleInfo.Name -ErrorAction SilentlyContinue
        $results += [PSCustomObject]@{
            Function    = $func
            Implemented = ($null -ne $exists)
            Status      = if ($exists) { '✅' } else { '❌' }
        }
    }
    
    $allPassed = ($results | Where-Object { -not $_.Implemented }).Count -eq 0
    return [PSCustomObject]@{
        Module   = $moduleInfo.Name
        Contract = $contract.ModuleName
        Passed   = $allPassed
        Details  = $results
    }
}