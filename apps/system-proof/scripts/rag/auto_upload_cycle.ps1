# Auto Upload Cycle Script
# Скрипт автоматического цикла загрузки

param(
    [string]$WatchFolder = ".\documents\incoming",
    [string]$ProcessedFolder = ".\documents\processed",
    [int]$CheckInterval = 60
)
# Функция для логирования

# Функция для логирования
function Write-Log {
    param([string]$Message)
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$Timestamp] $Message"
}

# Создание необходимых папок
if (!(Test-Path $WatchFolder)) {
    New-Item -ItemType Directory -Path $WatchFolder | Out-Null
    Write-Log "Создана папка для наблюдения: $WatchFolder"
}

if (!(Test-Path $ProcessedFolder)) {
    New-Item -ItemType Directory -Path $ProcessedFolder | Out-Null
    Write-Log "Создана папка для обработанных файлов: $ProcessedFolder"
}

Write-Log "Запуск цикла автоматической загрузки"
Write-Log "Наблюдение за папкой: $WatchFolder"
Write-Log "Интервал проверки: $CheckInterval секунд"

try {
    while ($true) {
        Write-Log "Проверка новых файлов..."

        # Получение списка новых файлов
        $NewFiles = Get-ChildItem -Path $WatchFolder -File -Recurse | Where-Object {
            $_.LastWriteTime -gt (Get-Date).AddMinutes(-5)
        }

        if ($NewFiles.Count -gt 0) {
            Write-Log "Найдено $($NewFiles.Count) новых файлов для обработки"

            foreach ($File in $NewFiles) {
                Write-Log "Обработка файла: $($File.Name)"

                # Здесь будет логика загрузки файла
                # Для демонстрации просто перемещаем файл
                $DestinationPath = Join-Path $ProcessedFolder $File.Name
                Move-Item -Path $File.FullName -Destination $DestinationPath -Force
                Write-Log "Файл перемещен в: $DestinationPath"
            }
        } else {
            Write-Log "Новых файлов не найдено"
        }

        Write-Log "Ожидание следующей проверки..."
        Start-Sleep -Seconds $CheckInterval
    }
} catch {
    Write-Log "Ошибка в цикле автоматической загрузки: $($_.Exception.Message)"
    exit 1
}
