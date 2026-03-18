# src/infrastructure/git/GitHelper.psm1

function Initialize-GitRepo {
    param([string]$Path)
    if (Test-Path "$Path/.git") {
        Write-Log "Git repo already exists in $Path" -Level "INFO"
        return
    }
    git -C $Path init
    git -C $Path add .
    git -C $Path commit -m "Initial commit by Arch-Compass"
    Write-Log "Git repo initialized" -Level "INFO"
}

Export-ModuleMember -Function Initialize-GitRepo
