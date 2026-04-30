# src/core/logging/StructuredLogger.psm1
# StructuredLogger - асинхронное структурированное логирование с маскированием секретов

enum LogLevel {
    Debug
    Info
    Warning
    Error
    Critical
}

enum LogOutputFormat {
    JSON
    CSV
    Plain
}

class LogEntry {
    [DateTime] $Timestamp
    [LogLevel] $Level
    [string] $Message
    [string] $Category
    [hashtable] $Properties
    [string] $Exception
    [string] $StackTrace

    LogEntry([LogLevel]$level, [string]$message, [string]$category = '', [hashtable]$properties = $null, [Exception]$exception = $null) {
        $this.Timestamp = Get-Date
        $this.Level = $level
        $this.Message = $message
        $this.Category = $category
        $this.Properties = if ($properties) { $properties } else { @{} }
        if ($exception) {
            $this.Exception = $exception.Message
            $this.StackTrace = $exception.StackTrace
        }
    }
}

class StructuredLogger {
    hidden static [System.Collections.Concurrent.ConcurrentQueue[LogEntry]] $LogQueue = $null
    hidden static [System.Threading.Tasks.Task] $BackgroundTask = $null
    hidden static [System.Threading.CancellationTokenSource] $CancellationTokenSource = $null
    hidden static [string] $LogDirectory = ''
    hidden static [LogOutputFormat] $OutputFormat = [LogOutputFormat]::JSON
    hidden static [int] $MaxFileSizeMB = 10
    hidden static [int] $RetentionDays = 30
    hidden static [bool] $ConsoleOutput = $true
    hidden static [bool] $Initialized = $false
    hidden static [string] $CurrentLogFile = ''

    static [void] Initialize([hashtable]$config = @{}) {
        if ([StructuredLogger]::Initialized) {
            Write-Warning "StructuredLogger уже инициализирован"
            return
        }

        # Настройки из конфигурации
        [StructuredLogger]::LogDirectory = if ($config.LogDirectory) {
            $config.LogDirectory
        } else {
            Join-Path $PSScriptRoot '..\..\logs'
        }

        [StructuredLogger]::OutputFormat = if ($config.OutputFormat) {
            [LogOutputFormat]$config.OutputFormat
        } else {
            [LogOutputFormat]::JSON
        }

        [StructuredLogger]::MaxFileSizeMB = if ($config.MaxFileSizeMB) { $config.MaxFileSizeMB } else { 10 }
        [StructuredLogger]::RetentionDays = if ($config.RetentionDays) { $config.RetentionDays } else { 30 }
        [StructuredLogger]::ConsoleOutput = if ($config.ConsoleOutput -ne $null) { $config.ConsoleOutput } else { $true }

        # Создание директории логов
        if (-not (Test-Path [StructuredLogger]::LogDirectory)) {
            New-Item -ItemType Directory -Path [StructuredLogger]::LogDirectory -Force | Out-Null
        }

        # Инициализация очереди
        [StructuredLogger]::LogQueue = [System.Collections.Concurrent.ConcurrentQueue[LogEntry]]::new()

        # Создание токена отмены
        [StructuredLogger]::CancellationTokenSource = [System.Threading.CancellationTokenSource]::new()

        # Запуск фоновой задачи
        [StructuredLogger]::StartBackgroundTask()

        [StructuredLogger]::Initialized = $true

        # Логируем инициализацию
        [StructuredLogger]::Log([LogLevel]::Info, "StructuredLogger инициализирован", "Logger", @{
            LogDirectory = [StructuredLogger]::LogDirectory
            OutputFormat = [StructuredLogger]::OutputFormat
        })
    }

