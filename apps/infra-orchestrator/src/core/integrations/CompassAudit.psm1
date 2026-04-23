function Invoke-ArchCompassAudit {
    param(
        [string]$CompassPath = '../it-compass',
        [string]$OutputFormat = 'Markdown'
    )
    
    # Загрузка маркеров из IT-Compass
    $markersPath = Join-Path $CompassPath 'src/data/markers'
    $allMarkers = Get-ChildItem $markersPath -Filter '*.json' | ForEach-Object {
        Get-Content $_.FullName | ConvertFrom-Json
    }
    
    # Анализ: какие компетенции требуются для работы с Arch-Compass
    $requiredSkills = @(
        @{ Domain = 'DevOps'; Marker = 'powershell.3'; Description = 'Advanced PowerShell scripting' },
        @{ Domain = 'Security'; Marker = 'cybersecurity.2'; Description = 'Secret management & scanning' },
        @{ Domain = 'System Design'; Marker = 'system_design.4'; Description = 'Modular architecture design' },
        @{ Domain = 'AI Applications'; Marker = 'ai_applications.3'; Description = 'LLM API integration patterns' }
    )
    
    # Генерация отчёта
    $report = @"
# Arch-Compass → IT-Compass Audit Report

## Required Competencies for Framework Usage
| Domain | Marker | Description | Status |
|--------|--------|-------------|--------|
$(foreach ($skill in $requiredSkills) {
    "| $($skill.Domain) | $($skill.Marker) | $($skill.Description) | 🟡 To Assess |`n"
})

## How to Validate
1. Open IT-Compass: \`cd $CompassPath && python src/main.py\`
2. Navigate to markers listed above
3. Complete validation tasks for each
4. Export progress: \`python src/utils/marker_export.py\`

## Next Steps
- [ ] Add automated marker validation to Arch-Compass CI
- [ ] Link Arch-Compass usage logs to IT-Compass progress tracking
- [ ] Generate competency growth report from framework adoption
"@
    
    $report | Out-File -FilePath './docs/compass-audit.md' -Encoding utf8
    Write-Host "✅ Compass audit report: ./docs/compass-audit.md"
}