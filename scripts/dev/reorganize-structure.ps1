param(
    [switch]$WhatIf = $false
)

Write-Host "🔍 Проверка структуры..."

$repoRoot = (Resolve-Path .).Path

$actions = @()

# 1. Проверяем и планируем перемещение существующих файлов
if (Test-Path "$repoRoot\ArchCompass.psm1") {
            if (-not ($actions | Where-Object { $_.Action -eq 'Rename' -and $_.From -eq "$repoRoot\ArchCompass.psm1" -and $_.To -eq "$repoRoot\arch-compass.psd1" })) {
        $actions += @{
            Action = "Rename"
            From = "$repoRoot\ArchCompass.psm1"
            To = "$repoRoot\arch-compass.psd1"
        }
    }
}

if (Test-Path "$repoRoot\src\core\security\SecretManager.psm1") {
            if (-not ($actions | Where-Object { $_.Action -eq 'Move' -and $_.From -eq "$repoRoot\src\core\security\SecretManager.psm1" -and $_.To -eq "$repoRoot\src\infrastructure\security\SecretManager.psm1" })) {
        $actions += @{
            Action = "Move"
            From = "$repoRoot\src\core\security\SecretManager.psm1"
            To = "$repoRoot\src\infrastructure\security\SecretManager.psm1"
        }
    }
}

if (Test-Path "$repoRoot\src\core\configuration\ConfigurationManager.psm1") {
            if (-not ($actions | Where-Object { $_.Action -eq 'Move' -and $_.From -eq "$repoRoot\src\core\configuration\ConfigurationManager.psm1" -and $_.To -eq "$repoRoot\src\core\utilities\ConfigurationManager.psm1" })) {
        $actions += @{
            Action = "Move"
            From = "$repoRoot\src\core\configuration\ConfigurationManager.psm1"
            To = "$repoRoot\src\core\utilities\ConfigurationManager.psm1"
        }
    }
}

if (Test-Path "$repoRoot\config\defaults\default_config.yaml") {
            if (-not ($actions | Where-Object { $_.Action -eq 'Move' -and $_.From -eq "$repoRoot\config\defaults\default_config.yaml" -and $_.To -eq "$repoRoot\config\templates\default_config.yaml" })) {
        $actions += @{
            Action = "Move"
            From = "$repoRoot\config\defaults\default_config.yaml"
            To = "$repoRoot\config\templates\default_config.yaml"
        }
    }
}

# 2. Проверяем и планируем создание недостающих папок
$requiredDirs = @(
    "src/core/logging",
    "src/core/validation",
    "src/core/localization",
    "src/core/security",
    "src/infrastructure/monitoring",
    "src/infrastructure/git",
    "src/infrastructure/deployment",
    "src/ai/openai",
    "src/cli",
    "bin",
    "tests/unit",
    "tests/integration",
    "docs/specifications",
    "docs/api",
    "config/templates",
    "config/secrets",
    "scripts/dev",
    "scripts/ci-cd"
)

foreach ($dir in $requiredDirs) {
    $fullPath = Join-Path -Path $repoRoot -ChildPath $dir
    if ($fullPath -and !(Test-Path -Path $fullPath)) {
        $actions += @{
            Action = "CreateDir"
            Path = $fullPath
        }
    }
}

# 3. Проверяем и планируем создание недостающих файлов
$requiredFiles = @(
    @{ Path = "src/core/logging/Logging.psm1"; Content = "`nfunction Write-Log { }`nExport-ModuleMember -Function Write-Log`n" },
    @{ Path = "src/core/validation/Validation.psm1"; Content = "`nfunction Test-Input { }`nExport-ModuleMember -Function Test-Input`n" },
    @{ Path = "src/core/localization/Localization.psm1"; Content = "`nfunction Get-LocalizedString { }`nExport-ModuleMember -Function Get-LocalizedString`n" },
    @{ Path = "src/infrastructure/monitoring/Monitoring.psm1"; Content = "`nfunction Send-Metric { }`nExport-ModuleMember -Function Send-Metric`n" },
    @{ Path = "src/infrastructure/git/Git.psm1"; Content = "`nfunction Get-ChangeReport { }`nExport-ModuleMember -Function Get-ChangeReport`n" },
    @{ Path = "src/infrastructure/deployment/Deployment.psm1"; Content = "`nfunction Deploy-ResourceGroup { }`nExport-ModuleMember -Function Deploy-ResourceGroup`n" },
    @{ Path = "src/ai/openai/OpenAI.psm1"; Content = "`nfunction Invoke-OpenAICompletion { }`nExport-ModuleMember -Function Invoke-OpenAICompletion`n" },
    @{ Path = "src/cli/CLI.psm1"; Content = "`nfunction Start-CLI { }`nExport-ModuleMember -Function Start-CLI`n" },
    @{ Path = "bin/Initialize.ps1"; Content = "#!/usr/bin/env pwsh`n`nWrite-Host 'Initializing Arch-Compass Framework...'`n" },
    @{ Path = "tests/unit/Logging.Tests.ps1"; Content = "`ndescribe 'Logging' { }`n" },
    @{ Path = "tests/integration/FullFlow.Tests.ps1"; Content = "`ndescribe 'FullFlow' { }`n" },
    @{ Path = "docs/specifications/Architecture.md"; Content = "# Architecture`n`nThe overall architecture of the framework.`n" },
    @{ Path = "docs/api/Logging.md"; Content = "# Logging API`n`nDocumentation for logging functions.`n" },
    @{ Path = "config/secrets/Secrets.psd1"; Content = "@{}`n" },
    @{ Path = "scripts/dev/Create-DevEnvironment.ps1"; Content = "# Script to set up a dev environment`n" },
    @{ Path = "scripts/ci-cd/Deploy-Production.ps1"; Content = "# Script for production deployment`n" },
    @{ Path = ".gitignore"; Content = "node_modules/`n*.log`n.DS_Store`n" },
    @{ Path = "README.md"; Content = "# Arch-Compass Framework`n`nTODO: Add description.`n" },
    @{ Path = "LICENSE"; Content = "TODO: Add license text.`n" },
    @{ Path = "CHANGELOG.md"; Content = "# Changelog`n`nAll notable changes to this project will be documented in this file.`n" }
)

