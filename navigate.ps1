#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Navigation script for Portfolio System Architect project
    Быстрая навигация по проекту и его компонентам

.DESCRIPTION
    Команды для быстрого доступа к сервисам, документации, инструментам и скриптам

.EXAMPLE
    ./navigate.ps1 -Status
    ./navigate.ps1 -Service cognitive-agent
    ./navigate.ps1 -List
    ./navigate.ps1 -Map
#>

param(
    [switch]$Status,
    [switch]$List,
    [switch]$Map,
    [switch]$Help,
    [string]$Service,
    [string]$Tool,
    [string]$Docs
)

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$appsDir = Join-Path $projectRoot "apps"

function Show-Header {
    Write-Host ""
    Write-Host "🧭 PORTFOLIO SYSTEM ARCHITECT - NAVIGATOR" -ForegroundColor Cyan
    Write-Host ("=" * 80) -ForegroundColor Cyan
    Write-Host ""
}

function Show-Help {
    Show-Header
    Write-Host "NAVIGATION COMMANDS:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  STATUS & OVERVIEW:"
    Write-Host "    ./navigate.ps1 -Status      Show project status and health"
    Write-Host "    ./navigate.ps1 -List        List all services"
    Write-Host "    ./navigate.ps1 -Map         Show architecture map"
    Write-Host ""
    Write-Host "  SERVICE NAVIGATION:"
    Write-Host "    ./navigate.ps1 -Service <name>     Go to service directory"
    Write-Host "    ./navigate.ps1 -Service cognitive-agent"
    Write-Host "    ./navigate.ps1 -Service decision-engine"
    Write-Host ""
    Write-Host "  TOOLS & DOCUMENTATION:"
    Write-Host "    ./navigate.ps1 -Tool <name>        Open tool/IDE config"
    Write-Host "    ./navigate.ps1 -Tool koda"
    Write-Host "    ./navigate.ps1 -Tool codeassistant"
    Write-Host ""
    Write-Host "    ./navigate.ps1 -Docs <topic>       Find documentation"
    Write-Host "    ./navigate.ps1 -Docs architecture"
    Write-Host "    ./navigate.ps1 -Docs security"
    Write-Host ""
    Write-Host "  UTILITIES:"
    Write-Host "    ./navigate.ps1 -Help               Show this help"
    Write-Host ""
}

function Show-Status {
    Show-Header
    Write-Host "📊 PROJECT STATUS:" -ForegroundColor Green
    Write-Host ""
    
    # Count services
    $services = Get-ChildItem -Path $appsDir -Directory -ErrorAction SilentlyContinue
    $serviceCount = $services.Count
    
    Write-Host "  Services:" -ForegroundColor White
    Write-Host "    Total: $serviceCount microservices" -ForegroundColor Cyan
    
    # Check health_check script
    if (Test-Path (Join-Path $projectRoot "health_check.py")) {
        Write-Host ""
        Write-Host "  Quick Commands:" -ForegroundColor White
        Write-Host "    python health_check.py                  Run health check" -ForegroundColor Cyan
        Write-Host "    ./fix_services.ps1                      Fix missing directories" -ForegroundColor Cyan
    }
    
    Write-Host ""
    Write-Host "  Documentation:" -ForegroundColor White
    Write-Host "    START_HERE.md                           Entry point for new developers" -ForegroundColor Cyan
    Write-Host "    ARCHITECTURE_MAP.md                     Full architecture overview" -ForegroundColor Cyan
    Write-Host "    DASHBOARD.md                            Project metrics & status" -ForegroundColor Cyan
    Write-Host ""
}

function Show-Services {
    Show-Header
    Write-Host "📋 ALL SERVICES:" -ForegroundColor Green
    Write-Host ""
    
    $services = Get-ChildItem -Path $appsDir -Directory -ErrorAction SilentlyContinue | Sort-Object Name
    
    $i = 1
    foreach ($service in $services) {
        $readme = Join-Path $service.FullName "README.md"
        $hasReadme = Test-Path $readme
        $status = if ($hasReadme) { "📄" } else { "❌" }
        
        Write-Host "  $i. $($service.Name) $status" -ForegroundColor Cyan
        $i++
    }
    
    Write-Host ""
    Write-Host "To navigate to a service:" -ForegroundColor Yellow
    Write-Host "  ./navigate.ps1 -Service <service-name>" -ForegroundColor White
    Write-Host ""
}

