# src/core/logging/StructuredLogger.psm1

using namespace System.Collections.Concurrent
using namespace System.Threading.Tasks
using namespace System.IO

# Класс для результата логгирования (опционально)
class LogEntry {
    [DateTime] $Timestamp
    [string] $Level
    [string] $Message
    [string] $Category
    [hashtable] $Properties
    [int] $ProcessId
    [int] $ThreadId
    [string] $MachineName
    [string] $UserName
    [string] $Application
    [string] $Version
}

# Настройки по умолчанию
class LoggerConfig {
    [string] $LogDirectory
    [int] $MaxFileSizeMB
    [int] $RetentionDays
    [string] $Format  # JSON, CSV, Plain
    [bool] $EnableConsole
    [bool] $EnableFile
    [int] $BatchSize
    [int] $FlushIntervalMs
    [scriptblock] $SecretMasker  # Функция для маскирования: { param($obj) return $maskedObj }

    LoggerConfig() {
        $this.LogDirectory = "logs"
        $this.MaxFileSizeMB = 100
        $this.RetentionDays = 30
        $this.Format = "JSON"
        $this.EnableConsole = $true
        $this.EnableFile = $true
        $this.BatchSize = 50
        $this.FlushIntervalMs = 100
        $this.SecretMasker = $null
    }
}

class StructuredLogger {
    hidden static [ConcurrentQueue[hashtable]] $LogQueue = $null
    hidden static [Task] $LogTask = $null
    hidden static [CancellationTokenSource] $CancellationTokenSource = $null
    hidden static [LoggerConfig] $Config = $null
    hidden static [bool] $IsInitialized = $false

    # === Публичный интерфейс ===

    static [void] Initialize([hashtable]$config) {
        if ([StructuredLogger]::IsInitialized) {
            Write-Warning "StructuredLogger is already initialized. Use Stop-Logging before reinitializing."
            return
        }

        [StructuredLogger]::$Config = [LoggerConfig]::new()

        # Применяем конфиг
        $config.GetEnumerator() | ForEach-Object {
            if ($_.Key -in $Config.PSObject.Properties.Name) {
                $Config.$($_.Key) = $_.Value
            }
        }

        # Создаём директорию
        $fullPath = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($Config.LogDirectory)
        if (-not (Test-Path $fullPath)) {
            New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
        }

        [StructuredLogger]::$LogQueue = [ConcurrentQueue[hashtable]]::new()
        [StructuredLogger]::$CancellationTokenSource = [CancellationTokenSource]::new()

        [StructuredLogger]::StartBackgroundTask()

        [StructuredLogger]::$IsInitialized = $true

        [StructuredLogger]::Log("StructuredLogger initialized", "INFO", @{
            LogDirectory = $fullPath
            Format = $Config.Format
            BatchSize = $Config.BatchSize
        })
    }

    static [void] Log(
        [string]$Message,
        [string]$Level = "INFO",
        [hashtable]$Properties = $null,
        [string]$Category = "Application"
    ) {
        if (-not [StructuredLogger]::$IsInitialized) {
            [StructuredLogger]::FallbackLog($Message, $Level)
            return
        }

        $entry = @{
            Timestamp = [DateTime]::UtcNow.ToString("o")
            Level = $Level.ToUpper()
            Message = $Message
            Category = $Category
            Properties = if ($null -eq $Properties) { @{} } else { $Properties.Clone() }
            ProcessId = $PID
            ThreadId = [Threading.Thread]::CurrentThread.ManagedThreadId
            MachineName = $env:COMPUTERNAME
            UserName = try { [Security.Principal.WindowsIdentity]::GetCurrent().Name } catch { "Unknown" }
            Application = "Arch-Compass"
            Version = "6.0.0"
        }

        # Маскирование
        if ($Config.SecretMasker) {
            try {
                $entry = & $Config.SecretMasker $entry
            }
            catch {
                Write-Warning "Failed to mask secrets in log: $_"
            }
        }

        [StructuredLogger]::$LogQueue.Enqueue($entry)

        if ($Config.EnableConsole) {
            [StructuredLogger]::WriteToConsole($entry)
        }
    }

