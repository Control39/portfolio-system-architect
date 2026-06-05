# fix-dockerfiles.ps1 - Автоматически добавляет git в Dockerfile, где его нет
$files = Get-ChildItem -Path apps -Filter "Dockerfile" -Recurse
$fixed = 0
$skipped = 0

foreach ($file in $files) {
    $content = Get-Content $file.FullName -Raw

    # Пропускаем, если уже есть git
    if ($content -match "apt-get.*install.*git") {
        Write-Host "✅ Пропуск (уже есть git): $($file.FullName)" -ForegroundColor Green
        $skipped++
        continue
    }

    # Пропускаем, если нет pip install (не Python-образ)
    if ($content -notmatch "pip install") {
        Write-Host "⏭️  Пропуск (нет pip): $($file.FullName)" -ForegroundColor Cyan
        $skipped++
        continue
    }

    # Находим первую строку с pip install и добавляем git перед ней
    $lines = Get-Content $file.FullName
    $newLines = @()
    $added = $false

    foreach ($line in $lines) {
        # Добавляем git перед первой командой pip install или COPY requirements
        if (-not $added -and ($line -match "^\s*RUN.*pip install" -or $line -match "^\s*COPY.*requirements")) {
            # Определяем отступ
            $indent = if ($line -match "^(\s*)") { $matches[1] } else { "" }
            $newLines += "${indent}# Install git for pip dependencies from git+https://"
            $newLines += "${indent}RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*"
            $newLines += ""
            $added = $true
        }
        $newLines += $line
    }

    # Сохраняем изменения
    $newLines | Set-Content $file.FullName -Encoding UTF8
    Write-Host "🔧 Исправлено: $($file.FullName)" -ForegroundColor Yellow
    $fixed++
}

Write-Host "`n📊 Итого: исправлено $fixed, пропущено $skipped" -ForegroundColor Magenta
