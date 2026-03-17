# tests/run-tests.ps1
param(
    [ValidateSet("Unit", "Integration", "E2E", "All")]
    [string]$TestType = "Unit",

    [switch]$CodeCoverage,

    [switch]$CI
)

# --- Настройки ---
$TestsRoot = $PSScriptRoot
$ArtifactsDir = "$PSScriptRoot/../artifacts"
$ReportsDir = "$ArtifactsDir/reports"
$LogsDir = "$ArtifactsDir/logs"

New-Item -ItemType Directory -Path $ArtifactsDir, $ReportsDir, $LogsDir -Force | Out-Null

$Timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$LogPath = "$LogsDir/test-run-$Timestamp.log"

# --- Функции ---
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $line = "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] [$Level] $Message"
    Write-Host $line
    $line | Out-File -FilePath $LogPath -Append -Encoding UTF8
}

function Get-TestConfig {
    param([hashtable]$Overrides = @{})

    $config = . "$TestsRoot/pester.config.ps1"

    # Применяем оверрайды
    if ($Overrides.ContainsKey("Path")) { $config.Run.Path = $Overrides.Path }
    if ($Overrides.ContainsKey("Tag")) { $config.Filter.Tag = $Overrides.Tag; $config.Filter.ExcludeTag = @() }
    if ($Overrides.ContainsKey("CodeCoverage")) { $config.CodeCoverage.Enabled = $Overrides.CodeCoverage }

    $config
}

function Run-Tests {
    param([string]$Path, [hashtable]$ConfigOverrides)

    $config = Get-TestConfig $ConfigOverrides

    Write-Log "Starting tests in '$Path' with config: $($config | ConvertTo-Json -Compress)"
    
    $result = Invoke-Pester -Configuration $config -ErrorVariable ev -ErrorAction SilentlyContinue

    # Обновляем путь к отчёту, если нужно
    $reportFile = $config.TestResult.OutputPath
    if (Test-Path $reportFile) {
        $newName = $reportFile -replace '\.xml$', "-$Timestamp.xml"
        Rename-Item -Path $reportFile -NewName (Split-Path $newName -Leaf) -PathType Leaf -Force
    }

    if ($result.FailedCount -gt 0) {
        Write-Log "❌ Tests failed: $($result.FailedCount)" "ERROR"
        return $false
    }

    Write-Log "✅ All tests passed."
    return $true
}

# --- Главная логика ---
Write-Log "Starting test suite: $TestType (Coverage: $CodeCoverage, CI: $CI)"

$allPassed = $true

try {
    # Unit тесты
    if ($TestType -in @("Unit", "All")) {
        $unitConfig = @{
            Path = "$TestsRoot/unit"
            CodeCoverage = $CodeCoverage
        }
        if (-not (Run-Tests -Path $unitConfig.Path -ConfigOverrides $unitConfig)) {
            $allPassed = $false
            if (-not $CI) { exit 1 }
        }
    }

    # Integration тесты
    if ($TestType -in @("Integration", "All")) {
        $integrationConfig = @{
            Path = "$TestsRoot/integration"
            Tag = @("Integration")
            ExcludeTag = @("E2E", "Slow", "RequiresAzure")
        }
        if (-not (Run-Tests -Path $integrationConfig.Path -ConfigOverrides $integrationConfig)) {
            $allPassed = $false
            if (-not $CI) { exit 1 }
        }
    }

    # E2E тесты
    if ($TestType -in @("E2E", "All")) {
        $e2eConfig = @{
            Path = "$TestsRoot/e2e"
            Tag = @("E2E", "Slow")
            ExcludeTag = @()
        }
        if (-not (Run-Tests -Path $e2eConfig.Path -ConfigOverrides $e2eConfig)) {
            $allPassed = $false
            if (-not $CI) { exit 1 }
        }
    }
}
catch {
    Write-Log "🚨 Test runner failed: $_" "ERROR"
    exit 1
}

# --- CI Артефакты ---
if ($CI) {
    Write-Log "📦 Preparing CI artifacts..."

    # Копируем отчёты в корень артефактов
    Get-ChildItem "$ReportsDir/*-$Timestamp.xml" | Copy-Item -Destination $ArtifactsDir -Force

    # Экспорт переменных (для GitHub Actions / Azure DevOps)
    if ($env:GITHUB_ACTIONS) {
        "##[set-output name=test_status;]$($allPassed.ToString().ToLower())"
    }
    if ($env:TF_BUILD) {
        Write-Host "##vso[task.setvariable variable=testStatus]$($allPassed)"
    }
}

Write-Log "🏁 Test run completed. Success: $allPassed"
exit (if ($allPassed) { 0 } else { 1 })
