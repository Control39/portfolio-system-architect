# arch.ps1
param(
    [Parameter(Mandatory)]
    [ValidateSet("init", "deploy", "analyze", "report", "test", "logs", "score")]
    [string]$Command,

    [string]$RepoName,
    [string]$ConfigFile,
    [ValidateSet("azure")]
    [string]$CloudProvider,
    [string]$SubscriptionId,
    [string]$ResourceGroup,
    [switch]$InteractiveAI = $false,
    [ValidateSet("en-US", "ru-RU")]
    [string]$Language = "en-US",
    [switch]$RunSecurityTests,
    [switch]$Help
)

# Показать помощь
if ($Help) {
    Write-Host @"
🚀 Arch-Compass — Automated Architecture Scaffolding

Usage:
  arch.ps1 <command> [options]

Commands:
  init        Initialize a new project
  deploy      Deploy infrastructure
  analyze     Analyze codebase
  report      Generate security report
  test        Run tests
  logs        Show logs
  score       Get security score

Examples:
  arch.ps1 init -RepoName "my-app" -Language "en-US"
  arch.ps1 deploy -CloudProvider azure -SubscriptionId "xxxx"
  arch.ps1 test -RunSecurityTests
"@
    exit 0
}

# Определяем путь к модулю
$ModulePath = $MyInvocation.MyCommand.Path | Split-Path | Join-Path -ChildPath "ArchCompass.psd1"
if (-not (Test-Path $ModulePath)) {
    Write-Error "ArchCompass module not found. Expected at: $ModulePath"
    exit 1
}

# Импортируем модуль
Import-Module $ModulePath -Force

# Передаём параметры в Main
$mainParams = @{}
if ($PSBoundParameters.ContainsKey("RepoName")) { $mainParams.RepoName = $RepoName }
if ($PSBoundParameters.ContainsKey("ConfigFile")) { $mainParams.ConfigFile = $ConfigFile }
if ($PSBoundParameters.ContainsKey("CloudProvider")) { $mainParams.CloudProvider = $CloudProvider }
if ($PSBoundParameters.ContainsKey("SubscriptionId")) { $mainParams.SubscriptionId = $SubscriptionId }
if ($PSBoundParameters.ContainsKey("ResourceGroup")) { $mainParams.ResourceGroup = $ResourceGroup }
if ($InteractiveAI) { $mainParams.InteractiveAI = $true }
if ($PSBoundParameters.ContainsKey("Language")) { $mainParams.Language = $Language }
if ($RunSecurityTests) { $mainParams.RunSecurityTests = $true }

try {
    switch ($Command) {
        "test" {
            $testType = if ($RunSecurityTests) { "All" } else { "Unit" }
            & "$PSScriptRoot/tests/run-tests.ps1" -TestType $testType -CodeCoverage:$RunSecurityTests
        }
        "logs" {
            $logDir = "$PSScriptRoot/logs"
            if (Test-Path $logDir) {
                Get-ChildItem $logDir -Filter "*.log" | Sort-Object LastWriteTime -Descending | Select-Object Name, LastWriteTime, Length
            } else {
                Write-Host "Logs directory not found. Run a command first."
            }
        }
        "score" {
            $result = Get-SecurityScore -RepoPath (Get-Location).Path
            Write-Host "🔐 Security Score: $($result.Score)/100 [Grade: $($result.Grade)]" -ForegroundColor (
                if ($result.Score -ge 80) { "Green" } elseif ($result.Score -ge 60) { "Yellow" } else { "Red" }
            )
            Write-Host "`n📝 Recommendations:"
            $result.Recommendations | ForEach-Object { Write-Host "  • $_" }
        }
        default {
            Main -Command $Command @mainParams
        }
    }
}
catch {
    Write-Error "Command '$Command' failed: $($_.Exception.Message)"
    exit 1
}
