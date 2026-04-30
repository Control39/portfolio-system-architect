# diagnostic-renames.ps1
# Поиск всех упоминаний старых имён компонентов

$RepoRoot = Get-Location

# Единственные ключи — без дублей
$OldNames = @(
    "it-compass",
    "Айти компас",
    "Cloud-Reason",
    "cloud-reason",
    "src_cloud_reason",
    "arch-compass",
    "ArchCompass",
    "Cloud Reason",
    "auth_service"
)

$ExcludedDirs = @(".git", "__pycache__", "venv", ".venv", "node_modules", ".archive-backup-20260425_181308")

Write-Host "🔍 Начинаем диагностику устаревших имён в $RepoRoot..." -ForegroundColor Cyan

foreach ($old in $OldNames) {
    Write-Host "`n🔎 Ищем: '$old'" -ForegroundColor Yellow

    # По содержимому файлов
    $filesWithContent = Get-ChildItem -Recurse -Exclude $ExcludedDirs -File | Where-Object {
        $_.PSIsContainer -eq $false
    } | ForEach-Object {
        $path = $_.FullName
        try {
            $content = Get-Content $path -Raw -Encoding UTF8 -ErrorAction SilentlyContinue
            if ($content -and $content -match [regex]::Escape($old)) {
                $matches = Select-String -Path $path -Pattern $old -AllMatches -Encoding UTF8
                $matches | ForEach-Object {
                    Write-Host "📄 $($_.Path):$($_.LineNumber)" -ForegroundColor Green
                    Write-Host "   ➤ $($_.Line.Trim())" -ForegroundColor Gray
                }
            }
        } catch {
            Write-Warning "⚠️ Ошибка чтения файла $path : $_"
        }
    }

    # По имени файлов и папок
    Write-Host "📁 Ищем в именах файлов/папок с '$old'..." -ForegroundColor Magenta
    Get-ChildItem -Recurse -Exclude $ExcludedDirs -ErrorAction SilentlyContinue | Where-Object {
        $_.Name -like "*$old*"
    } | ForEach-Object {
        Write-Host "   💼 $($_.FullName)" -ForegroundColor White
    }
}

Write-Host "`n✅ Диагностика завершена. Результат сохранён в 'diagnostic-before-rename.txt'" -ForegroundColor Green
