# Добавить алиас в профиль
$profilePath = $PROFILE
$aliasLine = 'Set-Alias -Name py -Value "C:\repo\.venv\Scripts\python.exe" -Scope Global'

# Проверить, есть ли уже
$content = Get-Content $profilePath -ErrorAction SilentlyContinue
if ($content -notcontains $aliasLine) {
    Add-Content -Path $profilePath -Value $aliasLine
    Write-Host "Добавлен алиас 'py' в профиль" -ForegroundColor Green
} else {
    Write-Host "Алиас уже существует" -ForegroundColor Yellow
}

Write-Host "Профиль: $profilePath"
Write-Host "Теперь выполните: . $PROFILE"
