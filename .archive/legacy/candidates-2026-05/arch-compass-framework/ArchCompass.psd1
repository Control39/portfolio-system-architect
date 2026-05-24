@{
    RootModule        = 'ArchCompass.psm1'
    ModuleVersion     = '6.0.0'
    GUID              = 'a1b2c3d4-e5f6-7890-abcd-ef1234567890'
    Author            = 'Ekaterina Kudelya'
    CompanyName       = 'Cognitive Architect'
    Copyright         = '(c) 2026 Ekaterina Kudelya. CC BY-ND 4.0'
    Description       = 'Professional PowerShell framework for cognitive architecture: AI-powered scaffolding with security, logging, validation, DevOps integrations.'
    PowerShellVersion = '7.0'
    FunctionsToExport = 'Start-ArchCompass'
    CmdletsToExport   = @()
    VariablesToExport = @()
    AliasesToExport   = @()
    PrivateData       = @{
        PSData = @{
            Tags       = @('architecture', 'powershell', 'ai', 'devops', 'security', 'scaffold', 'gitleaks')
            LicenseUri = './LICENSE'
            ProjectUri = 'https://github.com/EkaterinaKudelya/portfolio-system-architect'
            ReleaseNotes = 'Integrated full ecosystem from backups'
        }
    }
    RequiredModules = @('Pester')
}
