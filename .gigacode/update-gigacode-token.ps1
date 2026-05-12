# PowerShell script для обновления GigaChat токена в VS Code
# Запустите: .\update-gigacode-token.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Обновление GigaChat токена для VS Code" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$tokenScript = Join-Path $scriptDir "update_vscode_token.py"

if (-not (Test-Path $tokenScript)) {
    Write-Host "❌ Ошибка: скрипт update_vscode_token.py не найден" -ForegroundColor Red
    exit 1
}

Write-Host "`n🔄 Запуск обновления токена..." -ForegroundColor Yellow

try {
    & python $tokenScript
    $exitCode = $LASTEXITCODE

    if ($exitCode -eq 0) {
        Write-Host "`n✅ Успешно!" -ForegroundColor Green
        Write-Host "`nПерезагрузите VS Code:" -ForegroundColor Yellow
        Write-Host "  Ctrl+Shift+P → 'Developer: Reload Window'" -ForegroundColor White
    } else {
        Write-Host "`n❌ Ошибка при обновлении токена" -ForegroundColor Red
        exit $exitCode
    }
} catch {
    Write-Host "❌ Ошибка: $_" -ForegroundColor Red
    exit 1
}
