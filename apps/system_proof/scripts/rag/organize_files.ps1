# Organize Files Script
# Скрипт организации файлов

param(
    [Parameter(Mandatory=$true)]
    [string]$SourcePath,
    [Parameter(Mandatory=$true)]
    [string]$DestinationPath,
    [switch]$IncludeSubdirectories
)
# Функция для логирования

# Функция для логирования
function Write-Log {
    param([string]$Message)
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$Timestamp] $Message"
}

# Проверка существования исходной папки
if (!(Test-Path $SourcePath)) {
    Write-Log "Ошибка: Исходная папка не найдена - $SourcePath"
    exit 1
}

# Создание папки назначения
if (!(Test-Path $DestinationPath)) {
    New-Item -ItemType Directory -Path $DestinationPath | Out-Null
    Write-Log "Создана папка назначения: $DestinationPath"
}

Write-Log "Начало организации файлов"
Write-Log "Исходная папка: $SourcePath"
Write-Log "Папка назначения: $DestinationPath"

try {
    # Получение списка файлов
    if ($IncludeSubdirectories) {
        $Files = Get-ChildItem -Path $SourcePath -File -Recurse
    } else {
        $Files = Get-ChildItem -Path $SourcePath -File
    }

    Write-Log "Найдено $($Files.Count) файлов для организации"

    # Счетчики для статистики
    $ProcessedCount = 0
    $ErrorCount = 0

    foreach ($File in $Files) {
        try {
            # Определение категории файла по расширению
            $Category = switch ($File.Extension) {
                {$_ -in ".pdf", ".docx", ".doc", ".txt"} { "documents" }
                {$_ -in ".xlsx", ".xls", ".csv"} { "spreadsheets" }
                {$_ -in ".pptx", ".ppt"} { "presentations" }
                {$_ -in ".jpg", ".jpeg", ".png", ".gif", ".bmp"} { "images" }
                {$_ -in ".mp4", ".avi", ".mkv", ".mov"} { "videos" }
                {$_ -in ".mp3", ".wav", ".flac"} { "audio" }
                default { "other" }
            }

            # Создание папки категории
            $CategoryPath = Join-Path $DestinationPath $Category
            if (!(Test-Path $CategoryPath)) {
                New-Item -ItemType Directory -Path $CategoryPath | Out-Null
            }

            # Перемещение файла
            $DestinationFile = Join-Path $CategoryPath $File.Name
            Move-Item -Path $File.FullName -Destination $DestinationFile -Force

            $ProcessedCount++
            Write-Log "Организован файл: $($File.Name) -> $Category"
        } catch {
            $ErrorCount++
            Write-Log "Ошибка при организации файла $($File.Name): $($_.Exception.Message)"
        }
    }

    Write-Log "Организация файлов завершена"
    Write-Log "Успешно обработано: $ProcessedCount файлов"
    if ($ErrorCount -gt 0) {
        Write-Log "Ошибок: $ErrorCount"
    }
} catch {
    Write-Log "Ошибка в процессе организации файлов: $($_.Exception.Message)"
    exit 1
}
