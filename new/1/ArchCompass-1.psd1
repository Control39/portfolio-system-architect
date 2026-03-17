# ArchCompass.psd1
@{
    RootModule        = 'ArchCompass.psm1'
    ModuleVersion     = '6.0.0'
    GUID              = 'a1b2c3d4-e5f6-7890-1234-567890abcdef'  # Замените на новый GUID
    Author            = 'Your Name'
    CompanyName       = 'Your Organization'
    Copyright         = '(c) 2025. All rights reserved.'
    Description       = 'Arch-Compass: Automated architecture scaffolding with security, AI, and DevOps.'
    PowerShellVersion = '5.1'
    FunctionsToExport = 'Main'
    CmdletsToExport   = @()
    VariablesToExport = @()
    AliasesToExport   = @()
    PrivateData       = @{
        PSData = @{
            Tags       = @("architecture", "devops", "security", "ai", "scaffold", "powershell")
            LicenseUri = 'https://github.com/your-org/arch-compass/LICENSE'
            ProjectUri = 'https://github.com/your-org/arch-compass'
            IconUri    = ''
            ReleaseNotes = 'Initial release with security-first scaffolding, SecretManager, and AI integration.'
        }
    }
}