    static [void] Log([LogLevel]$level, [string]$message, [string]$category = '', [hashtable]$properties = $null, [Exception]$exception = $null) {
        if (-not [StructuredLogger]::Initialized) {
            # Fallback на консольный вывод, если логгер не инициализирован
            $color = switch ($level) {
                'Debug' { 'Gray' }
                'Info' { 'White' }
                'Warning' { 'Yellow' }
                'Error' { 'Red' }
                'Critical' { 'Magenta' }
            }
            Write-Host "[$level] $message" -ForegroundColor $color
            return
        }

        # Маскирование секретов в properties перед логированием
        $maskedProperties = if ($properties) {
            try {
                [SecretManager]::MaskSecretsInObject($properties)
            } catch {
                # Если SecretManager недоступен, используем исходные properties
                $properties
            }
        } else {
            $null
        }

        # Маскирование секретов в сообщении
        $maskedMessage = try {
            [SecretManager]::MaskSecretsInObject($message)
        } catch {
            # Если SecretManager недоступен, используем исходное сообщение
            $message
        }

        $entry = [LogEntry]::new($level, $maskedMessage, $category, $maskedProperties, $exception)

        # Добавление в очередь (неблокирующее)
        if ([StructuredLogger]::LogQueue) {
            [StructuredLogger]::LogQueue.Enqueue($entry)
        }

        # Консольный вывод (синхронный, для немедленной обратной связи)
        if ([StructuredLogger]::ConsoleOutput) {
            [StructuredLogger]::WriteToConsole($entry)
        }
    }

    hidden static [void] WriteToConsole([LogEntry]$entry) {
        $color = switch ($entry.Level) {
            'Debug' { 'Gray' }
            'Info' { 'White' }
            'Warning' { 'Yellow' }
            'Error' { 'Red' }
            'Critical' { 'Magenta' }
        }

        $timestamp = $entry.Timestamp.ToString('yyyy-MM-dd HH:mm:ss')
        $output = "[$timestamp] [$($entry.Level)]"

        if ($entry.Category) {
            $output += " [$($entry.Category)]"
        }

        $output += " $($entry.Message)"

        if ($entry.Exception) {
            $output += "`n   Exception: $($entry.Exception)"
        }

        Write-Host $output -ForegroundColor $color
    }

    hidden static [void] StartBackgroundTask() {
        $cancellationToken = [StructuredLogger]::CancellationTokenSource.Token

        [StructuredLogger]::BackgroundTask = [System.Threading.Tasks.Task]::Run({
            param($token)

            while (-not $token.IsCancellationRequested) {
                $entriesToWrite = @()

                # Извлечение записей из очереди (пакетная обработка)
                $entry = $null
                while ([StructuredLogger]::LogQueue -and [StructuredLogger]::LogQueue.Count -gt 0 -and $entriesToWrite.Count -lt 100) {
                    if ([StructuredLogger]::LogQueue.TryDequeue([ref]$entry)) {
                        $entriesToWrite += $entry
                    }
                }

                # Запись в файл
                if ($entriesToWrite.Count -gt 0) {
                    [StructuredLogger]::WriteToFile($entriesToWrite)
                }

                # Пауза перед следующей итерацией
                Start-Sleep -Milliseconds 100
            }

            # Запись оставшихся записей при остановке
            $remainingEntries = @()
            $entry = $null
            while ([StructuredLogger]::LogQueue -and [StructuredLogger]::LogQueue.Count -gt 0) {
                if ([StructuredLogger]::LogQueue.TryDequeue([ref]$entry)) {
                    $remainingEntries += $entry
                }
            }

            if ($remainingEntries.Count -gt 0) {
                [StructuredLogger]::WriteToFile($remainingEntries)
            }
        }, $cancellationToken)
    }

