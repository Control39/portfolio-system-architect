# Простой скрипт для обновления токена GigaCode
# Запускайте вручную, когда расширение перестаёт работать

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Обновление токена GigaCode" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$scriptPath = "C:\repo\tools\devtools\.devtools\.gigacode\update_vscode_token.py"
$venvPython = "C:\repo\.venv\Scripts\python.exe"

if (-not (Test-Path $scriptPath)) {
    Write-Host "❌ Ошибка: Скрипт не найден: $scriptPath" -ForegroundColor Red
    exit 1
}

Write-Host "`n🔄 Запуск обновления..." -ForegroundColor Yellow
& $venvPython "C:\repo\scripts\ai\run_gigacode_update.py"

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ Токен успешно обновлён!" -ForegroundColor Green
    Write-Host "`n💡 Следующие шаги:" -ForegroundColor Cyan
    Write-Host "  1. Перезагрузите VS Code (Ctrl+Shift+P → 'Developer: Reload Window')" -ForegroundColor White
    Write-Host "  2. Или перезапустите расширение: GigaCode: Restart" -ForegroundColor White
} else {
    Write-Host "`n❌ Ошибка при обновлении токена" -ForegroundColor Red
    Write-Host "  Попробуйте вручную получить новые OAuth credentials" -ForegroundColor Yellow
    exit 1
}
