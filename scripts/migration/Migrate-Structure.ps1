<#
.SYNOPSIS
    Безопасная миграция структуры проекта Arch-Compass в новую структуру arch-compass-system

.DESCRIPTION
    Выполняет поэтапную миграцию структуры проекта с возможностью отката на каждом этапе.
    Использует git для отслеживания изменений и создания точек восстановления.

.PARAMETER Step
    Номер этапа для выполнения (0-7). Если не указан, выполняется интерактивный режим.

.PARAMETER Rollback
    Откатывает изменения последнего этапа через git reset.

.PARAMETER WhatIf
    Показывает, что будет сделано, без фактического выполнения.

.EXAMPLE
    .\Migrate-Structure.ps1 -WhatIf
    Показывает план миграции без выполнения

.EXAMPLE
    .\Migrate-Structure.ps1 -Step 1
    Выполняет только этап 1 (создание структуры)

.EXAMPLE
    .\Migrate-Structure.ps1 -Rollback
    Откатывает последний этап
#>

[CmdletBinding(SupportsShouldProcess)]
param(
    [Parameter()]
    [ValidateRange(0, 7)]
    [int]$Step = -1,

    [Parameter()]
    [switch]$Rollback,

    [Parameter()]
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path $PSScriptRoot\..\..).Path
Set-Location $repoRoot

# Цвета для вывода
function Write-Step { param($msg) Write-Host "`n🔷 $msg" -ForegroundColor Cyan }
function Write-Success { param($msg) Write-Host "✅ $msg" -ForegroundColor Green }
function Write-Warning { param($msg) Write-Host "⚠️  $msg" -ForegroundColor Yellow }
function Write-Error { param($msg) Write-Host "❌ $msg" -ForegroundColor Red }

# Проверка git статуса
function Test-GitClean {
    $status = git status --porcelain
    if ($status) {
        Write-Warning "Рабочая директория не чистая. Рекомендуется сделать commit перед миграцией."
        if ($Force -or -not [Environment]::UserInteractive) {
            Write-Host "  Автоматическое продолжение (Force режим)" -ForegroundColor Gray
        } else {
            $response = Read-Host "Продолжить? (y/n)"
            if ($response -ne 'y') { exit }
        }
    }
}

# Этап 0: Подготовка
function Step-0-Preparation {
    Write-Step "ЭТАП 0: Подготовка"

    Test-GitClean

    # Пропуск интерактивного запроса в неинтерактивном режиме
    if (-not [Environment]::UserInteractive) {
        Write-Host "  Неинтерактивный режим: автоматическое продолжение" -ForegroundColor Gray
    }

    # Создание backup ветки
    $backupBranch = "backup/pre-migration-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
    if (-not $WhatIfPreference) {
        git checkout -b $backupBranch
        git checkout main 2>$null
        git checkout master 2>$null
        Write-Success "Создана backup ветка: $backupBranch"
    } else {
        Write-Host "  [WhatIf] Создана backup ветка: $backupBranch" -ForegroundColor Gray
    }

    # Commit текущего состояния
    if (-not $WhatIfPreference) {
        git add -A
        git commit -m "Pre-migration checkpoint" -m "Создана точка восстановления перед миграцией структуры"
        Write-Success "Создан checkpoint commit"
    } else {
        Write-Host "  [WhatIf] Создан checkpoint commit" -ForegroundColor Gray
    }

    Write-Success "Этап 0 завершен"
}

