class ConfigurationManager {
    static [ConfigurationManager] $Instance
    static [ConfigurationManager] GetInstance() {
        if (-not [ConfigurationManager]::Instance) {
            [ConfigurationManager]::Instance = [ConfigurationManager]::new()
        }
        return [ConfigurationManager]::Instance
    }
}
Export-ModuleMember -Class ConfigurationManager