foreach ($fileObj in $requiredFiles) {
    $fullPath = Join-Path -Path $repoRoot -ChildPath $fileObj.Path
    if ($fullPath -and !(Test-Path -Path $fullPath)) {
        $actions += @{
            Action = "CreateFile"
            Path = $fullPath
            Content = $fileObj.Content
        }
    }
}

# Выводим запланированные действия
foreach ($action in $actions) {
    if ($action.Action -eq "Rename") {
        Write-Host "🔄 (Planned) Rename: $($action.From) -> $($action.To)" -ForegroundColor Yellow
    } elseif ($action.Action -eq "Move") {
        Write-Host "📁 (Planned) Move: $($action.From) -> $($action.To)" -ForegroundColor Yellow
    } elseif ($action.Action -eq "CreateDir") {
        Write-Host "📦 (Planned) Create directory: $($action.Path)" -ForegroundColor Yellow
    } elseif ($action.Action -eq "CreateFile") {
        Write-Host "📄 (Planned) Create file: $($action.Path)" -ForegroundColor Yellow
    }
}

if ($WhatIf) {
    Write-Host "`n💡 WhatIf mode: No changes were made." -ForegroundColor Green
    return
}

# Выполняем действия
foreach ($action in $actions) {
    if ($action.Action -eq "Rename") {
        Rename-Item -Path $action.From -NewName $action.To -Force
        Write-Host "✅ Renamed: $($action.From) -> $($action.To)"
    } elseif ($action.Action -eq "Move") {
        $destDir = Split-Path $action.To -Parent
        if (!(Test-Path $destDir)) {
            New-Item -ItemType Directory -Path $destDir -Force | Out-Null
        }
        Move-Item -Path $action.From -Destination $action.To -Force
        Write-Host "✅ Moved: $($action.From) -> $($action.To)"
    } elseif ($action.Action -eq "CreateDir") {
        New-Item -ItemType Directory -Path $action.Path -Force | Out-Null
        Write-Host "✅ Created directory: $($action.Path)"
    } elseif ($action.Action -eq "CreateFile") {
        $dir = Split-Path $action.Path -Parent
        if (!(Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
        }
        Set-Content -Path $action.Path -Value $action.Content -Encoding UTF8
        Write-Host "✅ Created file: $($action.Path)"
    }
}

# 4. Удаляем пустые директории
Write-Host "`n🗑️ Удаление пустых директорий..."
Get-ChildItem -Path $repoRoot -Directory -Recurse | Where-Object { (Get-ChildItem $_.FullName -Recurse | Measure-Object).Count -eq 0 } | ForEach-Object {
    Remove-Item $_.FullName -Confirm:$false
    Write-Host "✅ Removed empty directory: $($_.FullName)"
}

# 5. Создаем лог миграции
$logPath = Join-Path $repoRoot "docs/structure_migration.md"
$logDir = Split-Path $logPath -Parent
if (!(Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
}
$migrationLog = @"
# Лог миграции структуры

Дата: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

## Перемещенные файлы:
- `ArchCompass.psm1` → `arch-compass.psd1` (корень)
- `src/core/security/SecretManager.psm1` → `src/infrastructure/security/`
- `src/core/configuration/ConfigurationManager.psm1` → `src/core/utilities/`
- `config/defaults/default_config.yaml` → `config/templates/`

## Созданные директории:
$((requiredDirs | ForEach-Object { "- $_" }) -join "`n")

## Созданные файлы:
$((requiredFiles | Where-Object { !(Test-Path (Join-Path $repoRoot $_.Path)) } | ForEach-Object { "- $($_.Path)" }) -join "`n")

"@ 

Set-Content -Path $logPath -Value $migrationLog -Encoding UTF8
Write-Host "📄 Created migration log: $logPath"

Write-Host "`n🎉 Миграция структуры завершена!" -ForegroundColor Green