# Этап 1: Создание структуры директорий
function Step-1-CreateStructure {
    Write-Step "ЭТАП 1: Создание структуры директорий"

    $newDirs = @(
        # GitHub
        ".github/workflows",
        ".github/ISSUE_TEMPLATE",
        ".github/PULL_REQUEST_TEMPLATE",

        # Dev Containers
        ".devcontainer",

        # VS Code
        ".vscode",

        # Artifacts
        "artifacts/builds",
        "artifacts/packages",
        "artifacts/reports",
        "artifacts/logs",

        # Source - Core
        "src/core/commands",
        "src/core/logging",
        "src/core/validation",
        "src/core/rollback",
        "src/core/localization/en-US",
        "src/core/localization/ru-RU",
        "src/core/utilities",

        # Source - Providers
        "src/providers/azure",
        "src/providers/aws",
        "src/providers/gcp",

        # Source - AI
        "src/ai/analyzers",
        "src/ai/providers",
        "src/ai/prompts/structure-analysis",
        "src/ai/prompts/code-review",

        # Source - Infrastructure
        "src/infrastructure/monitoring",
        "src/infrastructure/messaging",
        "src/infrastructure/security",
        "src/infrastructure/deployment",

        # Source - Templates
        "src/templates/dotnet-webapi",
        "src/templates/nodejs-microservice",
        "src/templates/python-data",
        "src/templates/react-frontend",

        # Source - Web
        "src/web/dashboard",
        "src/web/api",

        # Config
        "config/environments",
        "config/templates",
        "config/schema",

        # Docs
        "docs/api/reference",
        "docs/api/examples",
        "docs/architecture/decisions",
        "docs/architecture/diagrams",
        "docs/guides/getting-started",
        "docs/guides/deployment",
        "docs/guides/troubleshooting",
        "docs/specifications",
        "docs/translations",

        # Tests
        "tests/unit/core",
        "tests/unit/providers",
        "tests/unit/ai",
        "tests/integration/azure",
        "tests/integration/monitoring",
        "tests/integration/security",
        "tests/e2e/scenarios",
        "tests/e2e/fixtures",
        "tests/performance/benchmarks",
        "tests/test-data/mocks",

        # Scripts
        "scripts/build",
        "scripts/dev",
        "scripts/deployment",
        "scripts/maintenance",

        # Tools
        "tools/code-analysis",
        "tools/migration",
        "tools/diagnostics",

        # Infrastructure
        "infrastructure/terraform/modules",
        "infrastructure/terraform/environments",
        "infrastructure/terraform/state",
        "infrastructure/kubernetes/base",
        "infrastructure/kubernetes/overlays",
        "infrastructure/kubernetes/helm",
        "infrastructure/docker",
        "infrastructure/monitoring/prometheus",
        "infrastructure/monitoring/grafana",

        # Samples
        "samples/quickstart",
        "samples/tutorials",
        "samples/advanced",

        # Packages
        "packages/nuget",
        "packages/npm",
        "packages/pypi"
    )

    foreach ($dir in $newDirs) {
        $fullPath = Join-Path $repoRoot $dir
        if (-not (Test-Path $fullPath)) {
            if ($WhatIfPreference) {
                Write-Host "  [WhatIf] Создана директория: $dir" -ForegroundColor Gray
            } else {
                New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
                # Создание .gitkeep для пустых директорий
                if ($dir -match "^(artifacts|packages|samples|infrastructure)") {
                    New-Item -ItemType File -Path (Join-Path $fullPath ".gitkeep") -Force | Out-Null
                }
            }
        }
    }

    Write-Success "Этап 1 завершен: созданы все необходимые директории"
}

