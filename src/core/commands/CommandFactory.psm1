# src/core/commands/CommandFactory.psm1

using module ../../../src/core/logging/StructuredLogger
using module ../../../src/core/validation/InputValidator

class CommandFactory {
    static [hashtable] $Commands = @{}

    # Регистрация команды
    static [void] RegisterCommand([string]$Name, [scriptblock]$Action, [hashtable]$Metadata = @{}) {
        [CommandFactory]::Commands[$Name] = @{
            Action   = $Action
            Metadata = $Metadata
        }
    }

    # Выполнение команды
    static [object] ExecuteCommand([string]$Name, [hashtable]$Parameters) {
        if (-not [CommandFactory]::Commands.ContainsKey($Name)) {
            $msg = "Command '$Name' not found. Available: $([CommandFactory]::GetCommands())"
            [StructuredLogger]::Log($msg, "ERROR", @{ Command = $Name })
            throw $msg
        }

        $command = [CommandFactory]::Commands[$Name]
        [StructuredLogger]::Log("Executing command: $Name", "INFO", @{ Parameters = $Parameters.Keys })

        try {
            $result = & $command.Action $Parameters
            [StructuredLogger]::Log("Command succeeded: $Name", "INFO")
            return $result
        }
        catch {
            [StructuredLogger]::Log("Command failed: $Name", "ERROR", @{ Error = $_.Exception.Message })
            throw
        }
    }

    # Получить список команд
    static [string[]] GetCommands() {
        return [CommandFactory]::Commands.Keys | Sort-Object
    }

    # Проверить, существует ли команда
    static [bool] HasCommand([string]$Name) {
        return [CommandFactory]::Commands.ContainsKey($Name)
    }
}

# === Регистрация команд ===

[CommandFactory]::RegisterCommand("init", {
        param([hashtable]$Config)

        if (-not (Test-RepoName -Name $Config.Repository.Name)) {
            throw "Invalid repository name: $($Config.Repository.Name)"
        }

        [StructuredLogger]::Log("Initializing repository: $($Config.Repository.Name)", "INFO")
        # Логика инициализации репозитория
        # ...
        return @{ Status = "Initialized"; Name = $Config.Repository.Name }
    }, @{
        Description = "Initialize a new Arch-Compass project"
        Usage       = "init -Config @{ Repository = @{ Name = 'my-app' } }"
    })

[CommandFactory]::RegisterCommand("deploy", {
        param([hashtable]$Config)

        $provider = $Config.Cloud.Provider
        if (-not [CommandFactory]::HasCommand("deploy-$provider")) {
            throw "Unsupported cloud provider: $provider"
        }

        [StructuredLogger]::Log("Deploying to $provider", "INFO")
        # Логика деплоя
        return @{ Status = "Deployed"; Provider = $provider }
    }, @{
        Description = "Deploy infrastructure to cloud"
        Usage       = "deploy -Config @{ Cloud = @{ Provider = 'azure' } }"
    })