    static [void] Flush() {
        if (-not $IsInitialized) { return }

        $batch = [System.Collections.Generic.List[hashtable]]::new()
        while ([StructuredLogger]::$LogQueue.TryDequeue([ref]$entry)) {
            $batch.Add($entry)
        }

        if ($batch.Count -gt 0) {
            [StructuredLogger]::WriteBatchToFile($batch)
        }
    }

    static [void] Stop() {
        if (-not [StructuredLogger]::$IsInitialized) {
            return
        }

        [StructuredLogger]::Log("Stopping StructuredLogger", "INFO")
        [StructuredLogger]::Flush()

        if ([StructuredLogger]::$CancellationTokenSource) {
            [StructuredLogger]::$CancellationTokenSource.Cancel()

            try {
                $task = [StructuredLogger]::$LogTask
                if ($task -and -not $task.IsCompleted) {
                    $task.Wait(5000)
                }
            } catch {
                Write-Warning "Logger task did not stop gracefully: $_"
            }

            [StructuredLogger]::$CancellationTokenSource.Dispose()
            [StructuredLogger]::$CancellationTokenSource = $null
        }

        [StructuredLogger]::$IsInitialized = $false
        [StructuredLogger]::$LogQueue = $null
        [StructuredLogger]::$LogTask = $null
        [StructuredLogger]::$Config = $null
    }

    # === Приватные методы ===

    hidden static [void] StartBackgroundTask() {
        [StructuredLogger]::$LogTask = [Task]::Factory.StartNew({
            $token = [StructuredLogger]::$CancellationTokenSource.Token
            $batch = [System.Collections.Generic.List[hashtable]]::new()

            while (-not $token.IsCancellationRequested) {
                $batch.Clear()
                $count = 0

                while ($count -lt [StructuredLogger]::$Config.BatchSize -and
                       [StructuredLogger]::$LogQueue.Count -gt 0) {
                    if ([StructuredLogger]::$LogQueue.TryDequeue([ref]$entry)) {
                        $batch.Add($entry)
                        $count++
                    }
                }

                if ($batch.Count -gt 0) {
                    [StructuredLogger]::WriteBatchToFile($batch)
                }

                # Асинхронная задержка
                $null = [Task]::Delay([StructuredLogger]::$Config.FlushIntervalMs, $token).Wait($token)
            }

            # Финальная запись
            if ([StructuredLogger]::$LogQueue.Count -gt 0) {
                $finalBatch = [System.Collections.Generic.List[hashtable]]::new()
                while ([StructuredLogger]::$LogQueue.TryDequeue([ref]$entry)) {
                    $finalBatch.Add($entry)
                }
                if ($finalBatch.Count -gt 0) {
                    [StructuredLogger]::WriteBatchToFile($finalBatch)
                }
            }
        }, $token, [TaskCreationOptions]::LongRunning, [TaskScheduler]::Default)
    }

