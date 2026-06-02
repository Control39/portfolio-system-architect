# src/core/configuration/ConfigurationManager.psm1

class ConfigurationManager {
    static [ConfigurationManager] $Instance = $null
    [hashtable] $Configuration

    ConfigurationManager() {
        $this.Configuration = @{
            App = @{
                Language = "en-US"
            }
            Repository = @{
                DefaultName = "arch-compass-system"
            }
            Cloud = @{
                Provider = "azure"
                Azure = @{
                    SubscriptionId = $null
                    ResourceGroup = "arch-rg"
                }
            }
            AI = @{
                Enabled = $false
                OpenAI = @{
                    ApiKey = $null
                    Model = "gpt-4"
                }
            }
            Security = @{
                ScanForSecrets = $true
                RunExternalTools = $false
                Vault = @{ Type = "Environment" }
                Cache = @{ TTLSeconds = 300 }
            }
            Monitoring = @{
                Prometheus = @{ PushgatewayUrl = $null }
            }
        }
    }

    static [ConfigurationManager] GetInstance() {
        if (-not [ConfigurationManager]::$Instance) {
            [ConfigurationManager]::$Instance = [ConfigurationManager]::new()
        }
        return [ConfigurationManager]::$Instance
    }

    [void] LoadConfiguration([string]$Path = "") {
        if ($Path -and (Test-Path $Path)) {
            $json = Get-Content $Path -Raw | ConvertFrom-Json -AsHashtable
            $this.MergeConfig($this.Configuration, $json)
        }
    }

    [void] SetValue([string]$Key, $Value) {
        $keys = $Key -split '\.'
        $current = $this.Configuration
        for ($i = 0; $i -lt $keys.Length - 1; $i++) {
            if (-not $current.ContainsKey($keys[$i])) {
                $current[$keys[$i]] = @{}
            }
            $current = $current[$keys[$i]]
        }
        $current[$keys[-1]] = $Value
    }

    $Value GetValue([string]$Key, $Default = $null) {
        $keys = $Key -split '\.'
        $current = $this.Configuration
        foreach ($k in $keys) {
            if ($current -and $current.ContainsKey($k)) {
                $current = $current[$k]
            } else {
                return $Default
            }
        }
        return $current
    }

    hidden [void] MergeConfig([hashtable]$Target, [hashtable]$Source) {
        foreach ($key in $Source.Keys) {
            if ($Source[$key] -is [hashtable] -and $Target[$key] -is [hashtable]) {
                $this.MergeConfig($Target[$key], $Source[$key])
            } else {
                $Target[$key] = $Source[$key]
            }
        }
    }
}

Export-ModuleMember -Class ConfigurationManager
