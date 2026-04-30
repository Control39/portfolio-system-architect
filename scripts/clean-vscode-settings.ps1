<#
.SYNOPSIS
Очистка настроек Visual Studio Code для решения проблем с Pyright и конфликтующими конфигурациями.

.DESCRIPTION
Этот скрипт удаляет все настройки VSCode, кэш и расширения с компьютера,
чтобы решить проблемы с разбросанными настройками и конфликтами конфигураций.

.PARAMETER Backup
Создать резервную копию перед удалением (по умолчанию: true)

.PARAMETER SkipConfirmation
Пропустить подтверждение удаления (по умолчанию: false)

.EXAMPLE
.\clean-vscode-settings.ps1
Удаляет настройки VSCode с подтверждением и создает резервную копию.

.EXAMPLE
.\clean-vscode-settings.ps1 -Backup $false -SkipConfirmation $true
Удаляет настройки без резервной копии и без подтверждения.

.NOTES
Требует прав администратора для удаления некоторых системных файлов.
#>

[CmdletBinding()]
param(
    [bool]$Backup = $true,
    [bool]$SkipConfirmation = $false
)

# Проверка прав администратора
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Warning "Скрипт запущен без прав администратора. Некоторые файлы могут быть недоступны для удаления."
}

# Пути к настройкам VSCode
$vscodePaths = @(
    # Пользовательские настройки
    "$env:APPDATA\Code",
    "$env:APPDATA\Code - Insiders",
    "$env:APPDATA\VSCodium",

    # Локальные настройки
    "$env:LOCALAPPDATA\Programs\Microsoft VS Code",
    "$env:LOCALAPPDATA\Programs\VSCodium",

    # Кэш и временные файлы
    "$env:LOCALAPPDATA\Microsoft\vscode-cpptools",
    "$env:LOCALAPPDATA\Microsoft\VSCodeCache",

    # Настройки в профиле пользователя
    "$env:USERPROFILE\.vscode",
    "$env:USERPROFILE\.vscode-insiders",
    "$env:USERPROFILE\.vscode-oss",

    # Кэш расширений
    "$env:USERPROFILE\.vscode\extensions",
    "$env:USERPROFILE\.vscode-insiders\extensions"
)

# Функция для создания резервной копии
function Backup-VSCodeSettings {
    param([string]$BackupDir)

    Write-Host "Создание резервной копии настроек VSCode..." -ForegroundColor Cyan

    $backupPaths = @()
    foreach ($path in $vscodePaths) {
        if (Test-Path $path) {
            $backupPaths += $path
        }
    }

    if ($backupPaths.Count -eq 0) {
        Write-Host "Настройки VSCode не найдены для резервного копирования." -ForegroundColor Yellow
        return
    }

    $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $backupFile = Join-Path $BackupDir "vscode-backup-$timestamp.zip"

    try {
        # Создаем временную директорию для копирования
        $tempDir = Join-Path $env:TEMP "vscode-backup-$timestamp"
        New-Item -ItemType Directory -Path $tempDir -Force | Out-Null

        foreach ($path in $backupPaths) {
            $name = Split-Path $path -Leaf
            $dest = Join-Path $tempDir $name
            Write-Host "  Копирование: $path" -ForegroundColor Gray

            if (Test-Path $path) {
                Copy-Item -Path $path -Destination $dest -Recurse -Force -ErrorAction SilentlyContinue
            }
        }

        # Архивируем
        Compress-Archive -Path "$tempDir\*" -DestinationPath $backupFile -CompressionLevel Optimal
        Write-Host "Резервная копия создана: $backupFile" -ForegroundColor Green

        # Очищаем временную директорию
        Remove-Item -Path $tempDir -Recurse -Force -ErrorAction SilentlyContinue

        return $backupFile
    }
    catch {
        Write-Error "Ошибка при создании резервной копии: $_"
        return $null
    }
}

