# Путь к вашему проекту
$rootPath = "C:\Users\Z\Desktop\my-ecosystem-CLONE"

# Проверяем, существует ли путь
if (-not (Test-Path $rootPath)) {
    Write-Error "Путь не найден: $rootPath"
    exit 1
}

Write-Host "🔍 Поиск всех папок .git в $rootPath..." -ForegroundColor Yellow

# Находим все папки .git рекурсивно
$gitFolders = Get-ChildItem -Path $rootPath -Recurse -Directory -Filter ".git" -ErrorAction SilentlyContinue

if ($gitFolders.Count -eq 0) {
    Write-Host "✅ Папки .git не найдены. Нечего удалять." -ForegroundColor Green
    exit 0
}

# Выводим список найденных папок
Write-Host "🗑️  Найдено папок .git: $($gitFolders.Count)" -ForegroundColor Cyan
foreach ($folder in $gitFolders) {
    Write-Host "   → $($folder.FullName)"
}

# Подтверждение перед удалением
$confirm = Read-Host "Вы уверены, что хотите удалить все эти папки .git? (да/нет)"
if ($confirm -notmatch "^да$|^y$|^yes$") {
    Write-Host "❌ Удаление отменено." -ForegroundColor Red
    exit 0
}

# Удаляем каждую папку .git
foreach ($folder in $gitFolders) {
    try {
        Remove-Item -Path $folder.FullName -Recurse -Force -ErrorAction Stop
        Write-Host "✅ Удалено: $($folder.FullName)" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ Ошибка при удалении: $($folder.FullName) | $_" -ForegroundColor Red
    }
}

Write-Host "🎉 Все папки .git удалены. Проект больше не содержит вложенных репозиториев." -ForegroundColor Green