    hidden static [void] WriteBatchToFile([System.Collections.Generic.List[hashtable]]$batch) {
        if (-not [StructuredLogger]::$Config.EnableFile) { return }

        $logFile = [StructuredLogger]::GetCurrentLogFile()

        $lines = @()
        foreach ($entry in $batch) {
            try {
                $line = switch ([StructuredLogger]::$Config.Format.ToUpper()) {
                    "JSON" {
                        ConvertTo-Json -InputObject $entry -Compress -Depth 5 -ErrorAction Stop
                    }
                    "CSV" {
                        $quoted = $entry.Message -replace '"', '""'
                        "$($entry.Timestamp),`"$quoted`",$($entry.Level)"
                    }
                    default {
                        "[$($entry.Timestamp)] [$($entry.Level)] $($entry.Message)"
                    }
                }
                $lines += $line
            }
            catch {
                Write-Warning "Failed to serialize log entry: $_"
            }
        }

        try {
            $lines | Out-File -FilePath $logFile -Append -Encoding UTF8 -ErrorAction Stop
            [StructuredLogger]::RotateLogsIfNeeded($logFile)
        }
        catch {
            Write-Warning "Failed to write log batch to file: $_"
        }
    }

    hidden static [string] GetCurrentLogFile() {
        $date = Get-Date -Format "yyyy-MM-dd"
        return Join-Path [StructuredLogger]::$Config.LogDirectory "arch-compass-$date.log"
    }

    hidden static [void] RotateLogsIfNeeded([string]$currentFile) {
        $config = [StructuredLogger]::$Config
        if (-not (Test-Path $config.LogDirectory)) { return }

        # Ротация по размеру
        if (Test-Path $currentFile) {
            $fileSizeMB = (Get-Item $currentFile).Length / 1MB
            if ($fileSizeMB -gt $config.MaxFileSizeMB) {
                $timestamp = Get-Date -Format "yyyyMMddHHmmss"
                $newName = $currentFile -replace '\.log$', "-$timestamp.log"
                try { Rename-Item -Path $currentFile -NewName $newName -Force -ErrorAction Stop }
                catch { Write-Warning "Failed to rotate log file: $_" }
            }
        }

        # Удаление старых
        $cutoff = (Get-Date).AddDays(-$config.RetentionDays)
        Get-ChildItem $config.LogDirectory -Filter "*.log" -ErrorAction SilentlyContinue |
            Where-Object { $_.LastWriteTime -lt $cutoff } |
            Remove-Item -Force -ErrorAction SilentlyContinue
    }

    hidden static [void] WriteToConsole([hashtable]$entry) {
        $color = [StructuredLogger]::GetColorForLevel($entry.Level)
        $msg = "[$($entry.Timestamp)] [$($entry.Level)] $($entry.Message)"

        if ($entry.Properties.Count -gt 0) {
            $props = ($entry.Properties.GetEnumerator() | ForEach-Object { "$($_.Key)=$($_.Value)" }) -join ', '
            $msg += " | $props"
        }

        Write-Host $msg -ForegroundColor $color
    }

    hidden static [ConsoleColor] GetColorForLevel([string]$level) {
        return switch ($level.ToUpper()) {
            "DEBUG"    { [ConsoleColor]::Gray }
            "INFO"     { [ConsoleColor]::White }
            "WARN"     { [ConsoleColor]::Yellow }
            "ERROR"    { [ConsoleColor]::Red }
            "CRITICAL" { [ConsoleColor]::DarkRed }
            default    { [ConsoleColor]::White }
        }
    }

    hidden static [void] FallbackLog([string]$Message, [string]$Level) {
        $color = [StructuredLogger]::GetColorForLevel($Level)
        Write-Host "[FALLBACK] [$Level] $Message" -ForegroundColor $color
    }
}

# === Экспорт функций ===

function Write-Log {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Message,
        [ValidateSet("DEBUG", "INFO", "WARN", "ERROR", "CRITICAL")]
        [string]$Level = "INFO",
        [hashtable]$Properties = @{},
        [string]$Category = "Application"
    )
    [StructuredLogger]::Log($Message, $Level, $Properties, $Category)
}

function Initialize-Logging {
    [CmdletBinding()]
    param([hashtable]$Config = @{})
    [StructuredLogger]::Initialize($Config)
}

function Stop-Logging {
    [CmdletBinding()]
    param()
    [StructuredLogger]::Stop()
}

# Функция для установки маскировщика (интеграция с SecretManager)
function Set-SecretMasker {
    [CmdletBinding()]
    param([scriptblock]$Masker)
    if (-not [StructuredLogger]::$IsInitialized) {
        throw "StructuredLogger must be initialized before setting masker."
    }
    [StructuredLogger]::$Config.SecretMasker = $Masker
}

Export-ModuleMember -Function Write-Log, Initialize-Logging, Stop-Logging, Set-SecretMasker
