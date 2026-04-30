# full-cleanup-old-names.ps1
# Безопасная замена всех устаревших имён → decision-engine

param(
    [switch]$WhatIf = $true
)

$RepoRoot = Get-Location
$LogFile = "$RepoRoot/cleanup-old-names.log"

function Log { Add-Content -Path $LogFile -Value "[$(Get-Date -Format 'HH:mm:ss')] $($args[0])" }

Log "START: Cleanup old names. WhatIf: $WhatIf"

# --- Список паттернов для замены (с сохранением регистра) ---
# Каждое правило будет обрабатываться отдельно
$Replacements = @(
    @{ Old = "cloud-reason"; New = "decision-engine" }
    @{ Old = "Cloud-Reason"; New = "Decision-Engine" }
    @{ Old = "src_cloud_reason"; New = "src_decision_engine" }
    @{ Old = "cloud_reason"; New = "decision_engine" }
    @{ Old = "apps/cloud-reason"; New = "apps/decision-engine" }
    @{ Old = "apps\cloud-reason"; New = "apps\decision-engine" }
)

# --- Поиск файлов ---
$SearchPatterns = "*.yml", "*.yaml", "*.py", "*.ps1", "*.sh", "*.md", "*.json", "*.txt", "Dockerfile", "*.dockerfile"
$ExcludeDirs = ".git", "node_modules", "__pycache__", "venv", ".venv", "dist", "build"

$ChangedFiles = 0

# --- Получаем все подходящие файлы ---
$Files = Get-ChildItem -Path $RepoRoot -Include $SearchPatterns -Recurse -File | Where-Object {
    $path = $_.DirectoryName
    ($ExcludeDirs | ForEach-Object { $path -notlike "*$_*" }) -notcontains $false
}

foreach ($file in $Files) {
    try {
        $content = Get-Content -Path $file.FullName -Raw -Encoding UTF8
        $original = $content

        $replacementsInFile = 0

        # Применяем каждое правило
        foreach ($rule in $Replacements) {
            $old = $rule.Old
            $new = $rule.New

            # Проверяем, есть ли совпадение
            if ($content -match [regex]::Escape($old)) {
                $content = $content -replace [regex]::Escape($old), $new
                $replacementsInFile++
            }
        }

        # Если были изменения
        if ($content -ne $original) {
            $relPath = $file.FullName.Substring($RepoRoot.Length).TrimStart('\')

            if ($WhatIf) {
                Write-Host "🔍 [WhatIf] Обновится: $relPath ($replacementsInFile)" -ForegroundColor Yellow
                Log "WHATIF: Will update $relPath ($replacementsInFile replacements)"
            } else {
                Set-Content -Path $file.FullName -Value $content -Encoding UTF8
                $ChangedFiles++
                Log "UPDATED: $relPath"
            }
        }
    } catch {
        Write-Warning "⚠️ Ошибка при обработке: $($file.Name)"
        Log "ERROR: Failed to process $($file.Name) - $_"
    }
}

# --- Финал ---
if ($WhatIf) {
    Write-Host "`n📌 Режим просмотра завершён." -ForegroundColor Cyan
    Write-Host "💡 Чтобы применить изменения, запустите:" -ForegroundColor White
    Write-Host "   .\full-cleanup-old-names.ps1 -WhatIf:`$false" -ForegroundColor White
} else {
    Write-Host "`n✅ Готово! Изменено файлов: $ChangedFiles" -ForegroundColor Green
}
Log "FINISH: $ChangedFiles files updated"
