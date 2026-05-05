#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Services Structure Fixer
    Быстро создает недостающие директории и файлы в сервисах

.EXAMPLE
    .\fix_services.ps1 -Mode critical   # Только критичные
    .\fix_services.ps1 -Mode all        # Все сервисы
    .\fix_services.ps1 -Dry             # Только показать что будет сделано
#>

param(
    [ValidateSet('critical', 'all')]
    [string]$Mode = 'critical',
    
    [switch]$Dry
)

$ErrorActionPreference = 'Continue'

function Write-Title { param([string]$Text) Write-Host "`n$Text`n" -ForegroundColor Cyan }
function Write-OK { param([string]$Text) Write-Host "✅ $Text" -ForegroundColor Green }
function Write-Warn { param([string]$Text) Write-Host "⚠️  $Text" -ForegroundColor Yellow }
function Write-Error { param([string]$Text) Write-Host "❌ $Text" -ForegroundColor Red }
function Write-Info { param([string]$Text) Write-Host "ℹ️  $Text" -ForegroundColor Gray }

# Services that need fixing
$criticalServices = @(
    'auth_service',
    'system-proof',
    'thought-architecture'
)

$configMissing = @(
    'ai-config-manager',
    'auth_service',
    'career_development',
    'cognitive-agent',
    'decision-engine',
    'job-automation-agent',
    'knowledge-graph',
    'ml-model-registry',
    'portfolio_organizer',
    'system-proof',
    'template-service',
    'thought-architecture'
)

$testsMissing = @(
    'ai-config-manager',
    'auth_service',
    'infra-orchestrator',
    'job-automation-agent',
    'portfolio_organizer',
    'system-proof',
    'thought-architecture'
)

Write-Title "🔧 SERVICES STRUCTURE FIXER"

if ($Dry) {
    Write-Warn "DRY RUN MODE - No changes will be made"
}

# Select services to fix based on mode
$servicesToFix = if ($Mode -eq 'critical') { $criticalServices } else { Get-ChildItem "apps" -Directory | Select-Object -ExpandProperty Name }

Write-Info "Mode: $Mode"
Write-Info "Services to fix: $($servicesToFix.Count)"

# Counter
$created = 0
$skipped = 0

foreach ($service in $servicesToFix) {
    $servicePath = "apps/$service"
    
    if (-not (Test-Path $servicePath)) {
        Write-Warn "Skipping $service - directory not found"
        $skipped++
        continue
    }
    
    Write-Host "`n📦 Processing: $service"
    
    # Check and create src (for critical)
    if ($Mode -eq 'critical' -or $service -in $criticalServices) {
        $srcPath = "$servicePath/src"
        if (-not (Test-Path $srcPath)) {
            if ($Dry) {
                Write-Info "  Would create: src/"
            } else {
                New-Item -ItemType Directory -Path $srcPath -Force | Out-Null
                Write-OK "Created: src/"
                $created++
            }
        } else {
            Write-Info "  Already exists: src/"
        }
    }
    
    # Check and create config
    if ($service -in $configMissing) {
        $configPath = "$servicePath/config"
        if (-not (Test-Path $configPath)) {
            if ($Dry) {
                Write-Info "  Would create: config/"
            } else {
                New-Item -ItemType Directory -Path $configPath -Force | Out-Null
                Write-OK "Created: config/"
                $created++
            }
        } else {
            Write-Info "  Already exists: config/"
        }
    }
    
    # Check and create tests
    if ($service -in $testsMissing) {
        $testsPath = "$servicePath/tests"
        if (-not (Test-Path $testsPath)) {
            if ($Dry) {
                Write-Info "  Would create: tests/"
            } else {
                New-Item -ItemType Directory -Path $testsPath -Force | Out-Null
                Write-OK "Created: tests/"
                $created++
                
                # Create __init__.py
                "" | Out-File -FilePath "$testsPath/__init__.py" -Encoding UTF8
                Write-OK "Created: tests/__init__.py"
            }
        } else {
            Write-Info "  Already exists: tests/"
        }
    }
    
    # Check README.md
    $readmePath = "$servicePath/README.md"
    if (-not (Test-Path $readmePath)) {
        if ($Dry) {
            Write-Info "  Would create: README.md"
        } else {
            $readmeContent = @"
# $service

Service description here.

## Getting Started

\`\`\`bash
cd apps/$service
pytest tests/ -v
\`\`\`

## Configuration

Configuration files are in \`config/\` directory.

## Testing

\`\`\`bash
pytest tests/ -v --cov
\`\`\`

## Documentation

See \`docs/\` for more information.
"@
            $readmeContent | Out-File -FilePath $readmePath -Encoding UTF8
            Write-OK "Created: README.md"
            $created++
        }
    } else {
        Write-Info "  Already exists: README.md"
    }
}

Write-Title "📊 SUMMARY"
Write-OK "Directories/files created: $created"
Write-Info "Skipped: $skipped"

if ($Dry) {
    Write-Warn "`nDRY RUN - To actually create, run without -Dry flag"
    Write-Info "Example: .\fix_services.ps1 -Mode critical"
} else {
    Write-OK "`n✅ All fixes applied!"
}

# Run health check after
Write-Info "`nTo verify, run: python health_check.py"