function Show-Map {
    Show-Header
    Write-Host "🗺️  ARCHITECTURE MAP:" -ForegroundColor Green
    Write-Host ""
    
    $mapFile = Join-Path $projectRoot "ARCHITECTURE_MAP.md"
    if (Test-Path $mapFile) {
        Write-Host "Full architecture map available in:" -ForegroundColor Yellow
        Write-Host "  📄 ARCHITECTURE_MAP.md" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Quick overview:" -ForegroundColor White
        Write-Host ""
        Write-Host "  ┌────────────────────────────────────────────────┐" -ForegroundColor Gray
        Write-Host "  │    IDE & ANALYSIS TOOLS                        │" -ForegroundColor Gray
        Write-Host "  │  (Koda • Sourcecraft • Continue • Codeassistant)" -ForegroundColor Gray
        Write-Host "  └────────────────┬────────────────────────────────┘" -ForegroundColor Gray
        Write-Host "                   │" -ForegroundColor Gray
        Write-Host "     ┌─────────────┼──────────────┐" -ForegroundColor Gray
        Write-Host "     │             │              │" -ForegroundColor Gray
        Write-Host "  ┌──▼──┐  ┌──────▼──┐  ┌───────▼──┐" -ForegroundColor Gray
        Write-Host "  │Tier1│  │ Tier 2  │  │ Tier 3   │" -ForegroundColor Gray
        Write-Host "  │Core │  │Infra   │  │Business │" -ForegroundColor Gray
        Write-Host "  └──┬──┘  └───┬────┘  └────┬─────┘" -ForegroundColor Gray
        Write-Host "     │        │            │" -ForegroundColor Gray
        Write-Host "  ┌──▼────────▼─────────────▼──┐" -ForegroundColor Gray
        Write-Host "  │  15 Microservices          │" -ForegroundColor Gray
        Write-Host "  └──────────┬─────────────────┘" -ForegroundColor Gray
        Write-Host "             │" -ForegroundColor Gray
        Write-Host "  ┌──────────┼──────────┐" -ForegroundColor Gray
        Write-Host "  │          │          │" -ForegroundColor Gray
        Write-Host "  ▼          ▼          ▼" -ForegroundColor Gray
        Write-Host "Monitoring Database  Logs" -ForegroundColor Gray
        Write-Host ""
    }
}

function Go-ToService {
    param([string]$serviceName)
    
    $servicePath = Join-Path $appsDir $serviceName
    
    if (Test-Path $servicePath) {
        Write-Host ""
        Write-Host "📁 Service: $serviceName" -ForegroundColor Green
        Write-Host "📂 Path: $servicePath" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "To open this directory, run:" -ForegroundColor Yellow
        Write-Host "  cd $servicePath" -ForegroundColor White
        Write-Host ""
        
        # List what's in the service
        $items = Get-ChildItem -Path $servicePath -ErrorAction SilentlyContinue
        if ($items) {
            Write-Host "Contents:" -ForegroundColor Yellow
            foreach ($item in $items) {
                if ($item.PSIsContainer) {
                    Write-Host "  📁 $($item.Name)/" -ForegroundColor Cyan
                } else {
                    Write-Host "  📄 $($item.Name)" -ForegroundColor White
                }
            }
            Write-Host ""
        }
    } else {
        Write-Host ""
        Write-Host "❌ Service not found: $serviceName" -ForegroundColor Red
        Write-Host ""
        Show-Services
    }
}

# Main execution
if ($Help -or (-not $Status -and -not $List -and -not $Map -and -not $Service -and -not $Tool -and -not $Docs)) {
    Show-Help
} elseif ($Status) {
    Show-Status
} elseif ($List) {
    Show-Services
} elseif ($Map) {
    Show-Map
} elseif ($Service) {
    Go-ToService -serviceName $Service
} elseif ($Tool) {
    Write-Host ""
    Write-Host "🔧 Tool: $Tool" -ForegroundColor Green
    $toolPath = Join-Path $projectRoot ".$Tool"
    if (Test-Path $toolPath) {
        Write-Host "Found at: $toolPath" -ForegroundColor Cyan
    } else {
        Write-Host "Tool directory not found" -ForegroundColor Yellow
    }
    Write-Host ""
} elseif ($Docs) {
    Write-Host ""
    Write-Host "📚 Documentation: $Docs" -ForegroundColor Green
    Write-Host ""
    Write-Host "Search documentation files..." -ForegroundColor Yellow
    $docsPath = Join-Path $projectRoot "docs"
    if (Test-Path $docsPath) {
        Write-Host "Found in: $docsPath" -ForegroundColor Cyan
    }
    Write-Host ""
}
