$archive = Test-Path 'C:\repo\apps\ai_config_manager\.archive-js-legacy'
$pkg = Test-Path 'C:\repo\apps\ai_config_manager\package.json'
$api = Test-Path 'C:\repo\apps\ai_config_manager\api'
$components = Test-Path 'C:\repo\apps\ai_config_manager\components'

Write-Host "=== Проверка структуры ai_config_manager ==="
Write-Host "Archive exists: $archive"
Write-Host "package.json exists: $pkg"
Write-Host "api folder exists: $api"
Write-Host "components folder exists: $components"

# Список оставшихся элементов
Write-Host "`n=== Оставшиеся элементы ==="
Get-ChildItem 'C:\repo\apps\ai_config_manager' -Name | ForEach-Object { Write-Host $_ }
