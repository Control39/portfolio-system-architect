# 1. Пути для поиска (дубликаты и несуществующие отфильтруются автоматически)
$RawPaths = @(
    "C:\Users\Z\my-ecosystem-FINAL",
    "C:\Users\Z\DeveloperEnvironment\projects\portfolio-system-architect-BACKUP-20260406",
    "C:\Users\Z\DeveloperEnvironment\projects\Новая папка\portfolio-system-architect",
    "C:\Users\Z\DeveloperEnvironment\projects\Новая папка\portfolio-system-architect\apps",
    "C:\Users\Z\DeveloperEnvironment\projects\Новая папка",
    "C:\Users\Z\Desktop",
    "C:\Backup\my-ecosystem-FINAL_backup",
    "C:\Users\Z\.streamlit",
    "C:\Users\Z\BACKUP_ALL_VERSIONS_20260306_121602",
    "C:\Users\Z\backup-cloud-reason",
    "C:\Users\Z\",
    "C:\Users\Z\portfolio-system-architect",
    "C:\Users\Z\portfolio-backup",
    "C:\Users\Z\temp_sourcecraft_test"
)

$SearchPaths = $RawPaths | Where-Object { Test-Path $_ } | Select-Object -Unique

# 2. Исключения (системные и временные папки, чтобы поиск по C:\Users\Z\ не завис)
$ExcludeFolders = @(
    "__pycache__", ".git", "node_modules", ".pytest_cache", ".vscode",
    "AppData", "OneDrive", "Pictures", "Downloads", "Music", "Videos",
    "Contacts", "Favorites", "Links", "Saved Games", "Searches", "NTUSER"
)
$ExcludeRegex = '({0})' -f (($ExcludeFolders | ForEach-Object { [regex]::Escape($_) }) -join '|')

# 3. Категории поиска и Regex-паттерны
$SearchConfig = @{
    "DB_Models"      = "(?i)(Mapped|mapped_column|__tablename__|relationship|ForeignKey).*(progress|record|log|track|history|level)"
    "Pydantic_Schemas" = "(?i)(BaseModel|pydantic|Field).*(progress|skill|level|before|after|notes)"
    "API_Routes"     = "(?i)(@(app|router)\.(post|put|get|delete)|async def|def ).*(progress|track|skill|update|log)"
    "Services"       = "(?i)(update_progress|log_skill|track_level|session\.add|db\.commit|def .*progress)"
    "Migrations"     = "(?i)(op\.create_table|op\.add_column|progress|skill_log|history|alembic_version)"
    "Tests"          = "(?i)(def test_|assert|mock).*(progress|track|level|skill)"
}

$Results = @{}
foreach ($key in $SearchConfig.Keys) { $Results[$key] = @() }

# 4. Рекурсивный поиск
Write-Host " Начинаю рекурсивный поиск по $($SearchPaths.Count) путям..." -ForegroundColor Cyan
$TotalFiles = 0

foreach ($path in $SearchPaths) {
    Write-Host "`n📂 Сканирую: $path" -ForegroundColor Yellow

    # Поиск только .py файлов, рекурсивно, с фильтрацией исключений
    $Files = Get-ChildItem -Path $path -Filter "*.py" -Recurse -ErrorAction SilentlyContinue |
             Where-Object { $_.FullName -notmatch $ExcludeRegex }

    $TotalFiles += $Files.Count
    $Progress = 0

    foreach ($file in $Files) {
        $Progress++
        if ($Progress % 500 -eq 0) { Write-Host "   Обработано файлов: $Progress" -ForegroundColor DarkGray }

        foreach ($category in $SearchConfig.Keys) {
            try {
                $match = Select-String -Path $file.FullName -Pattern $SearchConfig[$category] -Quiet -ErrorAction SilentlyContinue
                if ($match) {
                    $Results[$category] += [PSCustomObject]@{
                        Path = $file.FullName
                        Category = $category
                    }
                }
            } catch { continue }
        }
    }
}

# 5. Вывод результатов
Write-Host "`n`n📊 ИТОГОВЫЙ ОТЧЁТ" -ForegroundColor Green
Write-Host "==================" -ForegroundColor Green
Write-Host "Всего файлов просканировано: $TotalFiles"

foreach ($category in $Results.Keys) {
    $count = $Results[$category].Count
    if ($count -gt 0) {
        Write-Host "`n✅ $category ($count совпадений):" -ForegroundColor Cyan
        $Results[$category] | Select-Object -First 10 | ForEach-Object {
            Write-Host "   • $($_.Path)" -ForegroundColor White
        }
        if ($count -gt 10) { Write-Host "   ... и ещё $($count - 10) файлов" -ForegroundColor DarkGray }
    } else {
        Write-Host "`n❌ $category: не найдено" -ForegroundColor DarkGray
    }
}

# 6. Сохранение полного отчёта
$ReportPath = "progress_search_report_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
$Results | ConvertTo-Json -Depth 3 | Out-File $ReportPath -Encoding UTF8
Write-Host "`n💾 Полный отчёт сохранён: $reportPath" -ForegroundColor Green
