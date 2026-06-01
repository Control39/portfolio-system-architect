#!/usr/bin/env pwsh
# =============================================================================
# MIGRATION SCRIPT: .agents/ + codeassistant/ + .sourcecraft/ → apps/cognitive_agent/
# =============================================================================
# Цель: Объединить все агенты в apps/cognitive_agent/
# Важно: Сравнивает содержимое файлов, а не только названия
# =============================================================================

$ErrorActionPreference = "Stop"
$StartTime = Get-Date

# Цвета для вывода
$Colors = @{
    Info     = "Cyan"
    Success  = "Green"
    Warning  = "Yellow"
    Error    = "Red"
    Highlight = "Magenta"
}

function Write-Log {
    param([string]$Message, [string]$Color = "White")
    $timestamp = Get-Date -Format "HH:mm:ss"
    Write-Host "[$timestamp] $Message" -ForegroundColor $Color
}

function Compare-Files-Content {
    param([string]$File1, [string]$File2)
    if (-not (Test-Path $File1) -or -not (Test-Path $File2)) {
        return $false
    }
    $content1 = Get-Content $File1 -Raw
    $content2 = Get-Content $File2 -Raw
    return ($content1 -eq $content2)
}

function Get-File-Hash {
    param([string]$FilePath)
    if (Test-Path $FilePath) {
        return (Get-FileHash $FilePath).Hash
    }
    return $null
}

function Merge-Directories {
    param(
        [string]$Source,
        [string]$Destination,
        [string]$ItemType = "files"
    )

    if (-not (Test-Path $Source)) {
        Write-Log "Игнорирую несуществующий источник: $Source" -Color $Colors.Warning
        return 0
    }

    $copiedCount = 0
    $skippedCount = 0
    $updatedCount = 0

    Write-Log "Объединение $ItemType: $Source → $Destination" -Color $Colors.Info

    $items = Get-ChildItem -Path $Source -Force

    foreach ($item in $items) {
        $destPath = Join-Path $Destination $item.Name

        if ($item.PSIsContainer) {
            # Папка - рекурсивно
            if (-not (Test-Path $destPath)) {
                New-Item -ItemType Directory -Path $destPath | Out-Null
                Write-Log "  Создана папка: $($item.Name)" -Color $Colors.Success
                $copiedCount++
            }
            $subResult = Merge-Directories -Source $item.FullName -Destination $destPath -ItemType "файлов"
            $copiedCount += $subResult
        }
        else {
            # Файл - сравниваем содержимое
            if (Test-Path $destPath) {
                $sourceHash = Get-File-Hash -FilePath $item.FullName
                $destHash = Get-File-Hash -FilePath $destPath

                if ($sourceHash -eq $destHash) {
                    Write-Log "  Пропущено (идентично): $($item.Name)" -Color $Colors.Warning
                    $skippedCount++
                }
                else {
                    Write-Log "  Обновлено (разное содержимое): $($item.Name)" -Color $Colors.Highlight
                    Copy-Item -Path $item.FullName -Destination $destPath -Force
                    $updatedCount++
                }
            }
            else {
                Copy-Item -Path $item.FullName -Destination $destPath
                Write-Log "  Скопировано: $($item.Name)" -Color $Colors.Success
                $copiedCount++
            }
        }
    }

    return $copiedCount + $updatedCount
}

# =============================================================================
# ЭТАП 1: Проверка предварительных условий
# =============================================================================
Write-Log "`n========================================" -Color $Colors.Highlight
Write-Log "ЭТАП 1: Проверка предварительных условий" -Color $Colors.Highlight
Write-Log "========================================`n" -Color $Colors.Highlight

$checks = @{
    "Git репозиторий" = (Test-Path ".git")
    "apps/cognitive_agent/" = (Test-Path "apps/cognitive_agent")
    ".agents/" = (Test-Path ".agents")
    "codeassistant/" = (Test-Path "codeassistant")
    ".sourcecraft/" = (Test-Path ".sourcecraft")
}

$allPassed = $true
foreach ($check in $checks.Keys) {
    $status = if ($checks[$check]) { "✅" } else { "⚠️" }
    Write-Log "  $status $check" -Color $(if ($checks[$check]) { $Colors.Success } else { $Colors.Warning })
    if (-not $checks[$check]) { $allPassed = $false }
}

if (-not $allPassed) {
    Write-Log "`n⚠️ Некоторые проверки не пройдены. Продолжить? (y/n): " -Color $Colors.Warning
    $response = Read-Host
    if ($response -ne 'y') {
        Write-Log "Миграция отменена" -Color $Colors.Error
        exit 1
    }
}

