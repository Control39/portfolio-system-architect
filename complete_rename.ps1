#!/usr/bin/env pwsh

Write-Host "=== COMPLETING SERVICE RENAME ===" -ForegroundColor Green
Write-Host ""

# 1. Rename case-2 folder
$oldCasePath = "docs/cases/cases/presentation-cases/case-2-arch-compass-cloud-reason"
$newCasePath = "docs/cases/cases/presentation-cases/case-2-infra-orchestrator-decision-engine"

if (Test-Path $oldCasePath) {
    Write-Host "[1] Renaming case-2 folder..." -ForegroundColor Cyan
    Move-Item -Path $oldCasePath -Destination $newCasePath -Force
    Write-Host "  ✅ Renamed: case-2-arch-compass-cloud-reason → case-2-infra-orchestrator-decision-engine" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  Folder not found at $oldCasePath" -ForegroundColor Yellow
}

# 2. Update case-2 README content
Write-Host ""
Write-Host "[2] Updating case-2 README content..." -ForegroundColor Cyan

$readmeFile = "docs/cases/cases/presentation-cases/case-2-infra-orchestrator-decision-engine/README.md"

if (Test-Path $readmeFile) {
    $content = Get-Content $readmeFile -Raw
    
    # Replace title
    $content = $content -replace "# Кейс 2: Интеграция Infra-Orchestrator и Cloud-Reason", `
                              "# Кейс 2: Интеграция Infra-Orchestrator и Decision-Engine"
    
    # Replace description
    $content = $content -replace "Cloud-Reason: облачная платформа для анализа и принятия решений", `
                              "Decision-Engine: система принятия решений с RAG и логикой вывода"
    
    # Replace mermaid diagram references
    $content = $content -replace "C\[Cloud-Reason\]", "C[Decision-Engine]"
    
    Set-Content $readmeFile -Value $content -Encoding UTF8
    Write-Host "  ✅ Updated case-2 README" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  README not found at $readmeFile" -ForegroundColor Yellow
}

# 3. Update docs references
Write-Host ""
Write-Host "[3] Updating documentation files..." -ForegroundColor Cyan

$docFiles = @(
    "docs/adr/ADR-004-data-storage-format.md",
    "docs/methodology/README.md",
    "docs/methodology/METHODOLOGY.md",
    "docs/methodology/ARCHITECTURE.md"
)

foreach ($file in $docFiles) {
    if (Test-Path $file) {
        $content = Get-Content $file -Raw
        
        # Replace Cloud-Reason
        if ($content -match "Cloud-Reason|Cloud Reason|cloud-reason|cloud_reason") {
            $content = $content -replace "Cloud-Reason", "Decision-Engine"
            $content = $content -replace "Cloud Reason", "Decision-Engine"
            $content = $content -replace "cloud-reason", "decision-engine"
            $content = $content -replace "cloud_reason", "decision_engine"
            
            Set-Content $file -Value $content -Encoding UTF8
            Write-Host "  ✅ Updated: $file" -ForegroundColor Green
        }
        
        # Replace Arch-Compass
        if ($content -match "Arch-Compass|Arch Compass|arch-compass") {
            $content = Get-Content $file -Raw
            $content = $content -replace "Arch-Compass", "Infra-Orchestrator"
            $content = $content -replace "Arch Compass", "Infra-Orchestrator"
            $content = $content -replace "arch-compass", "infra-orchestrator"
            
            Set-Content $file -Value $content -Encoding UTF8
            Write-Host "  ✅ Updated: $file" -ForegroundColor Green
        }
    }
}

# 4. Update case references in docs/cases/cases/presentation-cases
Write-Host ""
Write-Host "[4] Flattening case structure (docs/cases/cases/ → docs/cases/)..." -ForegroundColor Cyan

if (Test-Path "docs/cases/cases/presentation-cases") {
    Get-ChildItem "docs/cases/cases/presentation-cases" | ForEach-Object {
        $src = $_.FullName
        $dst = "docs/cases/$($_.Name)"
        Move-Item -Path $src -Destination $dst -Force
        Write-Host "  ✅ Moved: $($_.Name)" -ForegroundColor Green
    }
}

if (Test-Path "docs/cases/cases/thinking-cases") {
    Get-ChildItem "docs/cases/cases/thinking-cases" | Where-Object { $_.Name -ne "README.md" } | ForEach-Object {
        $src = $_.FullName
        $dst = "docs/cases/thinking-cases/$($_.Name)"
        Move-Item -Path $src -Destination $dst -Force
        Write-Host "  ✅ Moved: thinking-cases/$($_.Name)" -ForegroundColor Green
    }
}

if (Test-Path "docs/cases/cases/evolution-cases") {
    Get-ChildItem "docs/cases/cases/evolution-cases" | ForEach-Object {
        $src = $_.FullName
        $dst = "docs/cases/evolution-cases/$($_.Name)"
        Move-Item -Path $src -Destination $dst -Force
        Write-Host "  ✅ Moved: evolution-cases/$($_.Name)" -ForegroundColor Green
    }
}

# Delete empty nested structure
if (Test-Path "docs/cases/cases") {
    Remove-Item "docs/cases/cases" -Recurse -Force
    Write-Host "  ✅ Removed empty docs/cases/cases/" -ForegroundColor Green
}

Write-Host ""
Write-Host "=== CLEANUP COMPLETE ===" -ForegroundColor Green
Write-Host ""
Write-Host "Summary:" -ForegroundColor Cyan
Write-Host "  ✅ Service names updated:" -ForegroundColor Green
Write-Host "     - Cloud-Reason → Decision-Engine" 
Write-Host "     - Arch-Compass → Infra-Orchestrator"
Write-Host "  ✅ Case structure flattened"
Write-Host "  ✅ Documentation updated"
Write-Host ""
Write-Host "Next: Run tests and commit changes" -ForegroundColor Yellow
