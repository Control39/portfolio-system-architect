# tests/pester.config.ps1

$config = New-PesterConfiguration

# Общие настройки
$config.Run.Path = "$PSScriptRoot/unit"
$config.Run.PassThru = $true
$config.Run.ContainerMode = 'PerFile'

# Результаты
$config.TestResult.Enabled = $true
$config.TestResult.OutputFormat = 'NUnitXml'
$config.TestResult.OutputPath = "$PSScriptRoot/../artifacts/reports/testResults-unit.xml"

# Покрытие кода (включено только при необходимости)
$config.CodeCoverage.Enabled = $false  # Включаем вручную
$config.CodeCoverage.OutputFormat = 'JaCoCo'
$config.CodeCoverage.OutputPath = "$PSScriptRoot/../artifacts/reports/coverage.xml"
$config.CodeCoverage.Path = "$PSScriptRoot/../src/**/*.psm1"

# Фильтрация
$config.Filter.Tag = @()
$config.Filter.ExcludeTag = @('Integration', 'E2E', 'Slow', 'RequiresAzure', 'Manual')

# Вывод
$config.Output.Verbosity = 'Normal'

$config
