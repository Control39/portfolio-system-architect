class SecretManager {
    static [hashtable] $Cache = @{}
    static [string] GetSecret([string]$key) {
        return [SecretManager]::Cache[$key]
    }
}
Export-ModuleMember -Class SecretManager
