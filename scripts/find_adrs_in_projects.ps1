#Requires -Version 5.1
<#
.SYNOPSIS
    Поиск всех ADR (Architecture Decision Records) в C:\Projects.

.DESCRIPTION
    Рекурсивно сканирует C:\Projects включая скрытые папки.
    Ищет файлы по паттернам: ADR-*.md, *decision*.md, *архитектурное*решение*.md.
    Записывает результаты в .reports/adr_search_results.md.

.PARAMETER SearchPath
    Корневая папка для поиска (по умолчанию C:\Projects).

.PARAMETER OutputPath
    Куда записать отчёт (по умолчанию .reports/adr_search_results.md).

.EXAMPLE
    .\scripts\find_adrs_in_projects.ps1
    .\scripts\find_adrs_in_projects.ps1 -SearchPath "D:\Work" -OutputPath ".reports\custom.md"
#>

param(
    [string]$SearchPath = "C:\Projects",
    [string]$OutputPath = ".reports\adr_search_results.md"
)

$startTime = Get-Date
Write-Host "🔍 Сканирование $SearchPath на предмет ADR-файлов..." -ForegroundColor Cyan
Write-Host "   (включая скрытые папки)" -ForegroundColor Gray

# Проверка существования пути
if (-not (Test-Path $SearchPath)) {
    Write-Error "❌ Путь не найден: $SearchPath"
    exit 1
}

# Паттерны для поиска ADR
$patterns = @(
    "ADR-*.md"
    "adr-*.md"
    "*decision*.md"
    "*architecture-decision*.md"
    "*архитектурное*решение*.md"
)

# Исключения (чтобы не сканировать node_modules, .git и т.д.)
$excludeDirs = @('node_modules', '.git', '__pycache__', '.venv', 'venv', '.pytest_cache', '.mypy_cache', 'dist', 'build', 'target', '.idea', '.vscode', 'legacy', '.koda', '.reports')

$results = @()
$scanned = 0
$errors = @()

# Получаем все директории рекурсивно (включая скрытые)
try {
    $allDirs = Get-ChildItem -Path $SearchPath -Directory -Recurse -Force -ErrorAction SilentlyContinue |
        Where-Object {
            $dirName = $_.Name
            $excludeDirs -notcontains $dirName
        }
} catch {
    $errors += "Ошибка сканирования директорий: $_"
    $allDirs = @()
}

# Добавляем корневую папку
$allDirs = @((Get-Item $SearchPath)) + $allDirs

foreach ($dir in $allDirs) {
    $scanned++
    if ($scanned % 100 -eq 0) {
        Write-Host "   Сканировано папок: $scanned..." -ForegroundColor Gray
    }

    foreach ($pattern in $patterns) {
        try {
            $files = Get-ChildItem -Path $dir.FullName -Filter $pattern -File -Force -ErrorAction SilentlyContinue
            foreach ($file in $files) {
                # Проверяем, что файл действительно похож на ADR (по содержимому)
                $content = ""
                $isAdr = $false
                try {
                    $content = Get-Content -Path $file.FullName -TotalCount 5 -ErrorAction SilentlyContinue | Out-String
                    $isAdr = $content -match '(?i)(ADR|architecture decision|архитектурное решение|статус|контекст|решение)'
                } catch {
                    # Файл бинарный или недоступен — пропускаем проверку содержимого
                    $isAdr = $true  # По имени уже похоже на ADR
                }

                if ($isAdr) {
                    $results += [PSCustomObject]@{
                        Path        = $file.FullName
                        Name        = $file.Name
                        Size        = $file.Length
                        Modified    = $file.LastWriteTime.ToString('yyyy-MM-dd HH:mm')
                        Directory   = $dir.FullName
                        Pattern     = $pattern
                    }
                }
            }
        } catch {
            $errors += "Ошибка в $($dir.FullName): $_"
        }
    }
}

# Сортировка: сначала по имени, потом по пути
$results = $results | Sort-Object Name, Path

# Удаляем дубликаты (если файл попал под несколько паттернов)
$results = $results | Sort-Object Path -Unique

# Формирование отчёта
$duration = (Get-Date) - $startTime
$report = @(
    "# 🔍 Результаты поиска ADR"
    ""
    "**Дата сканирования:** $($startTime.ToString('yyyy-MM-dd HH:mm:ss'))"
    "**Путь:** ``$SearchPath``"
    "**Длительность:** $($duration.ToString('mm\:ss\.fff'))"
    "**Просканировано папок:** $scanned"
    "**Найдено ADR-файлов:** $($results.Count)"
    ""
)

if ($errors.Count -gt 0) {
    $report += "## ⚠️ Ошибки при сканировании"
    $report += ""
    foreach ($err in $errors | Select-Object -First 10) {
        $report += "- $err"
    }
    $report += ""
}

if ($results.Count -eq 0) {
    $report += "## Результат"
    $report += ""
    $report += "❌ ADR-файлы не найдены."
    $report += ""
} else {
    # Группировка по папке
    $grouped = $results | Group-Object Directory | Sort-Object Name

    $report += "## 📁 Найденные ADR по папкам"
    $report += ""

    foreach ($group in $grouped) {
        $report += "### ``$($group.Name)``"
        $report += ""
        $report += "| Файл | Размер | Изменён |"
        $report += "|------|--------|---------|"

        foreach ($file in $group.Group | Sort-Object Name) {
            $sizeKb = [math]::Round($file.Size / 1KB, 1)
            $report += "| ``$($file.Name)`` | $($sizeKb) KB | $($file.Modified) |"
        }
        $report += ""
    }

    # Полный список
    $report += "## 📋 Полный список"
    $report += ""
    $report += "| # | Файл | Путь | Размер |"
    $report += "|---|------|------|--------|"

    $i = 1
    foreach ($file in $results) {
        $sizeKb = [math]::Round($file.Size / 1KB, 1)
        $report += "| $i | ``$($file.Name)`` | ``$($file.Path)`` | $($sizeKb) KB |"
        $i++
    }
    $report += ""
}

# Запись отчёта
$reportPath = Resolve-Path $OutputPath -ErrorAction SilentlyContinue
if (-not $reportPath) {
    $reportDir = Split-Path $OutputPath -Parent
    if ($reportDir -and -not (Test-Path $reportDir)) {
        New-Item -ItemType Directory -Path $reportDir -Force | Out-Null
    }
    $reportPath = $OutputPath
}

$report -join "`n" | Out-File -FilePath $reportPath -Encoding UTF8

Write-Host ""
Write-Host "✅ Готово!" -ForegroundColor Green
Write-Host "   Найдено ADR: $($results.Count)" -ForegroundColor White
Write-Host "   Просканировано папок: $scanned" -ForegroundColor Gray
Write-Host "   Отчёт: $reportPath" -ForegroundColor Cyan
