# PowerShell Script for Dependency Update
# Usage: .\scripts\update-dependencies.ps1

param(
    [switch]$All,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "         📦 DEPENDENCY UPDATE SCRIPT (PowerShell)" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Check if venv is activated
if ($env:VIRTUAL_ENV) {
    Write-Host "  ✅ Virtual environment: $env:VIRTUAL_ENV" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  Virtual environment NOT activated!" -ForegroundColor Yellow
    Write-Host "     Run: .\.venv\Scripts\Activate.ps1" -ForegroundColor Gray
    $response = Read-Host "Continue anyway? (y/n)"
    if ($response -ne 'y') {
        Write-Host "  ❌ Aborted." -ForegroundColor Red
        exit 1
    }
}

# Vulnerable packages
$packages = @{
    "jinja2" = "3.1.6"
    "langchain-text-splitters" = "1.1.2"
    "lxml" = "6.1.0"
    "pip" = "26.0"
    "pytest" = "9.0.3"
    "python-dotenv" = "1.2.2"
    "requests" = "2.33.0"
    "torch" = "2.8.0"
}

Write-Host "`n🔴 VULNERABLE PACKAGES TO UPDATE:" -ForegroundColor Red
Write-Host "───────────────────────────────────────────────────────────────" -ForegroundColor Gray

foreach ($pkg in $packages.Keys) {
    $version = $packages[$pkg]
    Write-Host "  $pkg → $version" -ForegroundColor Yellow
}

Write-Host "───────────────────────────────────────────────────────────────" -ForegroundColor Gray
Write-Host ""

if (-not $DryRun) {
    $response = Read-Host "Update these packages? (y/n)"
    if ($response -ne 'y') {
        Write-Host "  ❌ Aborted." -ForegroundColor Red
        exit 0
    }

    Write-Host ""

    $updated = 0
    $failed = 0

    foreach ($pkg in $packages.Keys) {
        $version = $packages[$pkg]
        Write-Host "  ⬆️  Updating $pkg to $version..." -ForegroundColor Cyan

        try {
            pip install --upgrade "$pkg==$version" | Out-Null
            Write-Host "     ✅ Success" -ForegroundColor Green
            $updated++
        } catch {
            Write-Host "     ❌ Failed: $_" -ForegroundColor Red
            $failed++
        }
    }

    Write-Host ""
    Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host "  ✅ Update complete: $updated updated, $failed failed" -ForegroundColor Green
    Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan

    if ($failed -eq 0) {
        Write-Host "`n  🎉 All vulnerable packages updated successfully!" -ForegroundColor Green
        Write-Host "`n  📝 Next steps:" -ForegroundColor Yellow
        Write-Host "     1. Run tests: pytest tests/ -v" -ForegroundColor Gray
        Write-Host "     2. Re-audit: pip-audit" -ForegroundColor Gray
    } else {
        Write-Host "`n  ⚠️  $failed package(s) failed to update." -ForegroundColor Yellow
    }
} else {
    Write-Host "`n🔍 DRY RUN - No changes made" -ForegroundColor Yellow
}

Write-Host ""
