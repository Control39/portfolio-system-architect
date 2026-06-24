# Читаем отчёт Python с кодировкой UTF-8
$reportLines = Get-Content "duplicates_report_before_deletion.txt" -Encoding UTF8

$currentHash = $null
$fileCount = 0
$mismatchCount = 0

Write-Host "Starting hash verification..."
Write-Host ""

foreach ($line in $reportLines) {
    # Ищем строки с хэшем: "Группа X (хэш: ...)" ИЛИ "Group X (hash: ...)"
    if ($line -match "Группа \d+ \(хэш: ([a-f0-9]{64})\)" -or $line -match "Group \d+ \(hash: ([a-f0-9]{64})\)") {
        $currentHash = $Matches[1].ToUpper()
        Write-Host "Checking group with hash: $currentHash"
        continue
    }

    # Ищем строки с путями файлов (начинаются с "  • ")
    if ($line.StartsWith("  • ")) {
        # Извлекаем путь (убираем "  • " в начале)
        $filepath = $line.Substring(3).Trim()

        try {
            # Вычисляем хэш файла через PowerShell
            $psHash = (Get-FileHash $filepath -Algorithm SHA256).Hash
            $fileCount++

            if ($psHash -eq $currentHash) {
                Write-Host "✓ OK: $filepath"
            } else {
                Write-Host "✗ MISMATCH: $filepath"
                Write-Host "  Python hash: $currentHash"
                Write-Host "  PS hash:   $psHash"
                $mismatchCount++
            }
        } catch {
            Write-Host "⚠ ERROR reading: $filepath"
            Write-Host "  Error: $($_.Exception.Message)"
            $mismatchCount++
        }
    }
}

Write-Host ""
Write-Host "Verification completed!"
Write-Host "Files checked: $fileCount"
Write-Host "Mismatches: $mismatchCount"

if ($mismatchCount -eq 0) {
    Write-Host "✅ All hashes match!" -ForegroundColor Green
} else {
    Write-Host "❌ Mismatches found!" -ForegroundColor Red
}
