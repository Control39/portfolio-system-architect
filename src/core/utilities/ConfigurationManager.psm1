# src/core/configuration/ConfigurationManager.psm1

class ConfigurationManager {
    hidden static [hashtable] $Instance = $null
    hidden static [hashtable] $Configuration = @{}

    static [ConfigurationManager] GetInstance() {
        if (-not [ConfigurationManager]::Instance) {
            [ConfigurationManager]::Instance = [ConfigurationManager]::new()
        }
        return [ConfigurationManager]::Instance
    }

    [void] Initialize([string]$environment = "default") {
        Write-Host "🔧 Инициализация конфигурации для окружения: $environment" -ForegroundColor Cyan

        # Базовая конфигурация
        [ConfigurationManager]::Configuration = @{
            version = "1.0.0"
            environment = $environment
            openai = @{
                api_key = ""
                model = "gpt-4"
            }
            logging = @{
                level = "Info"
                output = "Console"
            }
            security = @{
                enable_scanning = $true
                vault_type = "Environment"
            }
            Paths = @{
                Source = './src'
                Artifacts = './artifacts'
            }
            Features = @{
                AIEnabled = $true
                SecurityScan = $true
            }
        }

        Write-Host "✅ Конфигурация инициализирована" -ForegroundColor Green
    }

    [hashtable] GetConfig() {
        return [ConfigurationManager]::Configuration
    }

    [object] GetValue([string]$key, [object]$defaultValue = $null) {
        $keys = $key -split '\.'
        $current = [ConfigurationManager]::Configuration

        foreach ($k in $keys) {
            if ($current -is [hashtable] -and $current.ContainsKey($k)) {
                $current = $current[$k]
            } else {
                return $defaultValue
            }
        }

        return $current
    }

    [void] SetValue([string]$key, [object]$value) {
        $keys = $key -split '\.', 0, 'RegexMatch'
        $current = [ConfigurationManager]::Configuration
        for ($i = 0; $i -lt $keys.Length - 1; $i++) {
            $k = $keys[$i]
            if (-not $current.ContainsKey($k)) {
                $current[$k] = @{}
            }
            $current = $current[$k]
        }
        $current[$keys[-1]] = $value
    }
}

Export-ModuleMember -Variable ConfigurationManager
