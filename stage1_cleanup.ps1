# Этап 1: Очистка структуры ai_config_manager
Write-Host "=== Этап 1: Очистка структуры ===" -ForegroundColor Cyan

$servicePath = "C:\repo\apps\ai_config_manager"
$archivePath = "$servicePath\.archive-js-legacy"

# 1. Создаём архив
Write-Host "1. Создаём архив: $archivePath"
New-Item -ItemType Directory -Force -Path $archivePath | Out-Null

# 2. Перемещаем JS-артефакты
Write-Host "2. Перемещаем JS-артефакты в архив..."
$jsItems = @(
    "__tests__",
    "preload.js",
    "package.json",
    "package-lock.json",
    "components",
    "renderer",
    "public"
)

foreach ($item in $jsItems) {
    $source = Join-Path $servicePath $item
    if (Test-Path $source) {
        Move-Item -Path $source -Destination $archivePath -Force
        Write-Host "   Перемещено: $item"
    } else {
        Write-Host "   Пропущено (не существует): $item" -ForegroundColor Yellow
    }
}

# 3. Удаляем пустые/ненужные папки
Write-Host "3. Удаляем пустые папки..."
$emptyFolders = @(
    "api",
    "models",
    "services",
    "adapters",
    "main"
)

foreach ($folder in $emptyFolders) {
    $path = Join-Path $servicePath $folder
    if (Test-Path $path) {
        Remove-Item -Path $path -Recurse -Force
        Write-Host "   Удалено: $folder"
    } else {
        Write-Host "   Пропущено (не существует): $folder" -ForegroundColor Yellow
    }
}

# 4. Создаём __init__.py если нет
Write-Host "4. Создаём __init__.py..."
$initFiles = @(
    Join-Path $servicePath "src\__init__.py",
    Join-Path $servicePath "tests\__init__.py"
)

foreach ($initFile in $initFiles) {
    if (-not (Test-Path $initFile)) {
        "" | Out-File -FilePath $initFile -Encoding UTF8
        Write-Host "   Создано: $initFile"
    } else {
        Write-Host "   Уже существует: $initFile" -ForegroundColor Yellow
    }
}

# 5. Добавляем архив в .gitignore
Write-Host "5. Добавляем архив в .gitignore..."
$gitignorePath = Join-Path $servicePath ".gitignore"
if (Test-Path $gitignorePath) {
    $content = Get-Content $gitignorePath
    if ($content -notcontains ".archive-js-legacy/") {
        ".archive-js-legacy/" | Add-Content $gitignorePath
        Write-Host "   Добавлено в .gitignore"
    } else {
        Write-Host "   Уже есть в .gitignore" -ForegroundColor Yellow
    }
} else {
    ".archive-js-legacy/" | Out-File -FilePath $gitignorePath -Encoding UTF8
    Write-Host "   Создан .gitignore"
}

# Итоговая проверка
Write-Host "`n=== Итоговая структура ===" -ForegroundColor Green
Get-ChildItem $servicePath -Name | Sort-Object | ForEach-Object { Write-Host "  $_" }

Write-Host "`n=== Этап 1 завершён ===" -ForegroundColor Green
