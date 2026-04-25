param(
    [string]$serviceName = "it-compass",
    [switch]$dryRun = $false
)

$baseDir = "C:/Users/Z/DeveloperEnvironment/projects/portfolio-system-architect/apps"
$servicePath = Join-Path $baseDir $serviceName
$nestedPath = Join-Path $servicePath $serviceName

Write-Host "Начало обработки сервиса: $serviceName" -ForegroundColor Green
Write-Host "Базовый путь: $servicePath" -ForegroundColor Yellow
Write-Host "Вложенный путь: $nestedPath" -ForegroundColor Yellow

# 1. Проверка существования путей
if (-not (Test-Path $servicePath)) {
    Write-Error "Базовый путь не существует: $servicePath"
    exit 1
}
if (-not (Test-Path $nestedPath)) {
    Write-Host "Вложенная папка $nestedPath не найдена. Пропуск." -ForegroundColor Yellow
    exit 0
}

# 2. Получение содержимого вложенной папки (исключая саму вложенную папку)
$itemsToMove = Get-ChildItem $nestedPath | Where-Object { $_.Name -ne $serviceName }
if ($null -eq $itemsToMove) {
    Write-Host "Нет файлов/папок для перемещения из $nestedPath" -ForegroundColor Yellow
    exit 0
}

# 3. Dry Run: показать, что будет перемещено
Write-Host "`nDry Run - следующие элементы будут перемещены:" -ForegroundColor Cyan
$itemsToMove | ForEach-Object { Write-Host "  -> $($_.Name)" }
Write-Host "Из: $nestedPath"
Write-Host "В: $servicePath"
Write-Host "Вложенная папка '$serviceName' будет удалена, если станет пустой." -ForegroundColor Cyan

if ($dryRun) {
    Write-Host "`nРежим Dry Run завершен. Изменений не внесено." -ForegroundColor Cyan
    exit 0
}

# 4. Подтверждение перед выполнением
$confirmation = Read-Host "`nВыполнить перемещение? (yes/no)"
if ($confirmation -ne 'yes') {
    Write-Host "Операция отменена." -ForegroundColor Red
    exit 0
}

try {
    # 5. Перемещение каждого элемента
    $itemsToMove | ForEach-Object {
        $item = $_
        $destination = Join-Path $servicePath $item.Name

        if (Test-Path $destination) {
            Write-Error "Ошибка: Элемент с именем '$($item.Name)' уже существует в $servicePath"
            throw "Конфликт имен"
        }

        Write-Host "Перемещение: $($item.Name) ..." -ForegroundColor Yellow
        git mv $item.FullName $servicePath
        if ($LASTEXITCODE -ne 0) {
            throw "git mv завершился с ошибкой"
        }
    }

    # 6. Удаление вложенной папки, если она пуста
    if ((Get-ChildItem $nestedPath -Recurse | Measure-Object).Count -eq 0) {
        Write-Host "Удаление пустой папки: $nestedPath" -ForegroundColor Yellow
        Remove-Item $nestedPath
    } else {
        Write-Warning "Папка $nestedPath не пуста после перемещения. Проверьте вручную."
    }

    Write-Host "✅ Упрощение структуры для $serviceName завершено." -ForegroundColor Green

    # 7. Шаг проверки
    Write-Host "`n=== ШАГ ПРОВЕРКИ ===" -ForegroundColor Magenta
    Write-Host "1. Выполните 'git status' для проверки изменений." -ForegroundColor Magenta
    Write-Host "2. Запустите тесты сервиса, чтобы убедиться в работоспособности." -ForegroundColor Magenta
    Write-Host "   Пример: cd apps/$serviceName; python -m pytest tests/" -ForegroundColor Magenta
    Write-Host "3. Проверьте ключевые импорты в коде (например, в main.py, __init__.py)." -ForegroundColor Magenta

} catch {
    Write-Error "Произошла ошибка: $_"
    Write-Host "Попробуйте отменить изменения с помощью 'git reset --hard'." -ForegroundColor Red
}