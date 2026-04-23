@{
    RootModule        = 'InfraOrchestrator.psm1'
    ModuleVersion     = '7.0.0'
    GUID              = 'a1b2c3d4-e5f6-7890-abcd-ef1234567890'
    Author            = 'Ekaterina Kudelya'
    CompanyName       = 'Cognitive Architect'
    Copyright         = '(c) 2026 Ekaterina Kudelya. CC BY-ND 4.0'
    Description       = 'PowerShell library for infrastructure orchestration: AI workflow management, secrets handling, Prometheus metrics, and architectural compliance.'
    PowerShellVersion = '7.0'
    FunctionsToExport = 'Start-InfraOrchestrator'
    CmdletsToExport   = @()
    VariablesToExport = @()
    AliasesToExport   = @()
    PrivateData       = @{
        PSData = @{
            Tags       = @('infrastructure', 'orchestration', 'powershell', 'ai', 'devops', 'security', 'prometheus')
            LicenseUri = './LICENSE'
            ProjectUri = 'https://github.com/Control39/portfolio-system-architect'
            ReleaseNotes = 'Renamed from Arch-Compass to Infra-Orchestrator for professional positioning'
        }
    }
    RequiredModules = @('Pester')
}