# Этап 2: Перемещение файлов
function Step-2-MoveFiles {
    Write-Step "ЭТАП 2: Перемещение файлов"

    $moves = @(
        # Главный модуль
        @{ From = "ArchCompass.psm1"; To = "arch-compass.psd1"; Method = "Rename" },

        # Core - Configuration → Utilities
        @{ From = "src/core/configuration/ConfigurationManager.psm1"; To = "src/core/utilities/ConfigurationManager.psm1"; Method = "Move" },

        # Core - Security → Infrastructure/Security
        @{ From = "src/core/security/SecretManager.psm1"; To = "src/infrastructure/security/SecretManager.psm1"; Method = "Move" },

        # Из scripts/dev/src в основную структуру
        @{ From = "scripts/dev/src/core/logging/Logging.psm1"; To = "src/core/logging/AsyncLogger.psm1"; Method = "Move" },
        @{ From = "scripts/dev/src/core/validation/Validation.psm1"; To = "src/core/validation/InputValidator.psm1"; Method = "Move" },
        @{ From = "scripts/dev/src/core/localization/Localization.psm1"; To = "src/core/localization/LocalizationManager.psm1"; Method = "Move" },
        @{ From = "scripts/dev/src/infrastructure/monitoring/Monitoring.psm1"; To = "src/infrastructure/monitoring/PrometheusClient.psm1"; Method = "Move" },
        @{ From = "scripts/dev/src/infrastructure/deployment/Deployment.psm1"; To = "src/infrastructure/deployment/TerraformManager.psm1"; Method = "Move" },
        @{ From = "scripts/dev/src/infrastructure/git/Git.psm1"; To = "src/infrastructure/deployment/Git.psm1"; Method = "Move" },
        @{ From = "scripts/dev/src/ai/openai/OpenAI.psm1"; To = "src/ai/providers/OpenAIIntegration.psm1"; Method = "Move" },
        @{ From = "scripts/dev/src/cli/CLI.psm1"; To = "src/core/commands/CLI.psm1"; Method = "Move" },

        # Config
        @{ From = "config/defaults/default_config.yaml"; To = "config/templates/default_config.yaml"; Method = "Move" },
        @{ From = "config/schemas"; To = "config/schema"; Method = "Move" },

        # Docs
        @{ From = "scripts/dev/docs/specifications/Architecture.md"; To = "docs/architecture/diagrams/Architecture.md"; Method = "Move" },
        @{ From = "scripts/dev/docs/api/Logging.md"; To = "docs/api/reference/Logging.md"; Method = "Move" },

        # Tests
        @{ From = "scripts/dev/tests/integration/FullFlow.Tests.ps1"; To = "tests/integration/scenarios/FullFlow.Tests.ps1"; Method = "Move" },
        @{ From = "scripts/dev/tests/unit/Logging.Tests.ps1"; To = "tests/unit/core/Logging.Tests.ps1"; Method = "Move" },

        # Scripts
        @{ From = "scripts/dev/scripts/ci-cd/Deploy-Production.ps1"; To = "scripts/deployment/deploy-azure.ps1"; Method = "Move" },
        @{ From = "scripts/dev/scripts/dev/Create-DevEnvironment.ps1"; To = "scripts/dev/setup-dev.ps1"; Method = "Move" }
    )

    foreach ($move in $moves) {
        $fromPath = Join-Path $repoRoot $move.From
        $toPath = Join-Path $repoRoot $move.To

        if (Test-Path $fromPath) {
            $toDir = Split-Path $toPath -Parent
            if (-not (Test-Path $toDir)) {
                if (-not $WhatIfPreference) {
                    New-Item -ItemType Directory -Path $toDir -Force | Out-Null
                }
            }

            if ($WhatIfPreference) {
                Write-Host "  [WhatIf] $($move.Method): $($move.From) → $($move.To)" -ForegroundColor Gray
            } else {
                # Пытаемся использовать git mv (для файлов под контролем версий)
                $gitSuccess = $false
                try {
                    $null = & git mv $fromPath $toPath 2>&1 | Out-Null
                    if ($LASTEXITCODE -eq 0) {
                        $gitSuccess = $true
                    }
                } catch {
                    # Git mv не сработал, файл не под контролем версий
                    $gitSuccess = $false
                }

                if (-not $gitSuccess) {
                    # Если git mv не сработал (файл не в git), используем обычный Move
                    try {
                        Move-Item -Path $fromPath -Destination $toPath -Force -ErrorAction Stop
                        $gitSuccess = $true
                    } catch {
                        Write-Warning "  ✗ Ошибка при перемещении $($move.From): $_"
                    }
                }

                if ($gitSuccess -and (Test-Path $toPath)) {
                    Write-Host "  ✓ $($move.Method): $($move.From)" -ForegroundColor Green
                } elseif (-not (Test-Path $fromPath) -and (Test-Path $toPath)) {
                    Write-Host "  ✓ $($move.Method): $($move.From)" -ForegroundColor Green
                } else {
                    Write-Warning "  ✗ Не удалось переместить: $($move.From)"
                }
            }
        } else {
            Write-Warning "Файл не найден: $($move.From)"
        }
    }

    Write-Success "Этап 2 завершен: файлы перемещены"
}

