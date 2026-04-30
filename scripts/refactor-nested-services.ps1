function Merge-ServiceFolder {
    param(
        [Parameter(Mandatory=$true)]
        [string]$ServicePath,

        [Parameter(Mandatory=$true)]
        [string]$NestedFolderName
    )

    $nestedPath = Join-Path $ServicePath $NestedFolderName
    $tempPath = Join-Path $ServicePath "$($NestedFolderName)_temp"

    # Проверка существования папок
    if (-not (Test-Path $ServicePath)) {
        Write-Host "Путь сервиса не существует: $ServicePath" -ForegroundColor Yellow
        return $false
    }

    if (-not (Test-Path $nestedPath)) {
        return $true
    }

    try {
        Write-Host "Обработка: $ServicePath" -ForegroundColor Cyan

        # Перемещаем файлы
        $files = Get-ChildItem $nestedPath -File
        if ($files.Count -gt 0) {
            $files | Move-Item -Destination $ServicePath -Force
            Write-Host "  -> Файлы перемещены"
        }

        # Перемещаем/объединяем папки
        $dirs = Get-ChildItem $nestedPath -Directory
        foreach ($dir in $dirs) {
            $sourceDir = Join-Path $nestedPath $dir.Name
            $targetDir = Join-Path $ServicePath $dir.Name
            if (Test-Path $targetDir) {
                Get-ChildItem $sourceDir -Recurse | Move-Item -Destination $targetDir -Force
            } else {
                Move-Item -Path $sourceDir -Destination $targetDir -Force
            }
        }

        # Удаляем пустую вложенную папку
        Remove-Item $nestedPath -Recurse -Force
        Write-Host "  -> Папка $nestedPath удалена" -ForegroundColor Green

    } catch {
        Write-Error "Ошибка при обработке $ServicePath : $_"
        return $false
    }
}

# --- ЗАПУСК АВТОМАТИЧЕСКОГО РЕФАКТОРИНГА ---

$rootApps = "C:\Users\Z\DeveloperEnvironment\projects\portfolio-system-architect\apps"

# Список сервисов из таблицы агента
$servicesToFix = @(
    "ai-config-manager",
    "auth-service",
    "career-development",
    "decision-engine",
    "job-automation-agent",
    "knowledge-graph",
    "mcp-server",
    "ml-model-registry",
    "template-service",
    "thought-architecture"
)

Write-Host "=== НАЧАЛО АВТОМАТИЧЕСКОГО РЕФАКТОРИНГА ===" -ForegroundColor Yellow

foreach ($svc in $servicesToFix) {
    $svcPath = Join-Path $rootApps $svc
    # Пробуем разные варианты написания вложенной папки (с дефисом и подчеркиванием)
    $nestedName = if ($svc -match "-") { $svc -replace "-", "_" } else { $svc -replace "_", "-" }

    # Если сервис называется с дефисом, вложенная часто тоже с дефисом (или наоборот)
    # Проверяем стандартный вариант (имя в имени)
    $possibleNested = @($svc)
    if ($svc -match "-") { $possibleNested += $svc -replace "-", "_" }

    foreach ($nested in $possibleNested) {
        $nestedFullPath = Join-Path $svcPath $nested
        if (Test-Path $nestedFullPath) {
            Write-Host "Обнаружено дублирование: $nestedFullPath"
            Merge-ServiceFolder -ServicePath $svcPath -NestedFolderName $nested
            break # Если нашли и схлопнули, переходим к следующему сервису
        }
    }
}

# Особый случай: career-development/src/src/
$cdSrcPath = Join-Path $rootApps "career-development\src"
if (Test-Path (Join-Path $cdSrcPath "src")) {
    Write-Host "Исправление вложенности src/src/..." -ForegroundColor Cyan
    Merge-ServiceFolder -ServicePath $cdSrcPath -NestedFolderName "src"
}

Write-Host "=== РЕФАКТОРИНГ ЗАВЕРШЕН ===" -ForegroundColor Yellow
Write-Host "Пожалуйста, проверь результаты через 'git status' и запусти тесты."
