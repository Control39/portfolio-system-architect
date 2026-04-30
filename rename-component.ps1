# rename-component.ps1
# Безопасное переименование: cloud-reason → decision-engine
# Режим WhatIf: сначала показывает изменения, потом применяет
# Запуск: .\rename-component.ps1

param(
    [switch]$WhatIf = $true,   # По умолчанию только показываем, что будет сделано
    [switch]$Confirm = $false  # Требовать подтверждение перед выполнением
)

$RepoRoot = Get-Location
$OldName = "cloud-reason"
$NewName = "decision-engine"
$LogFile = Join-Path $RepoRoot "rename-log.txt"

# --- Логирование ---
function Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content -Path $LogFile -Value "[$timestamp] $Message"
    Write-Host $Message -ForegroundColor Gray
}

Log "START: Rename '$OldName' → '$NewName'. WhatIf: $WhatIf"

# --- ШАГ 1: Проверка папки ---
$OldPath = Join-Path $RepoRoot "apps/$OldName"
$NewPath = Join-Path $RepoRoot "apps/$NewName"

if (-not (Test-Path $OldPath)) {
    $msg = "❌ Папка не найдена: $OldPath"
    Log $msg
    Write-Error $msg
    exit 1
}

Write-Host "📁 Обнаружена папка: $OldPath" -ForegroundColor Green
Log "FOUND: $OldPath"

if ($WhatIf) {
    Write-Host "📝 [Сухой запуск] Будет переименовано: $OldPath → $NewPath" -ForegroundColor Yellow
    Log "WHATIF: Would rename folder to $NewPath"
} else {
    if ($Confirm) {
        $reply = Read-Host "Выполнить переименование папки? (y/N)"
        if ($reply -notmatch "^y|yes$") { exit }
    }
    try {
        Rename-Item -Path $OldPath -NewName $NewName
        Write-Host "✅ Папка переименована: $OldPath → $NewPath" -ForegroundColor Green
        Log "RENAMED FOLDER: $OldPath → $NewPath"
    } catch {
        $msg = "❌ Ошибка переименования папки: $_"
        Log $msg
        Write-Error $msg
        exit 1
    }
}

# --- ШАГ 2: Поиск файлов для замены ---
$SearchDirs = @("apps", "deployment", "docker", "scripts", "docs", "config", "tests")
$Excluded = @(
    "node_modules", "__pycache__", ".venv", "venv",
    ".git", "*.log", "*.tmp", "dist", "build", "*.png", "*.jpg", "objects.txt"
)

$ChangedFiles = 0
$TotalMatches = 0

foreach ($dir in $SearchDirs) {
    $path = Join-Path $RepoRoot $dir
    if (Test-Path $path) {
        $files = Get-ChildItem -Path $path -Recurse -File | Where-Object {
            $Excluded -notcontains $_.Name -and
            $Excluded -notcontains $_.Directory.Name
        }

        foreach ($file in $files) {
            try {
                $content = Get-Content -Path $file.FullName -Raw -Encoding UTF8
                $matches = 0

                if ($content -match [regex]::Escape($OldName)) { $matches++ }
                if ($content -match "Cloud-Reason") { $matches++ }

                if ($matches -gt 0) {
                    $TotalMatches += $matches
                    $relPath = $file.FullName.Substring($RepoRoot.Length).TrimStart('\')

                    if ($WhatIf) {
                        Write-Host "🔍 [WhatIf] Найдено в: $relPath" -ForegroundColor Cyan
                        Log "WHATIF: Found match in $relPath"
                    } else {
                        $newContent = $content `
                            -replace [regex]::Escape($OldName), $NewName `
                            -replace "Cloud-Reason", "Decision-Engine"

                        Set-Content -Path $file.FullName -Value $newContent -Encoding UTF8
                        $ChangedFiles++
                        Write-Host "✏️ Обновлено: $relPath" -ForegroundColor Green
                        Log "UPDATED: $relPath"
                    }
                }
            } catch {
                Write-Warning "⚠️ Не удалось обработать: $($file.Name)"
                Log "ERROR: Failed to process $($file.FullName) - $_"
            }
        }
    }
}

# --- Финал ---
Write-Host "`n🎉 Готово!" -ForegroundColor Green
if ($WhatIf) {
    Write-Host "📌 Найдено совпадений: $TotalMatches" -ForegroundColor Yellow
    Write-Host "📌 Файлов затронуто: $ChangedFiles (в режиме WhatIf не изменяются)" -ForegroundColor Yellow
    Write-Host "💡 Чтобы применить изменения, запустите: .\rename-component.ps1 -WhatIf:`$false" -ForegroundColor White
    Log "SUMMARY: WhatIf mode. $TotalMatches matches in approx $ChangedFiles files."
} else {
    Write-Host "✅ Изменено файлов: $ChangedFiles" -ForegroundColor Green
    Write-Host "📄 Лог сохранён: $LogFile" -ForegroundColor White
    Log "SUMMARY: Completed. $ChangedFiles files updated."
}