# Этап 3: Обновление путей импорта
function Step-3-UpdatePaths {
    Write-Step "ЭТАП 3: Обновление путей импорта"

    # Маппинг старых путей на новые
    $pathMappings = @{
        'src\\core\\configuration\\ConfigurationManager\.psm1' = 'src/core/utilities/ConfigurationManager.psm1'
        'src\\core\\security\\SecretManager\.psm1' = 'src/infrastructure/security/SecretManager.psm1'
        'scripts\\dev\\src\\core\\logging\\Logging\.psm1' = 'src/core/logging/AsyncLogger.psm1'
        'scripts\\dev\\src\\core\\validation\\Validation\.psm1' = 'src/core/validation/InputValidator.psm1'
        'config\\defaults\\default_config\.yaml' = 'config/templates/default_config.yaml'
    }

    # Файлы для обновления
    $filesToUpdate = @(
        "arch-compass.psd1",
        "src/core/utilities/ConfigurationManager.psm1",
        "src/infrastructure/security/SecretManager.psm1",
        "src/core/logging/AsyncLogger.psm1",
        "src/core/validation/InputValidator.psm1"
    )

    foreach ($file in $filesToUpdate) {
        $filePath = Join-Path $repoRoot $file
        if (Test-Path $filePath) {
            if ($WhatIfPreference) {
                Write-Host "  [WhatIf] Обновление путей в: $file" -ForegroundColor Gray
            } else {
                $content = Get-Content $filePath -Raw
                $originalContent = $content

                foreach ($mapping in $pathMappings.GetEnumerator()) {
                    $content = $content -replace $mapping.Key, $mapping.Value
                }

                # Обновление $PSScriptRoot путей
                $content = $content -replace '\$PSScriptRoot\\src\\core\\configuration', '$PSScriptRoot/../utilities'
                $content = $content -replace '\$PSScriptRoot\\src\\core\\security', '$PSScriptRoot/../../infrastructure/security'

                if ($content -ne $originalContent) {
                    Set-Content -Path $filePath -Value $content -NoNewline
                    Write-Host "  ✓ Обновлен: $file" -ForegroundColor Green
                }
            }
        }
    }

    Write-Success "Этап 3 завершен: пути обновлены"
}

# Этап 4: Создание новых файлов конфигурации
function Step-4-CreateConfigFiles {
    Write-Step "ЭТАП 4: Создание новых конфигурационных файлов"

    # .gitignore обновление
    $gitignoreAdditions = @"
# Artifacts
artifacts/
!artifacts/.gitkeep

# Packages
packages/
!packages/.gitkeep
"@

    if (-not $WhatIfPreference) {
        $gitignorePath = Join-Path $repoRoot ".gitignore"
        if (Test-Path $gitignorePath) {
            $currentContent = Get-Content $gitignorePath -Raw
            if ($currentContent -notmatch 'artifacts/') {
                Add-Content -Path $gitignorePath -Value "`n$gitignoreAdditions"
            }
        }
    }

    # Создание базовых конфигурационных файлов (если их нет)
    $configFiles = @{
        '.vscode/settings.json' = @'
{
    "powershell.codeFormatting.preset": "OTBS",
    "files.exclude": {
        "**/artifacts": true,
        "**/packages": true
    }
}
'@
        '.vscode/extensions.json' = @'
{
    "recommendations": [
        "ms-vscode.powershell",
        "ms-azuretools.vscode-azurefunctions"
    ]
}
'@
        '.devcontainer/devcontainer.json' = @'
{
    "name": "Arch-Compass Development",
    "image": "mcr.microsoft.com/powershell:latest",
    "features": {
        "ghcr.io/devcontainers/features/git:1": {}
    }
}
'@
    }

    foreach ($file in $configFiles.GetEnumerator()) {
        $filePath = Join-Path $repoRoot $file.Key
        if (-not (Test-Path $filePath)) {
            if ($WhatIfPreference) {
                Write-Host "  [WhatIf] Создан файл: $($file.Key)" -ForegroundColor Gray
            } else {
                $dir = Split-Path $filePath -Parent
                if (-not (Test-Path $dir)) {
                    New-Item -ItemType Directory -Path $dir -Force | Out-Null
                }
                Set-Content -Path $filePath -Value $file.Value
                Write-Host "  ✓ Создан: $($file.Key)" -ForegroundColor Green
            }
        }
    }

    Write-Success "Этап 4 завершен: конфигурационные файлы созданы"
}

