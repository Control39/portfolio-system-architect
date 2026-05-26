# Обновление Bearer Token для GigaCode
# Запустите этот скрипт, чтобы обновить токен в VS Code

Write-Host "🔄 Обновление Bearer Token для GigaCode..." -ForegroundColor Cyan

# Получите новый токен
Write-Host "`n📝 Получите новый токен:" -ForegroundColor Yellow
Write-Host "  1. Зайдите на https://gigachat.dev/" -ForegroundColor White
Write-Host "  2. Авторизуйтесь через Sber ID" -ForegroundColor White
Write-Host "  3. Перейдите в раздел 'API Keys' или 'Токены'" -ForegroundColor White
Write-Host "  4. Создайте новый токен или скопируйте существующий" -ForegroundColor White
Write-Host "  5. Скопируйте токен в буфер обмена" -ForegroundColor White

Write-Host "`n📋 Токен скопирован?" -ForegroundColor Yellow
$confirm = Read-Host "Нажмите Enter, когда токен будет в буфере обмена"

# Получаем токен из буфера обмена
try {
    $newToken = Get-Clipboard -ErrorAction Stop
    Write-Host "✅ Токен получен из буфера обмена" -ForegroundColor Green
} catch {
    Write-Host "❌ Не удалось получить токен из буфера обмена" -ForegroundColor Red
    $newToken = Read-Host "Введите токен вручную"
}

# Проверяем файл настроек
$settingsFile = ".vscode/settings.json"

if (-not (Test-Path $settingsFile)) {
    Write-Host "❌ Файл $settingsFile не найден" -ForegroundColor Red
    exit 1
}

# Читаем текущие настройки
$settingsContent = Get-Content $settingsFile -Raw

# Обновляем токен
if ($settingsContent -match '"gigacode\.bearerToken"\s*:\s*"[^"]*"') {
    $oldToken = $matches[0]
    $newSettings = $settingsContent -replace '"gigacode\.bearerToken"\s*:\s*"[^"]*"', "`"gigacode.bearerToken`": `"$newToken`""
    
    # Сохраняем новые настройки
    Set-Content -Path $settingsFile -Value $newSettings -NoNewline
    
    Write-Host "`n✅ Токен обновлён в $settingsFile" -ForegroundColor Green
} else {
    # Добавляем токен, если его нет
    $newSettings = $settingsContent.TrimEnd("}") + ",`n  `"gigacode.bearerToken`": `"$newToken`"`n}"
    Set-Content -Path $settingsFile -Value $newSettings -NoNewline
    
    Write-Host "`n✅ Токен добавлен в $settingsFile" -ForegroundColor Green
}

# Проверяем
Write-Host "`n🔍 Проверка обновления..." -ForegroundColor Yellow
$updatedContent = Get-Content $settingsFile -Raw
if ($updatedContent -match '"gigacode\.bearerToken"') {
    Write-Host "✅ Токен успешно обновлён" -ForegroundColor Green
} else {
    Write-Host "❌ Не удалось обновить токен" -ForegroundColor Red
    exit 1
}

# Рекомендации
Write-Host "`n💡 Следующие шаги:" -ForegroundColor Cyan
Write-Host "  1. Перезагрузите VS Code" -ForegroundColor White
Write-Host "  2. Откройте палету команд (Ctrl+Shift+P)" -ForegroundColor White
Write-Host "  3. Выберите 'GigaCode: Restart'" -ForegroundColor White
Write-Host "  4. Проверьте работу в чате" -ForegroundColor White

Write-Host "`n✅ Готово!" -ForegroundColor Green
