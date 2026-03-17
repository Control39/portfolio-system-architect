# src/core/configuration/ConfigurationManager.psm1

class ConfigurationManager {
    hidden static [ConfigurationManager] $Instance = $null
    [hashtable] $Configuration

    ConfigurationManager() {
        $this.Configuration = $this.GetDefaultConfiguration()
    }

    static [ConfigurationManager] GetInstance() {
        if (-not [ConfigurationManager]::$Instance) {
            [ConfigurationManager]::$Instance = [ConfigurationManager]::new()
        }
        return [ConfigurationManager]::$Instance
    }

    [void] LoadConfiguration([string]$Path = "") {
        if ($Path -and (Test-Path $Path)) {
            try {
                $json = Get-Content -Path $Path -Raw -Encoding UTF8
                $customConfig = ConvertFrom-Json -InputObject $json -AsHashtable -ErrorAction Stop
                $this.MergeHash($this.Configuration, $customConfig)
            } catch {
                Write-Warning "Failed to load config from $Path: $_"
            }
        }
    }

    [void] SetValue([string]$Key, $Value) {
        $keys = $Key -split '\.'
        $current = $this.Configuration
        for ($i = 0; $i -lt $keys.Length - 1; $i++) {
            $key = $keys[$i]
            if (-not $current.ContainsKey($key)) {
                $current[$key] = @{}
            }
            $current = $current[$key]
        }
        $current[$keys[-1]] = $Value
    }

    $Value GetValue([string]$Key, $Default = $null) {
        $keys = $Key -split '\.'
        $current = $this.Configuration
        foreach ($key in $keys) {
            if ($current -is [hashtable] -and $current.ContainsKey($key)) {
                $current = $current[$key]
            } else {
                return $Default
            }
        }
        return $current
    }

    hidden [void] MergeHash([hashtable]$Target, [hashtable]$Source) {
        foreach ($key in $Source.Keys) {
            if ($Source[$key] -is [hashtable] -and $Target[$key] -is [hashtable]) {
                $this.MergeHash($Target[$key], $Source[$key])
            } else {
                $Target[$key] = $Source[$key]
            }
        }
    }

    hidden [hashtable] GetDefaultConfiguration() {
        return @{
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
                Vault = @{ Type = "Environment"; CacheTTL = 300 }
            }
            Monitoring = @{
                Prometheus = @{ PushgatewayUrl = $null }
            }
        }
    }
}

Export-ModuleMember -Class ConfigurationManager
