# src/core/logging/StructuredLogger.psm1

class StructuredLogger {
    hidden static [scriptblock] $GlobalMasker = { param($s) $s }  # По умолчанию — ничего не делает

    static [void] SetMasker([scriptblock]$Masker) {
        if ($null -ne $Masker) {
            [StructuredLogger]::$GlobalMasker = $Masker
        }
    }

    static [void] Log([string]$Message, [string]$Level = "INFO") {
        # === МАСКИРОВАНИЕ ДО ЛОГИРОВАНИЯ ===
        $safeMessage = & [StructuredLogger]::$GlobalMasker $Message

        # Затем запись
        $entry = @{
            Timestamp = [DateTime]::UtcNow.ToString("o")
            Level     = $Level
            Message   = $safeMessage
        }

        # Запись в файл/консоль
        [StructuredLogger]::WriteToConsole($entry)
        [StructuredLogger]::WriteToFile($entry)
    }

    static [void] WriteToConsole([hashtable]$Entry) {
        $color = [ConsoleColor]::White
        if ($Entry.Level -eq "ERROR") { $color = "Red" }
        elseif ($Entry.Level -eq "WARN") { $color = "Yellow" }

        Write-Host "[$($Entry.Timestamp)] [$($Entry.Level)] $($Entry.Message)" -ForegroundColor $color
    }

    static [void] WriteToFile([hashtable]$Entry) {
        $logFile = "logs/arch-compass.log"
        $line = "$($Entry.Timestamp)|$($Entry.Level)|$($Entry.Message)"
        $line | Out-File $logFile -Append -Encoding UTF8 -Force
    }
}