# =============================================================================
# ЭТАП 2: Сравнение скиллов (критично!)
# =============================================================================
Write-Log "`n========================================" -Color $Colors.Highlight
Write-Log "ЭТАП 2: Сравнение скиллов" -Color $Colors.Highlight
Write-Log "========================================`n" -Color $Colors.Highlight

$skillsSources = @{
    ".agents/skills" = "source-agents"
    "codeassistant/skills" = "source-codeassistant"
    ".sourcecraft/skills" = "source-sourcecraft"
}

$destinationSkills = "apps/cognitive_agent/skills"
$skillComparison = @{}

foreach ($source in $skillsSources.Keys) {
    if (Test-Path $source) {
        $skills = Get-ChildItem -Path $source -Directory
        foreach ($skill in $skills) {
            $skillName = $skill.Name
            $sourceType = $skillsSources[$source]

            if (-not $skillComparison.ContainsKey($skillName)) {
                $skillComparison[$skillName] = @{}
            }

            $skillComparison[$skillName][$sourceType] = $skill.FullName
        }
    }
}

Write-Log "Найдено уникальных скиллов: $($skillComparison.Keys.Count)" -Color $Colors.Info

$duplicateSkills = 0
$mergedSkills = 0

foreach ($skillName in $skillComparison.Keys) {
    $sources = $skillComparison[$skillName]

    if ($sources.Count -gt 1) {
        $duplicateSkills++
        Write-Log "`n  Дубликат скилла: $skillName" -Color $Colors.Warning
        Write-Log "    Источники: $($sources.Keys -join ', ')" -Color $Colors.Warning

        # Выбираем "лучшую" версию по количеству файлов
        $bestSource = $null
        $maxFiles = 0

        foreach ($sourceType in $sources.Keys) {
            $skillPath = $sources[$sourceType]
            if (Test-Path $skillPath) {
                $fileCount = (Get-ChildItem -Path $skillPath -Recurse -File).Count
                Write-Log "      $sourceType: $fileCount файлов" -Color $Colors.Info

                if ($fileCount -gt $maxFiles) {
                    $maxFiles = $fileCount
                    $bestSource = $skillPath
                }
            }
        }

        if ($bestSource) {
            Write-Log "    → Будет использован: $bestSource" -Color $Colors.Success
        }
    }
    else {
        $mergedSkills++
    }
}

Write-Log "`nИтого: $duplicateSkills дубликатов, $mergedSkills уникальных" -Color $Colors.Info

Write-Log "`nПродолжить миграцию? (y/n): " -Color $Colors.Highlight
$response = Read-Host
if ($response -ne 'y') {
    Write-Log "Миграция отменена" -Color $Colors.Error
    exit 1
}

# =============================================================================
# ЭТАП 3: Объединение скиллов
# =============================================================================
Write-Log "`n========================================" -Color $Colors.Highlight
Write-Log "ЭТАП 3: Объединение скиллов" -Color $Colors.Highlight
Write-Log "========================================`n" -Color $Colors.Highlight

$totalSkillsCopied = 0

