# src/core/logging/StructuredLogger.psm1

using namespace System.Collections.Concurrent
using namespace System.Threading.Tasks
using namespace System.IO

# Класс для результата инициализации
class LoggerConfig {
    [string] $LogDirectory
    [string] $Format = "JSON" # JSON, CSV, Text
    [int] $MaxFileSizeMB = 100
    [int] $RetentionDays = 30
    [int] $BatchSize = 50
    [int] $FlushIntervalMs = 100
    [bool] $EnableFile = $true
    [bool] $EnableConsole = $true

    LoggerConfig([hashtable]$config) {
        $config.GetEnumerator() | ForEach-Object {
            if ($this.PSObject.Properties.Name -contains $_.Key) {
                $this.$($_.Key) = $_.Value
            }
        }
    }
}

class StructuredLogger {
    hidden static [ConcurrentQueue[hashtable]] $LogQueue = $null
    hidden static [Task] $LogTask = $null
    hidden static [CancellationTokenSource] $CancellationTokenSource = $null
    hidden static [LoggerConfig] $Config = $null
    hidden static [scriptblock] $SecretMasker = { param($e) $e } # no-op by default
    hidden static [bool] $IsInitialized = $false

    # --- Инициализация ---
    static [void] Initialize([hashtable]$config) {
        if ([StructuredLogger]::$IsInitialized) {
            Write-Warning "StructuredLogger is already initialized."
            return
        }

        [StructuredLogger]::$Config = [LoggerConfig]::new($config)
        [StructuredLogger]::$LogQueue = [ConcurrentQueue[hashtable]]::new()
        [StructuredLogger]::$CancellationTokenSource = [CancellationTokenSource]::new()

        # Создаём директорию
        $logDir = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath([StructuredLogger]::$Config.LogDirectory)
        if (-not (Test-Path $logDir)) {
            New-Item -ItemType Directory -Path $logDir -Force | Out-Null
        }

        [StructuredLogger]::StartBackgroundTask()
        [StructuredLogger]::$IsInitialized = $true

        [StructuredLogger]::Log("StructuredLogger initialized", "INFO", @{
            Directory = $logDir
            Format = [StructuredLogger]::$Config.Format
        })
    }

    # --- Основной метод логирования ---
    static [void] Log(
        [string]$Message,
        [string]$Level = "INFO",
        [hashtable]$Properties = $null,
        [string]$Category = "Application"
    ) {
        if (-not [StructuredLogger]::$IsInitialized) {
            # Fallback
            $color = [ConsoleColor]::White
            if ($Level -eq "ERROR") { $color = "Red" }
            elseif ($Level -in "WARN", "WARNING") { $color = "Yellow" }
            Write-Host "[$Level] $Message" -ForegroundColor $color
            return
        }

        $entry = @{
            Timestamp = [DateTime]::UtcNow.ToString("o")
            Level     = $Level.ToUpper()
            Message   = $Message
            Category  = $Category
            Properties = if ($null -eq $Properties) { @{} } else { $Properties }
            ProcessId  = $PID
            ThreadId   = [Threading.Thread]::CurrentThread.ManagedThreadId
            MachineName = $env:COMPUTERNAME
            UserName   = try { [Security.Principal.WindowsIdentity]::GetCurrent().Name } catch { "Unknown" }
        }

        # Применяем маскирование
        $maskedEntry = & [StructuredLogger]::$SecretMasker $entry

        [StructuredLogger]::$LogQueue.Enqueue($maskedEntry)

        # Консольный вывод (опционально)
        if ([StructuredLogger]::$Config.EnableConsole) {
            [StructuredLogger]::WriteToConsole($maskedEntry)
        }
    }

    # --- Установка маскировщика (для интеграции с SecretManager) ---
    static [void] SetSecretMasker([scriptblock]$Masker) {
        if ($null -ne $Masker) {
            [StructuredLogger]::$SecretMasker = $Masker
        }
    }

    # --- Запуск фоновой задачи ---
    hidden static [void] StartBackgroundTask() {
        [StructuredLogger]::$LogTask = [Task]::Factory.StartNew({
            $token = [StructuredLogger]::$CancellationTokenSource.Token
            $config = [StructuredLogger]::$Config
            $batch = [System.Collections.Generic.List[hashtable]]::new()

            while (-not $token.IsCancellationRequested) {
                $batch.Clear()
                $count = 0

                while ($count -lt $config.BatchSize -and [StructuredLogger]::$LogQueue.Count -gt 0) {
                    if ([StructuredLogger]::$LogQueue.TryDequeue([ref]$entry)) {
                        $batch.Add($entry)
                        $count++
                    }
                }

                if ($batch.Count -gt 0 -and $config.EnableFile) {
                    [StructuredLogger]::WriteBatchToFile($batch)
                }

                # Асинхронная задержка
                $null = [Task]::Delay($config.FlushIntervalMs, $token).Wait($token)
            }

            # Финальная запись
            if ([StructuredLogger]::$LogQueue.Count -gt 0) {
                $final = [System.Collections.Generic.List[hashtable]]::new()
                while ([StructuredLogger]::$LogQueue.TryDequeue([ref]$entry)) {
                    $final.Add($entry)
                }
                if ($final.Count -gt 0) {
                    [StructuredLogger]::WriteBatchToFile($final)
                }
            }
        }, $token, [TaskCreationOptions]::LongRunning, [TaskScheduler]::Default)
    }

