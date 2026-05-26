# Скрипт для настройки алиаса venv в PowerShell

$profilePath = $PROFILE

# Проверить существование профиля
if (-not (Test-Path $profilePath)) {
    Write-Host "Создаю профиль PowerShell: $profilePath" -ForegroundColor Green
    New-Item -ItemType File -Path $profilePath -Force | Out-Null
}

# Проверить, есть ли уже алиас
$profileContent = Get-Content $profilePath -ErrorAction SilentlyContinue
if ($profileContent -match "Set-Alias.*py.*venv") {
    Write-Host "Алиас 'py' уже настроен в профиле" -ForegroundColor Yellow
} else {
    # Добавить алиас
    $aliasLine = "`n# Venv alias - использует Python из .venv`nSet-Alias -Name py -Value `"C:\repo\.venv\Scripts\python.exe`" -Scope Global`n"
    Add-Content -Path $profilePath -Value $aliasLine
    Write-Host "Алиас 'py' добавлен в профиль: $profilePath" -ForegroundColor Green
}

Write-Host "`nПерезагрузите PowerShell или выполните:" -ForegroundColor Cyan
Write-Host ". \$profilePath" -ForegroundColor White
Write-Host "`nЗатем проверьте:" -ForegroundColor Cyan
Write-Host "py --version" -ForegroundColor White