foreach ($skillName in $skillComparison.Keys) {
    $sources = $skillComparison[$skillName]
    $destSkillPath = Join-Path $destinationSkills $skillName

    # Создаем папку если нет
    if (-not (Test-Path $destSkillPath)) {
        New-Item -ItemType Directory -Path $destSkillPath | Out-Null
    }

    # Выбираем лучший источник (максимум файлов)
    $bestSource = $null
    $maxFiles = 0

    foreach ($sourceType in $sources.Keys) {
        $skillPath = $sources[$sourceType]
        if (Test-Path $skillPath) {
            $fileCount = (Get-ChildItem -Path $skillPath -Recurse -File).Count
            if ($fileCount -gt $maxFiles) {
                $maxFiles = $fileCount
                $bestSource = $skillPath
            }
        }
    }

    if ($bestSource) {
        # Сравниваем содержимое каждого файла
        $filesCopied = 0
        $existingFiles = Get-ChildItem -Path $destSkillPath -Recurse -File -ErrorAction SilentlyContinue

        foreach ($sourceFile in (Get-ChildItem -Path $bestSource -Recurse -File)) {
            $relativePath = $sourceFile.FullName.Replace($bestSource, '').Trim('\')
            $destFile = Join-Path $destSkillPath $relativePath

            $destDir = Split-Path $destFile -Parent
            if (-not (Test-Path $destDir)) {
                New-Item -ItemType Directory -Path $destDir | Out-Null
            }

            if (Test-Path $destFile) {
                $sourceHash = Get-File-Hash -FilePath $sourceFile.FullName
                $destHash = Get-File-Hash -FilePath $destFile

                if ($sourceHash -ne $destHash) {
                    Write-Log "  Обновлено: $skillName/$relativePath" -Color $Colors.Highlight
                    Copy-Item -Path $sourceFile.FullName -Destination $destFile -Force
                    $filesCopied++
                }
            }
            else {
                Write-Log "  Добавлено: $skillName/$relativePath" -Color $Colors.Success
                Copy-Item -Path $sourceFile.FullName -Destination $destFile
                $filesCopied++
            }
        }

        $totalSkillsCopied += $filesCopied
        Write-Log "  ✓ $skillName: $filesCopied файлов" -Color $Colors.Success
    }
}

Write-Log "`nВсего файлов скиллов скопировано/обновлено: $totalSkillsCopied" -Color $Colors.Success

# =============================================================================
# ЭТАП 4: Объединение остальных папок
# =============================================================================
Write-Log "`n========================================" -Color $Colors.Highlight
Write-Log "ЭТАП 4: Объединение остальных папок" -Color $Colors.Highlight
Write-Log "========================================`n" -Color $Colors.Highlight

$directoriesToMerge = @(
    @{ Source = ".agents/config"; Dest = "apps/cognitive_agent/config" },
    @{ Source = ".agents/workflows"; Dest = "apps/cognitive_agent/workflows" },
    @{ Source = ".agents/rules"; Dest = "apps/cognitive_agent/rules" },
    @{ Source = ".agents/scripts"; Dest = "apps/cognitive_agent/scripts" },
    @{ Source = ".agents/teacher"; Dest = "apps/cognitive_agent/teacher" },
    @{ Source = ".agents/tests"; Dest = "apps/cognitive_agent/tests" },
    @{ Source = ".agents/tools"; Dest = "apps/cognitive_agent/tools" },
    @{ Source = ".agents/plans"; Dest = "apps/cognitive_agent/plans" },
    @{ Source = ".agents/integrations"; Dest = "apps/cognitive_agent/integrations" },
    @{ Source = ".agents/dashboards"; Dest = "apps/cognitive_agent/dashboards" },
    @{ Source = ".agents/changelogs"; Dest = "apps/cognitive_agent/changelogs" },
    @{ Source = "codeassistant/rules"; Dest = "apps/cognitive_agent/rules" },
    @{ Source = "codeassistant/teacher"; Dest = "apps/cognitive_agent/teacher" },
    @{ Source = "codeassistant/tools"; Dest = "apps/cognitive_agent/tools" }
)

$totalDirsCopied = 0

foreach ($dir in $directoriesToMerge) {
    if (Test-Path $dir.Source) {
        $count = Merge-Directories -Source $dir.Source -Destination $dir.Dest -ItemType "папок"
        $totalDirsCopied += $count
    }
}

Write-Log "`nВсего элементов папок обработано: $totalDirsCopied" -Color $Colors.Success

# =============================================================================
# ЭТАП 5: Объединение конфигурационных файлов
# =============================================================================
Write-Log "`n========================================" -Color $Colors.Highlight
Write-Log "ЭТАП 5: Объединение конфигурационных файлов" -Color $Colors.Highlight
Write-Log "========================================`n" -Color $Colors.Highlight

$configFiles = @(
    @{ Source = "codeassistant/mcp.json"; Dest = "apps/cognitive_agent/mcp.json" },
    @{ Source = "codeassistant/ai-models.yaml"; Dest = "apps/cognitive_agent/config/ai-models.yaml" },
    @{ Source = "codeassistant/custom_modes.yaml"; Dest = "apps/cognitive_agent/config/custom_modes.yaml" },
    @{ Source = "codeassistant/context.md"; Dest = "apps/cognitive_agent/context.md" },
    @{ Source = "codeassistant/README.md"; Dest = "apps/cognitive_agent/README.codeassistant.md" },
    @{ Source = ".sourcecraft/ci.yaml"; Dest = "apps/cognitive_agent/config/ci.yaml" },
    @{ Source = ".sourcecraft/sites.yaml"; Dest = "apps/cognitive_agent/config/sites.yaml" },
    @{ Source = ".sourcecraft/README.md"; Dest = "apps/cognitive_agent/README.sourcecraft.md" }
)

$totalConfigsCopied = 0

foreach ($config in $configFiles) {
    if (Test-Path $config.Source) {
        $destDir = Split-Path $config.Dest -Parent
        if (-not (Test-Path $destDir)) {
            New-Item -ItemType Directory -Path $destDir | Out-Null
        }

        if (Test-Path $config.Dest) {
            $sourceHash = Get-File-Hash -FilePath $config.Source
            $destHash = Get-File-Hash -FilePath $config.Dest

            if ($sourceHash -ne $destHash) {
                Write-Log "  Обновлено: $([System.IO.Path]::GetFileName($config.Dest))" -Color $Colors.Highlight
                Copy-Item -Path $config.Source -Destination $config.Dest -Force
            }
            else {
                Write-Log "  Пропущено (идентично): $([System.IO.Path]::GetFileName($config.Dest))" -Color $Colors.Warning
            }
        }
        else {
            Write-Log "  Добавлено: $([System.IO.Path]::GetFileName($config.Dest))" -Color $Colors.Success
            Copy-Item -Path $config.Source -Destination $config.Dest
        }

        $totalConfigsCopied++
    }
}

Write-Log "`nВсего конфигурационных файлов обработано: $totalConfigsCopied" -Color $Colors.Success

# =============================================================================
# ЭТАП 6: Копирование документации
# =============================================================================
Write-Log "`n========================================" -Color $Colors.Highlight
Write-Log "ЭТАП 6: Копирование документации" -Color $Colors.Highlight
Write-Log "========================================`n" -Color $Colors.Highlight

$docsFiles = @(
    @{ Source = ".agents/README.md"; Dest = "apps/cognitive_agent/README.agents.md" },
    @{ Source = ".agents/USAGE.md"; Dest = "apps/cognitive_agent/USAGE.md" },
    @{ Source = ".agents/USER_GUIDE.md"; Dest = "apps/cognitive_agent/USER_GUIDE.md" },
    @{ Source = ".agents/IMPLEMENTATION_REPORT.md"; Dest = "apps/cognitive_agent/IMPLEMENTATION_REPORT.md" },
    @{ Source = ".agents/AUTONOMY_REPORT.md"; Dest = "apps/cognitive_agent/AUTONOMY_REPORT.md" }
)

foreach ($doc in $docsFiles) {
    if (Test-Path $doc.Source) {
        if (-not (Test-Path $doc.Dest)) {
            Write-Log "  Добавлено: $([System.IO.Path]::GetFileName($doc.Dest))" -Color $Colors.Success
            Copy-Item -Path $doc.Source -Destination $doc.Dest
        }
        else {
            Write-Log "  Пропущено (уже существует): $([System.IO.Path]::GetFileName($doc.Dest))" -Color $Colors.Warning
        }
    }
}

# =============================================================================
# ЭТАП 7: Обновление путей в коде
# =============================================================================
Write-Log "`n========================================" -Color $Colors.Highlight
Write-Log "ЭТАП 7: Обновление путей в коде" -Color $Colors.Highlight
Write-Log "========================================`n" -Color $Colors.Highlight

$filesToUpdate = @("apps/cognitive_agent/autonomous_agent.py")

foreach ($file in $filesToUpdate) {
    if (Test-Path $file) {
        $content = Get-Content $file -Raw

        if ($content -match "\.agents/") {
            Write-Log "  Обновление файла: $file" -Color $Colors.Info

            # Заменяем '.agents/' на 'apps/cognitive_agent/'
            $newContent = $content -replace "'\.agents/'", "'apps/cognitive_agent/'"

            Set-Content -Path $file -Value $newContent -NoNewline
            Write-Log "    → Замещено: '.agents/' → 'apps/cognitive_agent/'" -Color $Colors.Success
        }
        else {
            Write-Log "  Файл не требует обновления: $file" -Color $Colors.Warning
        }
    }
}

# =============================================================================
# ЭТАП 8: Итоговый отчет
# =============================================================================
$EndTime = Get-Date
$Duration = ($EndTime - $StartTime).TotalSeconds

Write-Log "`n========================================" -Color $Colors.Success
Write-Log "МИГРАЦИЯ ЗАВЕРШЕНА" -Color $Colors.Success
Write-Log "========================================`n" -Color $Colors.Success

Write-Log "Длительность: $([math]::Round($Duration, 2)) секунд" -Color $Colors.Info
Write-Log "Скиллов обработано: $totalSkillsCopied файлов" -Color $Colors.Info
Write-Log "Папок обработано: $totalDirsCopied элементов" -Color $Colors.Info
Write-Log "Конфигов обработано: $totalConfigsCopied файлов" -Color $Colors.Info

Write-Log "`n========================================" -Color $Colors.Highlight
Write-Log "СЛЕДУЮЩИЕ ШАГИ" -Color $Colors.Highlight
Write-Log "========================================`n" -Color $Colors.Highlight

Write-Log "1. Проверь объединённые файлы в apps/cognitive_agent/" -Color $Colors.Info
Write-Log "2. Проверь дубликаты скиллов (было $duplicateSkills дубликатов)" -Color $Colors.Warning
Write-Log "3. Запусти тесты: pytest apps/cognitive_agent/tests/" -Color $Colors.Info
Write-Log "4. Если всё ок, удали старые папки вручную:" -Color $Colors.Warning
Write-Log "   rm -rf .agents/ codeassistant/ .sourcecraft/" -Color $Colors.Error
Write-Log "5. Обновить .gitignore (добавить личные данные)" -Color $Colors.Info

Write-Log "`nГотово!" -Color $Colors.Success
