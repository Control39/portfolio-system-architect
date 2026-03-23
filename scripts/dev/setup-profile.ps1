param([switch]$Force)

$profilePath = $PROFILE

if (-not (Test-Path $profilePath)) {
    Write-Host "Создаю профиль PowerShell..." -ForegroundColor Yellow
    New-Item -Path $profilePath -Type File -Force | Out-Null
}

$repoRoot = git rev-parse --show-toplevel 2>$null
if (-not $repoRoot) {
    $repoRoot = Split-Path $PSScriptRoot -Parent
}
$treeScript = Join-Path $repoRoot 'tools/tree.ps1'

$profileContent = Get-Content $profilePath -Raw -ErrorAction SilentlyContinue

if ($profileContent -notmatch [regex]::Escape($treeScript)) {
    if (-not $Force -and $profileContent) {
        Write-Host "Найден профиль. Добавить tree? (Y/N):" -ForegroundColor Cyan
        $response = Read-Host
        if ($response -notmatch '^[Yy]') { exit 0 }
    }
    
    $addLine = "# Tree utility from portfolio-system-architect`n. '$treeScript'`n"
    if ($profileContent) {
        Set-Content -Path $profilePath -Value ($addLine + $profileContent)
    } else {
        Set-Content -Path $profilePath -Value $addLine
    }
    Write-Host "✅ Tree добавлен в $profilePath" -ForegroundColor Green
} else {
    Write-Host "✅ Tree уже в профиле" -ForegroundColor Green
}

Write-Host "Перезагрузите PowerShell или выполните: . `$PROFILE" -ForegroundColor Cyan

