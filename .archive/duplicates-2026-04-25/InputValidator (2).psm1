function Test-RepoName {
    param([string]$Name)
    return $Name -match '^[a-zA-Z0-9_.-]+$'
}
Export-ModuleMember -Function Test-RepoName
