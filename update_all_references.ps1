#!/usr/bin/env pwsh

Write-Host "=== UPDATING ALL REMAINING REFERENCES ===" -ForegroundColor Green

$files = @(
    "docs/archive/KODA.md",
    "docs/assistant-orchestrator/DESIGN.md",
    "docs/grants/defense-presentation.md",
    "docs/grants/EXECUTIVE_SUMMARY.md",
    "docs/grants/GigaChain_Implementation_Plan.md",
    "docs/grants/PRESENTATION-5SLIDES.md",
    "docs/integrations/career-development-integrations.md",
    "docs/integrations/career-development-status.md",
    "docs/integrations/it-compass-merger.md",
    "docs/professional-journey/README.md",
    "docs/seo/SEO-ANALYSIS-AND-IMPROVEMENTS.md",
    "docs/employer/PRESENTATION-2MIN.md"
)

$replacements = @(
    @{ old = "Cloud-Reason"; new = "Decision-Engine" },
    @{ old = "Cloud Reason"; new = "Decision-Engine" },
    @{ old = "cloud-reason"; new = "decision-engine" },
    @{ old = "cloud_reason"; new = "decision_engine" },
    @{ old = "cloud reason"; new = "decision-engine" },
    @{ old = "Arch-Compass"; new = "Infra-Orchestrator" },
    @{ old = "Arch Compass"; new = "Infra-Orchestrator" },
    @{ old = "arch-compass"; new = "infra-orchestrator" },
    @{ old = "arch_compass"; new = "infra_orchestrator" },
    @{ old = "case-2-arch-compass-cloud-reason"; new = "case-2-infra-orchestrator-decision-engine" },
    @{ old = "case-2-arch-compass-decision-engine"; new = "case-2-infra-orchestrator-decision-engine" }
)

$updatedCount = 0

foreach ($file in $files) {
    if (Test-Path $file) {
        $content = Get-Content $file -Raw
        $original = $content
        
        foreach ($replacement in $replacements) {
            $content = $content -replace [regex]::Escape($replacement.old), $replacement.new
        }
        
        if ($content -ne $original) {
            Set-Content $file -Value $content -Encoding UTF8
            $updatedCount++
            Write-Host "✅ Updated: $file" -ForegroundColor Green
        }
    }
}

Write-Host ""
Write-Host "Updated $updatedCount files" -ForegroundColor Cyan
Write-Host ""

# Check if any old names remain
Write-Host "Verifying remaining old names..." -ForegroundColor Yellow
$patterns = @("Cloud-Reason", "cloud-reason", "cloud_reason", "Arch-Compass", "arch-compass")
$remaining = 0

foreach ($pattern in $patterns) {
    $matches = @(Select-String -Path "docs/**/*.md", "*.md" -Pattern $pattern -ErrorAction SilentlyContinue)
    if ($matches.Count -gt 0) {
        $remaining += $matches.Count
        Write-Host "  ⚠️  Found $($matches.Count) remaining '$pattern' references" -ForegroundColor Yellow
    }
}

if ($remaining -eq 0) {
    Write-Host "✅ All old names have been updated!" -ForegroundColor Green
} else {
    Write-Host "⚠️  $remaining old references remain (mostly in archived/draft docs)" -ForegroundColor Yellow
}
