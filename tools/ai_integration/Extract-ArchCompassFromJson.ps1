param(
    [Parameter(Mandatory = $true)]
    [string]$JsonPath,                # путь к 0101.json
    [Parameter(Mandatory = $true)]
    [string]$OutputRoot               # корень проекта Arch-Compass-Framework
)

# 1. Читаем JSON как сырой текст
$raw = Get-Content -Path $JsonPath -Raw -Encoding UTF8

function Save-Block {
    param(
        [string]$PatternStart,
        [string]$PatternEnd,
        [string]$TargetPath
    )

    $regex = [regex]::Escape($PatternStart) + '(.*?)' + [regex]::Escape($PatternEnd)
    $m = [regex]::Match($raw, $regex, 'Singleline')
    if (-not $m.Success) {
        Write-Warning "Не найден блок '$PatternStart' → $TargetPath"
        return
    }

    $code = $m.Groups[1].Value

    $fullPath = Join-Path $OutputRoot $TargetPath
    $dir = Split-Path $fullPath -Parent
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }

    $code | Set-Content -Path $fullPath -Encoding UTF8
    Write-Host "✅ Сохранён: $TargetPath"
}

# === CORE ===
Save-Block -PatternStart 'srccoreloggingStructuredLogger.psm1 ' `
          -PatternEnd   '--- 4. Main srccoreutilitiesUtilities.psm1' `
          -TargetPath   'src/Core/Logging.ps1'

Save-Block -PatternStart 'SecretManagerpowershell srccoresecuritySecretManager.psm1' `
          -PatternEnd   '--- 2...' `
          -TargetPath   'src/Core/Secrets.ps1'

Save-Block -PatternStart 'srccorevalidationInputValidator.psm1' `
          -PatternEnd   '-ModuleMember -Function Test-RepoName, Test-AzureSubscription' `
          -TargetPath   'src/Core/Validation.ps1'

Save-Block -PatternStart 'srccoreutilitiesUtilities.psm1powershell' `
          -PatternEnd   '--- 1. SecretManager.psm1' `
          -TargetPath   'src/Core/Utilities.ps1'

Save-Block -PatternStart 'srccorelocalizationLocalization.psm1powershell' `
          -PatternEnd   'srcMain.ps1powershell Main param stringRepoName' `
          -TargetPath   'src/Core/Localization.ps1'

Save-Block -PatternStart 'ConfigurationManager.psm1 , Arch-Compass-Framework' `
          -PatternEnd   '--- ! , , ... .' `
          -TargetPath   'src/Core/Configuration.ps1'

# === INFRASTRUCTURE ===
Save-Block -PatternStart 'srcinfrastructurecreationFileCreator.psm1 -Force' `
          -PatternEnd   '-ModuleMember -Function Connect-ToAzure, Deploy-ResourceGroup' `
          -TargetPath   'src/Infrastructure/Creation.ps1'

Save-Block -PatternStart 'srcInfrastructureMonitoring.ps1 powershell' `
          -PatternEnd   '-ModuleMember -Function Send-MetricToPrometheus, Test-InfrastructureReadiness' `
          -TargetPath   'src/Infrastructure/Monitoring.ps1'

Save-Block -PatternStart 'srcInfrastructureChangeTracking.ps1powershell' `
          -PatternEnd   '-ModuleMember -Function Get-ChangeReport' `
          -TargetPath   'src/Infrastructure/Git.ps1'

Save-Block -PatternStart 'srcinfrastructuredeploymentCloud.psm1 -Force AI-Module' `
          -PatternEnd   'Queues-Module PSScriptRootsrcqueuesRabbitMQClient.psm1' `
          -TargetPath   'src/Infrastructure/Deployment.ps1'

# === AI ===
Save-Block -PatternStart 'srcaiOpenAIIntegration.psm1 -Force' `
          -PatternEnd   'Queues-Module PSScriptRootsrcqueuesRabbitMQClient.psm1 -Force' `
          -TargetPath   'src/AI/OpenAI.ps1'

# === CLI / entry ===
Save-Block -PatternStart 'srcCLIArchCompassCLI.ps1powershell' `
          -PatternEnd   '-ModuleMember -Function Start-ArchCompassCLI' `
          -TargetPath   'src/CLI/ArchCompassCLI.ps1'

Save-Block -PatternStart 'Initialize-ArchCompass-Ultimate-Final.ps1powershell!usrbinenv pwsh' `
          -PatternEnd   'А 'using' statement must appear before any other statements in a script.' `
          -TargetPath   'bin/Initialize-ArchCompass-Ultimate-Final.ps1'