# Этап 5: Очистка
function Step-5-Cleanup {
    Write-Step "ЭТАП 5: Очистка старых файлов и директорий"

    $dirsToRemove = @(
        "scripts/dev/src",
        "scripts/dev/docs",
        "scripts/dev/tests",
        "scripts/dev/scripts",
        "src/core/configuration",
        "src/core/security",
        "config/defaults",
        "config/schemas"
    )

    foreach ($dir in $dirsToRemove) {
        $dirPath = Join-Path $repoRoot $dir
        if (Test-Path $dirPath) {
            $items = Get-ChildItem $dirPath -Recurse -File
            if ($items.Count -eq 0) {
                if ($WhatIfPreference) {
                    Write-Host "  [WhatIf] Удалена пустая директория: $dir" -ForegroundColor Gray
                } else {
                    Remove-Item -Path $dirPath -Recurse -Force
                    Write-Host "  ✓ Удалена: $dir" -ForegroundColor Green
                }
            } else {
                Write-Warning "Директория не пустая: $dir (оставлена)"
            }
        }
    }

    Write-Success "Этап 5 завершен: очистка выполнена"
}

# Этап 6: Проверка
function Step-6-Verification {
    Write-Step "ЭТАП 6: Проверка работоспособности"

    # Проверка существования ключевых файлов
    $keyFiles = @(
        "arch-compass.psd1",
        "src/core/utilities/ConfigurationManager.psm1",
        "src/infrastructure/security/SecretManager.psm1"
    )

    $allExist = $true
    foreach ($file in $keyFiles) {
        $filePath = Join-Path $repoRoot $file
        if (Test-Path $filePath) {
            Write-Host "  ✓ Найден: $file" -ForegroundColor Green
        } else {
            Write-Host "  ✗ Не найден: $file" -ForegroundColor Red
            $allExist = $false
        }
    }

    if ($allExist) {
        Write-Success "Все ключевые файлы на месте"
    } else {
        Write-Error "Некоторые файлы отсутствуют. Проверьте миграцию."
    }

    # Проверка синтаксиса PowerShell (если доступен PSScriptAnalyzer)
    Write-Host "`n  Проверка синтаксиса PowerShell..."
    $psFiles = Get-ChildItem -Path $repoRoot -Filter "*.psm1" -Recurse | Select-Object -First 5
    foreach ($psFile in $psFiles) {
        $errors = $null
        $null = [System.Management.Automation.PSParser]::Tokenize((Get-Content $psFile.FullName -Raw), [ref]$errors)
        if ($errors.Count -eq 0) {
            Write-Host "  ✓ Синтаксис OK: $($psFile.Name)" -ForegroundColor Green
        } else {
            Write-Host "  ✗ Ошибки синтаксиса: $($psFile.Name)" -ForegroundColor Red
            $errors | ForEach-Object { Write-Host "    - $_" -ForegroundColor Yellow }
        }
    }

    Write-Success "Этап 6 завершен: проверка выполнена"
}

# Этап 7: Финализация
function Step-7-Finalization {
    Write-Step "ЭТАП 7: Финализация"

    if (-not $WhatIfPreference) {
        # Git add всех изменений
        git add -A

        # Commit миграции
        $commitMessage = @'
Реорганизация структуры проекта в соответствии с новой архитектурой:

* Перемещение модулей в новую структуру
* Обновление путей импорта
* Создание новой структуры директорий
* Обновление конфигурационных файлов
* Очистка старых файлов

См. docs/migration/MIGRATION_PLAN.md для деталей.
'@
        git commit -m "Migrate to arch-compass-system structure" -m $commitMessage

        Write-Success "Создан commit миграции"
        Write-Host "`n  Для просмотра изменений: git show HEAD" -ForegroundColor Cyan
        Write-Host "  Для отката: git reset --hard HEAD~1" -ForegroundColor Yellow
    } else {
        Write-Host "  [WhatIf] Создан commit миграции" -ForegroundColor Gray
    }

    Write-Success "Этап 7 завершен: миграция завершена!"
}

