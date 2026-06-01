#!/usr/bin/env pwsh
<#
.SYNOPSIS
Перемещает скрипты из корня scripts/ в соответствующие категории согласно архитектурному плану.

.DESCRIPTION
Этот скрипт реализует Фазу 2 реструктуризации папки scripts/:
1. Перемещает Windows-скрипты в windows/
2. Перемещает Linux-скрипты в linux/
3. Перемещает Python-скрипты в python/
4. Оставляет кросс-платформенные/общие скрипты в корне

Архитектурный принцип: "Сохранять историческую ценность, обеспечивая навигацию"
#>

param(
    [switch]$WhatIf,
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$script:TotalMoved = 0
$script:TotalSkipped = 0

function Write-ColorOutput {
    param([string]$Message, [string]$Color = "White")
    Write-Host $Message -ForegroundColor $Color
}

function Move-Script {
    param(
        [string]$ScriptName,
        [string]$TargetDir,
        [string]$Reason
    )

    $sourcePath = Join-Path $PSScriptRoot $ScriptName
    $targetDirPath = Join-Path $PSScriptRoot $TargetDir
    $targetPath = Join-Path $targetDirPath $ScriptName

    if (-not (Test-Path $sourcePath)) {
        Write-ColorOutput "  [SKIP] $ScriptName → не найден в корне" "Yellow"
        $script:TotalSkipped++
        return
    }

    # Создаём целевую директорию, если её нет
    if (-not (Test-Path $targetDirPath)) {
        Write-ColorOutput "  [INFO] Создаю директорию: $TargetDir" "Cyan"
        if (-not $WhatIf) {
            New-Item -ItemType Directory -Path $targetDirPath -Force | Out-Null
        }
    }

    if ($WhatIf) {
        Write-ColorOutput "  [WHATIF] $ScriptName → $TargetDir/$ScriptName" "Gray"
        Write-ColorOutput "          Причина: $Reason" "Gray"
        $script:TotalMoved++
        return
    }

    try {
        Move-Item -Path $sourcePath -Destination $targetPath -Force:$Force
        Write-ColorOutput "  [OK] $ScriptName → $TargetDir/$ScriptName" "Green"
        Write-ColorOutput "       Причина: $Reason" "DarkGray"
        $script:TotalMoved++
    }
    catch {
        Write-ColorOutput "  [ERROR] Не удалось переместить $ScriptName : $_" "Red"
    }
}

Write-ColorOutput "==========================================" "Cyan"
Write-ColorOutput "РЕСТРУКТУРИЗАЦИЯ SCRIPTS/" "Cyan"
Write-ColorOutput "Архитектурный подход: 'От Зеро к Херо'" "Cyan"
Write-ColorOutput "==========================================" "Cyan"
Write-ColorOutput ""

if ($WhatIf) {
    Write-ColorOutput "РЕЖИМ ПРОСМОТРА (WhatIf): изменения не применяются" "Yellow"
    Write-ColorOutput ""
}

# 1. Windows-скрипты
Write-ColorOutput "1. WINDOWS-СКРИПТЫ (PowerShell/Batch):" "Magenta"
$windowsScripts = @(
    @{Name="fix_encoding.ps1"; Reason="Windows-specific PowerShell script"},
    @{Name="migrate-to-monorepo.bat"; Reason="Windows batch script"}
)

foreach ($script in $windowsScripts) {
    Move-Script -ScriptName $script.Name -TargetDir "windows" -Reason $script.Reason
}

# 2. Linux-скрипты
Write-ColorOutput ""
Write-ColorOutput "2. LINUX-СКРИПТЫ (Bash/Shell):" "Magenta"
$linuxScripts = @(
    @{Name="generate-index.sh"; Reason="Linux shell script"},
    @{Name="generate-site.sh"; Reason="Linux shell script"},
    @{Name="backup-postgres.sh"; Reason="PostgreSQL on Linux"},
    @{Name="restore-postgres.sh"; Reason="PostgreSQL on Linux"},
    @{Name="check-lfs.sh"; Reason="Git LFS check (Linux)"}
)

foreach ($script in $linuxScripts) {
    Move-Script -ScriptName $script.Name -TargetDir "linux" -Reason $script.Reason
}

# 3. Python-скрипты
Write-ColorOutput ""
Write-ColorOutput "3. PYTHON-СКРИПТЫ (Кросс-платформенные):" "Magenta"
$pythonScripts = @(
    @{Name="healthcheck.py"; Reason="Cross-platform Python"},
    @{Name="migrate-sqlite-to-postgres.py"; Reason="Cross-platform Python"},
    @{Name="sync-from-my-ecosystem.py"; Reason="Cross-platform Python"},
    @{Name="test_yandex_gpt_integration.py"; Reason="Cross-platform Python"},
    @{Name="translate-docs.py"; Reason="Cross-platform Python"}
)

foreach ($script in $pythonScripts) {
    Move-Script -ScriptName $script.Name -TargetDir "python" -Reason $script.Reason
}

# 4. Скрипты, которые остаются в корне (кросс-платформенные или общие)
Write-ColorOutput ""
Write-ColorOutput "4. СКРИПТЫ, ОСТАЮЩИЕСЯ В КОРНЕ:" "Magenta"
$rootScripts = @(
    "check-badges-health.py",
    "check-dependency-updates.py",
    "check_badge_urls.py",
    "check_yaml_fixed.py",
    "cleanup-old-branches.ps1",
    "cleanup-old-branches.sh",
    "deploy.sh",
    "enhance-badge-links.py",
    "fix_import_issues.py",
    "git-automation.sh",
    "health-check.sh",
    "rag-automation.sh",
    "security-check.sh",
    "setup-environment.sh",
    "setup-monitoring.sh",
    "setup-vscode-extensions.py",
    "start-all.sh",
    "stop-all.sh",
    "sync_projects_by_hash.py",
    "update-badges-enhanced.py",
    "validate_dependabot.py"
)

foreach ($script in $rootScripts) {
    $sourcePath = Join-Path $PSScriptRoot $script
    if (Test-Path $sourcePath) {
        Write-ColorOutput "  [KEEP] $script → остаётся в корне" "DarkGray"
    }
}

Write-ColorOutput ""
Write-ColorOutput "==========================================" "Cyan"
Write-ColorOutput "РЕЗУЛЬТАТ:" "Cyan"
Write-ColorOutput "  Перемещено: $script:TotalMoved скриптов" "Green"
Write-ColorOutput "  Пропущено: $script:TotalSkipped скриптов" $(if ($script:TotalSkipped -gt 0) { "Yellow" } else { "Green" })
Write-ColorOutput ""

if ($WhatIf) {
    Write-ColorOutput "Для применения изменений запустите скрипт БЕЗ параметра -WhatIf" "Yellow"
    Write-ColorOutput "  .\restructure-scripts.ps1 -Force" "White"
} else {
    Write-ColorOutput "Реструктуризация завершена!" "Green"
    Write-ColorOutput "Следующие шаги:" "Cyan"
    Write-ColorOutput "  1. Проверить целостность скриптов" "White"
    Write-ColorOutput "  2. Обновить INDEX.md" "White"
    Write-ColorOutput "  3. Сделать коммит изменений" "White"
}

Write-ColorOutput "==========================================" "Cyan"
