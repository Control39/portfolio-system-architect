function Initialize-GitRepo {
    param([string]$Path)
    Set-Location $Path
    git init
}

function Get-ChangeReport {
    git status --short
}

Export-ModuleMember -Function Initialize-GitRepo, Get-ChangeReport