# Главная функция
function Main {
    Write-Host @"
╔═══════════════════════════════════════════════════════════╗
║     МИГРАЦИЯ СТРУКТУРЫ ПРОЕКТА ARCH-COMPASS               ║
║     Безопасная поэтапная миграция с возможностью отката  ║
╚═══════════════════════════════════════════════════════════╝
"@ -ForegroundColor Cyan

    if ($Rollback) {
        Write-Warning "Откат последнего commit..."
        git reset --hard HEAD~1
        Write-Success "Откат выполнен"
        return
    }

    if ($Step -ge 0) {
        # Выполнение конкретного этапа
        switch ($Step) {
            0 { Step-0-Preparation }
            1 { Step-1-CreateStructure }
            2 { Step-2-MoveFiles }
            3 { Step-3-UpdatePaths }
            4 { Step-4-CreateConfigFiles }
            5 { Step-5-Cleanup }
            6 { Step-6-Verification }
            7 { Step-7-Finalization }
        }
    } else {
        # Интерактивный режим
        Write-Host "`nДоступные этапы:" -ForegroundColor Yellow
        Write-Host "  0 - Подготовка (backup, checkpoint)"
        Write-Host "  1 - Создание структуры директорий"
        Write-Host "  2 - Перемещение файлов"
        Write-Host "  3 - Обновление путей импорта"
        Write-Host "  4 - Создание конфигурационных файлов"
        Write-Host "  5 - Очистка старых файлов"
        Write-Host "  6 - Проверка работоспособности"
        Write-Host "  7 - Финализация (commit)"
        Write-Host ""

        if ($WhatIfPreference) {
            Write-Host "Режим WhatIf: изменения не будут применены`n" -ForegroundColor Yellow
            Write-Host "План миграции:" -ForegroundColor Cyan
            Write-Host "  Этап 0: Подготовка (backup, checkpoint)" -ForegroundColor Gray
            Write-Host "  Этап 1: Создание структуры директорий" -ForegroundColor Gray
            Write-Host "  Этап 2: Перемещение файлов" -ForegroundColor Gray
            Write-Host "  Этап 3: Обновление путей импорта" -ForegroundColor Gray
            Write-Host "  Этап 4: Создание конфигурационных файлов" -ForegroundColor Gray
            Write-Host "  Этап 5: Очистка старых файлов" -ForegroundColor Gray
            Write-Host "  Этап 6: Проверка работоспособности" -ForegroundColor Gray
            Write-Host "  Этап 7: Финализация (commit)" -ForegroundColor Gray
            Write-Host "`nДля выполнения миграции запустите скрипт без -WhatIf" -ForegroundColor Yellow
            return
        }

        if ($Force -or -not [Environment]::UserInteractive) {
            $response = 'y'  # Автоматически 'y' в Force или неинтерактивном режиме
        } else {
            $response = Read-Host "Выполнить все этапы последовательно? (y/n)"
        }
        if ($response -eq 'y') {
            Step-0-Preparation
            Step-1-CreateStructure
            Step-2-MoveFiles
            Step-3-UpdatePaths
            Step-4-CreateConfigFiles
            Step-5-Cleanup
            Step-6-Verification

            if ([Environment]::UserInteractive) {
                if ($Force -or -not [Environment]::UserInteractive) {
                $finalize = 'y'  # Автоматически 'y' в Force или неинтерактивном режиме
            } else {
                $finalize = Read-Host "`nСоздать commit? (y/n)"
            }
            } else {
                $finalize = 'y'  # Автоматически 'y' в неинтерактивном режиме
            }

            if ($finalize -eq 'y') {
                Step-7-Finalization
            }
        }
    }
}

Main
