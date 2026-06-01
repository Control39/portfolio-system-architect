# PowerShell скрипт для управления расширениями VS Code на Windows
# Автоматическая установка, проверка и синхронизация расширений

param(
    [string]$ConfigPath = "config/vscode/vscode-extensions.json",
    [switch]$DryRun,
    [switch]$Install,
    [switch]$Check,
    [switch]$Sync,
    [switch]$Report
)

# Настройка выполнения
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

# Функции логирования
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$timestamp] [$Level] $Message"
}

function Write-ErrorLog {
    param([string]$Message)
    Write-Log -Message $Message -Level "ERROR"
}

function Write-WarningLog {
    param([string]$Message)
    Write-Log -Message $Message -Level "WARNING"
}

# Проверка наличия VS Code
function Test-VSCodeInstalled {
    try {
        $codeVersion = & code --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Log "VS Code обнаружен: $($codeVersion[0])"
            return $true
        }
    } catch {
        # Пробуем альтернативные пути
        $possiblePaths = @(
            "$env:LOCALAPPDATA\Programs\Microsoft VS Code\bin\code.cmd",
            "$env:ProgramFiles\Microsoft VS Code\bin\code.cmd",
            "$env:ProgramFiles\Microsoft VS Code\Code.exe"
        )

        foreach ($path in $possiblePaths) {
            if (Test-Path $path) {
                Write-Log "VS Code найден по пути: $path"
                $global:CodeCommand = $path
                return $true
            }
        }
    }

    Write-ErrorLog "VS Code не найден. Установите VS Code и добавьте в PATH"
    return $false
}

# Получение установленных расширений
function Get-InstalledExtensions {
    try {
        $extensions = & code --list-extensions 2>$null
        if ($LASTEXITCODE -eq 0) {
            return $extensions
        }
    } catch {
        Write-ErrorLog "Ошибка при получении списка расширений: $_"
    }
    return @()
}

# Установка расширения
function Install-Extension {
    param([string]$ExtensionId)

    if ($DryRun) {
        Write-Log "[DRY RUN] Установка расширения: $ExtensionId"
        return $true
    }

    try {
        Write-Log "Установка расширения: $ExtensionId"
        & code --install-extension $ExtensionId 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Log "Расширение установлено: $ExtensionId"
            return $true
        } else {
            Write-WarningLog "Не удалось установить расширение: $ExtensionId"
            return $false
        }
    } catch {
        Write-ErrorLog "Ошибка при установке расширения $ExtensionId : $_"
        return $false
    }
}

# Удаление расширения
function Uninstall-Extension {
    param([string]$ExtensionId)

    if ($DryRun) {
        Write-Log "[DRY RUN] Удаление расширения: $ExtensionId"
        return $true
    }

    try {
        Write-Log "Удаление расширения: $ExtensionId"
        & code --uninstall-extension $ExtensionId 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Log "Расширение удалено: $ExtensionId"
            return $true
        } else {
            Write-WarningLog "Не удалось удалить расширение: $ExtensionId"
            return $false
        }
    } catch {
        Write-ErrorLog "Ошибка при удалении расширения $ExtensionId : $_"
        return $false
    }
}

# Загрузка конфигурации
function Load-Configuration {
    param([string]$ConfigPath)

    if (-not (Test-Path $ConfigPath)) {
        Write-ErrorLog "Конфигурационный файл не найден: $ConfigPath"
        return $null
    }

    try {
        $config = Get-Content $ConfigPath -Raw | ConvertFrom-Json
        Write-Log "Конфигурация загружена из: $ConfigPath"
        return $config
    } catch {
        Write-ErrorLog "Ошибка при загрузке конфигурации: $_"
        return $null
    }
}

# Проверка соответствия
function Check-Compliance {
    param([object]$Config)

    Write-Log "Проверка соответствия расширений..."

    $installed = Get-InstalledExtensions
    $required = @($Config.required)
    $excluded = @($Config.excluded)

    # Проверка обязательных расширений
    $missingRequired = @()
    foreach ($ext in $required) {
        if ($ext -notin $installed) {
            $missingRequired += $ext
        }
    }

    # Проверка исключенных расширений
    $foundExcluded = @()
    foreach ($ext in $excluded) {
        if ($ext -in $installed) {
            $foundExcluded += $ext
        }
    }

    # Расчет compliance score
    $totalRequired = $required.Count
    $installedRequired = $totalRequired - $missingRequired.Count
    $complianceScore = if ($totalRequired -gt 0) { [math]::Round(($installedRequired / $totalRequired) * 100, 2) } else { 100 }

    # Формирование отчета
    $report = @{
        TotalInstalled = $installed.Count
        RequiredCount = $totalRequired
        InstalledRequired = $installedRequired
        MissingRequired = $missingRequired
        ExcludedCount = $excluded.Count
        FoundExcluded = $foundExcluded
        ComplianceScore = $complianceScore
        Status = if ($complianceScore -eq 100 -and $foundExcluded.Count -eq 0) { "PASS" } else { "FAIL" }
    }

    return $report
}

