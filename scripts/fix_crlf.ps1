# fix_crlf.ps1 - Убрать CRLF из shell скриптов
$scripts = @(
    "scripts/ddd_full_scan.sh",
    "scripts/ddd_show_dependencies.sh",
    "scripts/ddd_show_issues.sh",
    "scripts/ddd_analyze_context.sh",
    "scripts/01_start_agent.sh",
    "scripts/02_start_agent_foreground.sh",
    "scripts/03_stop_agent.sh",
    "scripts/04_agent_status.sh"
)

foreach ($file in $scripts) {
    if (Test-Path $file) {
        $content = Get-Content $file -Raw
        # Убрать CR
        $content = $content -replace "`r", ""
        [System.IO.File]::WriteAllText($file, $content, [System.Text.Encoding]::UTF8)
        Write-Host "✅ Исправлен: $file"
    } else {
        Write-Host "⚠️  Файл не найден: $file"
    }
}

Write-Host "`nГотово!"