# Функция удаления настроек
function Remove-VSCodeSettings {
    Write-Host "Удаление настроек VSCode..." -ForegroundColor Cyan

    $deletedCount = 0
    $errorCount = 0

    foreach ($path in $vscodePaths) {
        if (Test-Path $path) {
            Write-Host "  Удаление: $path" -ForegroundColor Gray
            try {
                Remove-Item -Path $path -Recurse -Force -ErrorAction Stop
                $deletedCount++
            }
            catch {
                Write-Warning "    Не удалось удалить: $_"
                $errorCount++
            }
        }
    }

    # Дополнительные очистки реестра (опционально)
    if ($isAdmin) {
        Write-Host "Очистка записей реестра VSCode..." -ForegroundColor Cyan
        $regPaths = @(
            "HKCU:\Software\Microsoft\VSCode",
            "HKCU:\Software\Microsoft\VSCodeInsiders",
            "HKCU:\Software\Classes\VSCode*",
            "HKCU:\Software\Classes\Applications\Code.exe",
            "HKCU:\Software\Classes\Applications\CodeInsiders.exe"
        )

        foreach ($regPath in $regPaths) {
            if (Test-Path $regPath) {
                try {
                    Remove-Item -Path $regPath -Recurse -Force -ErrorAction SilentlyContinue
                }
                catch {
                    # Игнорируем ошибки реестра
                }
            }
        }
    }

    Write-Host "Удалено директорий: $deletedCount, ошибок: $errorCount" -ForegroundColor Green
}

# Функция проверки и переустановки
function Reinstall-VSCode {
    Write-Host "`nРекомендации по переустановке VSCode:" -ForegroundColor Cyan
    Write-Host "1. Скачайте свежий установщик с https://code.visualstudio.com/" -ForegroundColor Yellow
    Write-Host "2. Запустите установку с параметрами:" -ForegroundColor Yellow
    Write-Host "   - Не импортировать старые настройки" -ForegroundColor Yellow
    Write-Host "   - Установить в чистую директорию" -ForegroundColor Yellow
    Write-Host "   - Добавить в PATH" -ForegroundColor Yellow
    Write-Host "3. После установки откройте проект и выберите интерпретатор Python" -ForegroundColor Yellow
    Write-Host "4. Установите рекомендуемые расширения из .vscode/extensions.json" -ForegroundColor Yellow

    $choice = Read-Host "`nХотите открыть страницу загрузки VSCode? (y/n)"
    if ($choice -eq 'y' -or $choice -eq 'Y') {
        Start-Process "https://code.visualstudio.com/download"
    }
}

# Основной скрипт
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Очистка настроек Visual Studio Code" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Подтверждение
if (-not $SkipConfirmation) {
    Write-Host "`nЭтот скрипт удалит ВСЕ настройки VSCode с вашего компьютера." -ForegroundColor Red
    Write-Host "Будут удалены:" -ForegroundColor Yellow
    Write-Host "  - Настройки пользователя" -ForegroundColor Yellow
    Write-Host "  - Кэш и временные файлы" -ForegroundColor Yellow
    Write-Host "  - Установленные расширения" -ForegroundColor Yellow
    Write-Host "  - Конфигурации проектов" -ForegroundColor Yellow

    $confirm = Read-Host "`nПродолжить? (y/n)"
    if ($confirm -ne 'y' -and $confirm -ne 'Y') {
        Write-Host "Отменено пользователем." -ForegroundColor Yellow
        exit 0
    }
}

# Создание резервной копии
$backupFile = $null
if ($Backup) {
    $backupDir = Join-Path $env:USERPROFILE "vscode-backups"
    New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
    $backupFile = Backup-VSCodeSettings -BackupDir $backupDir
}

# Удаление настроек
Remove-VSCodeSettings

# Рекомендации
Reinstall-VSCode

# Итог
Write-Host "`n==========================================" -ForegroundColor Green
Write-Host "Очистка завершена!" -ForegroundColor Green
if ($backupFile) {
    Write-Host "Резервная копия: $backupFile" -ForegroundColor Green
}
Write-Host "`nДальнейшие действия:" -ForegroundColor Cyan
Write-Host "1. Перезагрузите компьютер" -ForegroundColor Yellow
Write-Host "2. Переустановите VSCode" -ForegroundColor Yellow
Write-Host "3. Откройте проект и проверьте работу Pyright" -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Green