    # --- Запись батча в файл ---
    hidden static [void] WriteBatchToFile([System.Collections.Generic.List[hashtable]]$Batch) {
        $logFile = [StructuredLogger]::GetCurrentLogFile()
        $lines = [System.Collections.Generic.List[string]]::new()

        foreach ($entry in $Batch) {
            try {
                $line = switch ([StructuredLogger]::$Config.Format.ToUpper()) {
                    "JSON" {
                        ConvertTo-Json -InputObject $entry -Compress -Depth 5
                    }
                    "CSV" {
                        $quotedMsg = $entry.Message -replace '"', '""'
                        "$($entry.Timestamp),`"$quotedMsg`",$($entry.Level),$($entry.Category)"
                    }
                    default {
                        "[$($entry.Timestamp)] [$($entry.Level)] $($entry.Message)"
                    }
                }
                $lines.Add($line)
            }
            catch {
                Write-Warning "Failed to format log entry: $_"
            }
        }

        try {
            $lines | Out-File -FilePath $logFile -Append -Encoding UTF8 -ErrorAction Stop
            [StructuredLogger]::RotateLogsIfNeeded($logFile)
        }
        catch {
            Write-Warning "Failed to write log batch: $_"
        }
    }

    # --- Текущий файл лога ---
    hidden static [string] GetCurrentLogFile() {
        $date = Get-Date -Format "yyyy-MM-dd"
        return Join-Path [StructuredLogger]::$Config.LogDirectory "arch-compass-$date.log"
    }

    # --- Ротация и архивация ---
    hidden static [void] RotateLogsIfNeeded([string]$LogFile) {
        $config = [StructuredLogger]::$Config

        # 1. Проверка размера
        if (Test-Path $LogFile) {
            $fileSizeMB = (Get-Item $LogFile).Length / 1MB
            if ($fileSizeMB -gt $config.MaxFileSizeMB) {
                $timestamp = Get-Date -Format "yyyyMMddHHmmss"
                $newName = $LogFile -replace '\.log$', "-$timestamp.log"
                try {
                    Rename-Item -Path $LogFile -NewName $newName -Force
                } catch {
                    Write-Warning "Failed to rotate log file: $_"
                }
            }
        }

        # 2. Удаление старых
        $cutoff = (Get-Date).AddDays(-$config.RetentionDays)
        Get-ChildItem $config.LogDirectory -Filter "*.log" -ErrorAction SilentlyContinue |
            Where-Object { $_.LastWriteTime -lt $cutoff } |
            Remove-Item -Force -ErrorAction SilentlyContinue

        # 3. Архивация (логи старше 1 дня, но не сегодняшние)
        $archiveCutoff = (Get-Date).AddDays(-1).Date
        Get-ChildItem $config.LogDirectory -Filter "*.log" -ErrorAction SilentlyContinue |
            Where-Object { 
                $_.LastWriteTime -lt $archiveCutoff -and 
                $_.Name -notmatch (Get-Date -Format "yyyy-MM-dd") 
            } | ForEach-Object {
                $zip = $_.FullName -replace '\.log$', '.zip'
                try {
                    Compress-Archive -Path $_.FullName -DestinationPath $zip -Force
                    Remove-Item $_.FullName -Force
                } catch {
                    Write-Warning "Failed to compress log: $($_.Exception.Message)"
                }
            }
    }

    # --- Вывод в консоль ---
    hidden static [void] WriteToConsole([hashtable]$Entry) {
        $color = switch ($Entry.Level) {
            "DEBUG"    { [ConsoleColor]::Gray }
            "INFO"     { [ConsoleColor]::White }
            "WARN"     { [ConsoleColor]::Yellow }
            "ERROR"    { [ConsoleColor]::Red }
            "CRITICAL" { [ConsoleColor]::DarkRed }
            default    { [ConsoleColor]::White }
        }

        $msg = "[$($Entry.Timestamp)] [$($Entry.Level)] $($Entry.Message)"
        if ($Entry.Properties.Count -gt 0) {
            $props = ($Entry.Properties.GetEnumerator() | ForEach-Object { "$($_.Key)=$($_.Value)" }) -join ', '
            $msg += " | $props"
        }

        Write-Host $msg -ForegroundColor $color
    }

    # --- Остановка логгера ---
    static [void] Stop() {
        if (-not [StructuredLogger]::$IsInitialized) { return }

        [StructuredLogger]::Log("Shutting down logger...", "INFO")
        [StructuredLogger]::$CancellationTokenSource.Cancel()

        try {
            if ([StructuredLogger]::$LogTask -and -not [StructuredLogger]::$LogTask.IsCompleted) {
                [StructuredLogger]::$LogTask.Wait(5000)
            }
        } catch {
            Write-Warning "Logger task did not stop gracefully: $_"
        }

        [StructuredLogger]::$CancellationTokenSource.Dispose()
        [StructuredLogger]::$IsInitialized = $false
    }
}

# === Экспорт функций ===

function Write-Log {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [string] $Message,
        [ValidateSet("DEBUG", "INFO", "WARN", "WARNING", "ERROR", "CRITICAL")]
        [string] $Level = "INFO",
        [hashtable] $Properties = @{},
        [string] $Category = "Application"
    )
    [StructuredLogger]::Log($Message, $Level, $Properties, $Category)
}

function Initialize-Logging {
    [CmdletBinding()]
    param([hashtable] $Config)
    [StructuredLogger]::Initialize($Config)
}

function Stop-Logging {
    [CmdletBinding()]
    param()
    [StructuredLogger]::Stop()
}

Export-ModuleMember -Function Write-Log, Initialize-Logging, Stop-Logging
