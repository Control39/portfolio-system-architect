# migrate-agents-safe.ps1 v2 - Bulletproof version
$ErrorActionPreference = "Continue"  # Не прерываться на ошибках
$MigrationReport = @()

# === КОНФИГУРАЦИЯ ===
$Destination = "apps/cognitive_agent"
$Sources = @(".agents", "codeassistant", ".sourcecraft")

$FoldersToMigrate = @(
    "skills", "config", "rules", "teacher", "tools",
    "workflows", "integrations", "dashboards", "plans",
    "changelogs", "scripts", "tests"
)

# === БЕЗОПАСНЫЕ ФУНКЦИИ ===
function Get-FileHashSafe($path) {
    try {
        # Проверяем, что это именно файл, а не папка
        if (-not (Test-Path $path -PathType Leaf)) { return $null }
        return (Get-FileHash $path -Algorithm SHA256 -ErrorAction Stop).Hash
    }
    catch {
        return $null
    }
}

function Copy-WithConflictResolution($src, $dst, $sourceName) {
    try {
        $dstDir = Split-Path $dst -Parent
        if (-not (Test-Path $dstDir)) {
            New-Item -ItemType Directory -Path $dstDir -Force | Out-Null
        }

        # Проверка конфликта типов: файл vs папка
        if (Test-Path $dst -PathType Container) {
            # Целевой путь - это папка, а мы копируем файл!
            $ext = [System.IO.Path]::GetExtension($dst)
            $base = [System.IO.Path]::GetFileNameWithoutExtension($dst)
            if ([string]::IsNullOrEmpty($base)) { $base = [System.IO.Path]::GetFileName($dst) }
            $conflictPath = Join-Path $dstDir "${base}_file_from_${sourceName}${ext}"
            Copy-Item $src $conflictPath -Force
            return "CONFLICT_FILE_VS_DIR"
        }

        if (-not (Test-Path $dst)) {
            Copy-Item $src $dst -Force
            return "COPIED"
        }

        $srcHash = Get-FileHashSafe $src
        $dstHash = Get-FileHashSafe $dst

        if ($srcHash -and $dstHash -and $srcHash -eq $dstHash) { return "IDENTICAL" }

        # Файлы отличаются — создаём версию с суффиксом
        $ext = [System.IO.Path]::GetExtension($dst)
        $base = [System.IO.Path]::GetFileNameWithoutExtension($dst)
        $conflictPath = Join-Path $dstDir "${base}_from_${sourceName}${ext}"
        Copy-Item $src $conflictPath -Force
        return "CONFLICT_SAVED"
    }
    catch {
        Write-Host "    ❌ Ошибка: $_" -ForegroundColor Red
        return "ERROR"
    }
}

# === ОСНОВНАЯ МИГРАЦИЯ ===
Write-Host "🚀 Начало безопасной миграции в $Destination" -ForegroundColor Cyan

foreach ($source in $Sources) {
    if (-not (Test-Path $source)) { continue }
    $sourceName = $source -replace '[^a-zA-Z0-9]', '_'
    Write-Host "`n📂 Обработка: $source" -ForegroundColor Green

    foreach ($folder in $FoldersToMigrate) {
        $srcFolder = Join-Path $source $folder
        if (-not (Test-Path $srcFolder)) { continue }

        $dstFolder = Join-Path $Destination $folder
        Write-Host "  📁 $folder" -ForegroundColor DarkCyan

        $files = Get-ChildItem $srcFolder -Recurse -File -ErrorAction SilentlyContinue
        foreach ($file in $files) {
            try {
                $srcPath = (Resolve-Path $srcFolder).Path
                $relPath = $file.FullName.Substring($srcPath.Length)
                $dstFile = Join-Path $dstFolder $relPath

                $result = Copy-WithConflictResolution $file.FullName $dstFile $sourceName
                $MigrationReport += [PSCustomObject]@{
                    Source = $source; Folder = $folder; File = $relPath; Result = $result
                }

                $icon = switch -Wildcard ($result) {
                    "COPIED" { "✅" }
                    "IDENTICAL" { "⚪" }
                    "CONFLICT*" { "⚠️" }
                    default { "❌" }
                }
                Write-Host "    $icon $($file.Name) → $result" -ForegroundColor Gray
            }
            catch {
                Write-Host "    ❌ Пропуск $($file.Name): $_" -ForegroundColor Red
            }
        }
    }
}

# === ОТЧЁТ ===
Write-Host "`n📊 Итоговый отчёт" -ForegroundColor Cyan
$MigrationReport | Group-Object Result | Select-Object Name, Count | Format-Table -AutoSize

$conflicts = $MigrationReport | Where-Object { $_.Result -like "CONFLICT*" }
if ($conflicts) {
    Write-Host "`n⚠️  Файлы с конфликтами (требуют ручного ревью):" -ForegroundColor Yellow
    $conflicts | ForEach-Object {
        Write-Host "  - $($_.Source)/$($_.Folder)/$($_.File) [$($_.Result)]" -ForegroundColor Yellow
    }
}

Write-Host "`n✅ Миграция завершена. Старые папки НЕ удалены." -ForegroundColor Green