    hidden static [void] WriteToFile([array]$entries) {
        if ($entries.Count -eq 0) {
            return
        }

        # Определение текущего файла лога
        $logFileName = "arch-compass_$(Get-Date -Format 'yyyyMMdd').log"
        $logFilePath = Join-Path [StructuredLogger]::LogDirectory $logFileName

        # Проверка размера файла и ротация
        if (Test-Path $logFilePath) {
            $fileInfo = Get-Item $logFilePath
            $fileSizeMB = $fileInfo.Length / 1MB

            if ($fileSizeMB -ge [StructuredLogger]::MaxFileSizeMB) {
                # Ротация: переименование старого файла
                $rotatedName = "arch-compass_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
                $rotatedPath = Join-Path [StructuredLogger]::LogDirectory $rotatedName
                Move-Item -Path $logFilePath -Destination $rotatedPath -Force
            }
        }

        # Запись в файл в зависимости от формата
        $content = switch ([StructuredLogger]::OutputFormat) {
            'JSON' {
                $entries | ForEach-Object {
                    @{
                        Timestamp = $_.Timestamp.ToString('o')
                        Level = $_.Level.ToString()
                        Message = $_.Message
                        Category = $_.Category
                        Properties = $_.Properties
                        Exception = $_.Exception
                        StackTrace = $_.StackTrace
                    } | ConvertTo-Json -Compress
                } | Out-String
            }
            'CSV' {
                $header = "Timestamp,Level,Message,Category,Properties,Exception"
                $lines = @($header)
                foreach ($entry in $entries) {
                    $props = ($entry.Properties | ConvertTo-Json -Compress) -replace '"', '""'
                    $line = "$($entry.Timestamp.ToString('o')),$($entry.Level),$($entry.Message),$($entry.Category),`"$props`",$($entry.Exception)"
                    $lines += $line
                }
                $lines -join "`n"
            }
            'Plain' {
                $entries | ForEach-Object {
                    $timestamp = $_.Timestamp.ToString('yyyy-MM-dd HH:mm:ss')
                    $line = "[$timestamp] [$($_.Level)]"
                    if ($_.Category) {
                        $line += " [$($_.Category)]"
                    }
                    $line += " $($_.Message)"
                    if ($_.Properties.Count -gt 0) {
                        $line += " | Properties: $($_.Properties | ConvertTo-Json -Compress)"
                    }
                    if ($_.Exception) {
                        $line += " | Exception: $($_.Exception)"
                    }
                    $line
                } | Out-String
            }
        }

        # Атомарная запись в файл
        try {
            Add-Content -Path $logFilePath -Value $content -Encoding UTF8 -ErrorAction Stop
        } catch {
            Write-Warning "Не удалось записать в лог-файл: $_"
        }

        # Очистка старых логов
        [StructuredLogger]::CleanupOldLogs()
    }

    hidden static [void] CleanupOldLogs() {
        $cutoffDate = (Get-Date).AddDays(-[StructuredLogger]::RetentionDays)

        Get-ChildItem -Path [StructuredLogger]::LogDirectory -Filter "arch-compass_*.log" -ErrorAction SilentlyContinue |
            Where-Object { $_.LastWriteTime -lt $cutoffDate } |
            Remove-Item -Force -ErrorAction SilentlyContinue
    }

    static [void] Stop() {
        if (-not [StructuredLogger]::Initialized) {
            return
        }

        # Остановка фоновой задачи
        [StructuredLogger]::CancellationTokenSource.Cancel()

        try {
            [StructuredLogger]::BackgroundTask.Wait(5000)  # Ждем до 5 секунд
        } catch {
            Write-Warning "Ошибка при остановке фоновой задачи логирования: $_"
        }

        [StructuredLogger]::Initialized = $false
    }
}

# Экспорт функций для использования в скриптах
function Initialize-Logging {
    param(
        [hashtable]$Config = @{}
    )

    [StructuredLogger]::Initialize($Config)
}

function Write-Log {
    param(
        [Parameter(Mandatory = $true)]
        [LogLevel]$Level,

        [Parameter(Mandatory = $true)]
        [string]$Message,

        [string]$Category = '',

        [hashtable]$Properties = $null,

        [Exception]$Exception = $null
    )

    [StructuredLogger]::Log($Level, $Message, $Category, $Properties, $Exception)
}

function Stop-Logging {
    [StructuredLogger]::Stop()
}

Export-ModuleMember -Function Initialize-Logging, Write-Log, Stop-Logging