# Синхронизация расширений
function Sync-Extensions {
    param([object]$Config)

    Write-Log "Синхронизация расширений..."

    $installed = Get-InstalledExtensions
    $required = @($Config.required)
    $excluded = @($Config.excluded)

    $actions = @{
        Installed = 0
        Uninstalled = 0
        Failed = 0
    }

    # Установка отсутствующих обязательных расширений
    foreach ($ext in $required) {
        if ($ext -notin $installed) {
            if (Install-Extension -ExtensionId $ext) {
                $actions.Installed++
            } else {
                $actions.Failed++
            }
        }
    }

    # Удаление исключенных расширений
    foreach ($ext in $excluded) {
        if ($ext -in $installed) {
            if (Uninstall-Extension -ExtensionId $ext) {
                $actions.Uninstalled++
            } else {
                $actions.Failed++
            }
        }
    }

    return $actions
}

# Генерация отчета
function Generate-Report {
    param([object]$Report)

    Write-Host "`n=== ОТЧЕТ О СООТВЕТСТВИИ РАСШИРЕНИЙ VS CODE ===" -ForegroundColor Cyan
    Write-Host "Всего установлено расширений: $($Report.TotalInstalled)" -ForegroundColor White
    Write-Host "Обязательных расширений: $($Report.RequiredCount)" -ForegroundColor White
    Write-Host "Установлено обязательных: $($Report.InstalledRequired)" -ForegroundColor White
    Write-Host "Оценка соответствия: $($Report.ComplianceScore)%" -ForegroundColor $(if ($Report.ComplianceScore -ge 90) { "Green" } elseif ($Report.ComplianceScore -ge 70) { "Yellow" } else { "Red" })
    Write-Host "Статус: $($Report.Status)" -ForegroundColor $(if ($Report.Status -eq "PASS") { "Green" } else { "Red" })

    if ($Report.MissingRequired.Count -gt 0) {
        Write-Host "`nОтсутствующие обязательные расширения:" -ForegroundColor Yellow
        foreach ($ext in $Report.MissingRequired) {
            Write-Host "  - $ext" -ForegroundColor Yellow
        }
    }

    if ($Report.FoundExcluded.Count -gt 0) {
        Write-Host "`nНайдены исключенные расширения:" -ForegroundColor Red
        foreach ($ext in $Report.FoundExcluded) {
            Write-Host "  - $ext" -ForegroundColor Red
        }
    }

    Write-Host "`n=============================================" -ForegroundColor Cyan
}

# Основная логика
function Main {
    Write-Log "Запуск скрипта управления расширениями VS Code для Windows"
    Write-Log "Конфигурационный файл: $ConfigPath"

    # Проверка VS Code
    if (-not (Test-VSCodeInstalled)) {
        exit 1
    }

    # Загрузка конфигурации
    $config = Load-Configuration -ConfigPath $ConfigPath
    if (-not $config) {
        exit 1
    }

    # Определение действия
    if ($Check -or (-not $Install -and -not $Sync -and -not $Report)) {
        # Проверка по умолчанию
        $report = Check-Compliance -Config $config
        Generate-Report -Report $report
    }

    if ($Install) {
        Write-Log "Режим установки обязательных расширений"
        $required = @($config.required)
        $installed = Get-InstalledExtensions

        foreach ($ext in $required) {
            if ($ext -notin $installed) {
                Install-Extension -ExtensionId $ext
            }
        }
    }

    if ($Sync) {
        Write-Log "Режим синхронизации"
        $actions = Sync-Extensions -Config $config
        Write-Log "Синхронизация завершена:"
        Write-Log "  Установлено: $($actions.Installed)"
        Write-Log "  Удалено: $($actions.Uninstalled)"
        Write-Log "  Ошибок: $($actions.Failed)"

        # Показываем итоговый отчет
        $report = Check-Compliance -Config $config
        Generate-Report -Report $report
    }

    if ($Report) {
        $report = Check-Compliance -Config $config
        Generate-Report -Report $report
    }

    Write-Log "Скрипт завершен"
}

# Запуск основной функции
if ($MyInvocation.InvocationName -ne '.') {
    Main
}
