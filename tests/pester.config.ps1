# Pester Configuration
# Конфигурация для запуска всех типов тестов

@{
    Run = @{
        Path = @(
            "$PSScriptRoot\unit",
            "$PSScriptRoot\integration",
            "$PSScriptRoot\e2e"
        )
        PassThru = $true
        Exit = $false
    }
    
    TestResult = @{
        Enabled = $true
        OutputPath = "$PSScriptRoot\TestResults\TestResults.xml"
        OutputFormat = "NUnitXml"
    }
    
    Filter = @{
        Tag = @()
        ExcludeTag = @()
    }
    
    CodeCoverage = @{
        Enabled = $true
        Path = @(
            "$PSScriptRoot\..\src\**\*.psm1",
            "$PSScriptRoot\..\src\**\*.ps1"
        )
        OutputPath = "$PSScriptRoot\TestResults\CodeCoverage.xml"
        OutputFormat = "CoverageGutters"
    }
    
    Output = @{
        Verbosity = "Detailed"
    }
}
