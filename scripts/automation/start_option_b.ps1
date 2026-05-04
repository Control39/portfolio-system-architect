#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Option B - Proper Fix Starter
    Все необходимое для начала Option B (2-3 недели, 90% результат)

.EXAMPLE
    .\start_option_b.ps1                    # Запустить все подготовки
    .\start_option_b.ps1 -ShowPlan          # Только показать план
#>

param(
    [switch]$ShowPlan,
    [switch]$Dry
)

function Write-Header { param([string]$Text) Write-Host "`n✨ $Text`n" -ForegroundColor Cyan -BackgroundColor Black }
function Write-Step { param([string]$Text) Write-Host "  ➜ $Text" -ForegroundColor Yellow }
function Write-OK { param([string]$Text) Write-Host "  ✅ $Text" -ForegroundColor Green }
function Write-Warn { param([string]$Text) Write-Host "  ⚠️  $Text" -ForegroundColor Yellow }
function Write-Info { param([string]$Text) Write-Host "  ℹ️  $Text" -ForegroundColor Gray }

Write-Header "OPTION B - PROPER FIX STARTER"

Write-Host "This script prepares your project for the 2-3 week proper fix" -ForegroundColor White
Write-Host "Goal: 53% → 90%+ test coverage + standardized structure" -ForegroundColor White

if ($ShowPlan) {
    Write-Header "YOUR PLAN"
    Write-Host @"
📅 WEEK 1: Foundation (20 hours)
   1. Add config directories (12 services)        - 30 minutes
   2. Add src directories (5 services)            - 15 minutes
   3. Standardize structure for all              - 3 hours
   4. Add basic tests to 7 services              - 12 hours

📅 WEEK 2: Improvement (20 hours)
   5. Add integration tests (5 services)         - 10 hours
   6. Improve test quality (8 services)          - 8 hours
   7. Update documentation & CI/CD               - 2 hours

📅 WEEK 3: Polish (10 hours)
   8. Full health check & validation             - 3 hours
   9. Fix issues & edge cases                    - 4 hours
   10. Final commit & merge                       - 3 hours

⏱️  TOTAL: 40-50 hours over 2-3 weeks
💪 Estimated: 3-4 hours per day for 2-3 weeks

📊 EXPECTED RESULTS:
   ✅ All 15 services with standard structure
   ✅ All 15 services with tests
   ✅ 90%+ code coverage
   ✅ Integrated CI/CD pipeline
   ✅ Clean, organized codebase
"@
    exit
}

Write-Header "STEP 1: Verify Project Structure"

$appsDirExists = Test-Path "portfolio-system-architect/apps"
if ($appsDirExists) {
    Write-OK "Found apps directory"
    $serviceCount = @(Get-ChildItem "portfolio-system-architect/apps" -Directory).Count
    Write-Info "Services found: $serviceCount"
} else {
    Write-Warn "Apps directory not found - make sure you're in the right location"
    exit 1
}

Write-Header "STEP 2: Generate Test Templates"

Write-Step "Creating test_basic.py for 7 services..."
if ($Dry) {
    Write-Info "DRY RUN: Would create test templates"
} else {
    try {
        cd portfolio-system-architect
        python bulk_test_generator.py
        cd ..
        Write-OK "Test templates created"
    } catch {
        Write-Warn "Could not run bulk_test_generator: $_"
    }
}

Write-Header "STEP 3: Verify Everything Ready"

Write-Step "Checking for required files..."

$filesNeeded = @(
    "portfolio-system-architect/OPTION_B_EXECUTION_PLAN.md",
    "portfolio-system-architect/health_check.py",
    "portfolio-system-architect/complete_diagnostic.py",
    "portfolio-system-architect/bulk_test_generator.py"
)

$allGood = $true
foreach ($file in $filesNeeded) {
    if (Test-Path $file) {
        Write-OK "Found: $file"
    } else {
        Write-Warn "Missing: $file"
        $allGood = $false
    }
}

Write-Header "STEP 4: Run Initial Health Check"

if ($allGood) {
    Write-Step "Running health check..."
    try {
        cd portfolio-system-architect
        python health_check.py | Select-Object -Last 20
        cd ..
    } catch {
        Write-Warn "Could not run health check: $_"
    }
} else {
    Write-Warn "Some files are missing, skipping health check"
}

Write-Header "READY TO START!"

Write-Host @"
✅ Your project is ready for Option B!

📋 WHAT TO DO NOW:

1. Read the execution plan:
   💻 cat portfolio-system-architect/OPTION_B_EXECUTION_PLAN.md

2. Start Week 1:
   - Day 1-2: Add directories (use fix_services.ps1)
   - Day 3-5: Standardize structure
   - Day 6-7: Write basic tests

3. Each day:
   - Run: python portfolio-system-architect/health_check.py
   - Check progress: cat HEALTH_CHECK_REPORT.md
   - Update TODOs: list_todos

4. Tools available:
   - fix_services.ps1          (auto-fix structure)
   - bulk_test_generator.py    (create test templates)
   - health_check.py           (daily validation)
   - navigate.ps1              (project navigation)

⏰ ESTIMATE: 3-4 hours per day for 2-3 weeks

🚀 YOU'VE GOT THIS!

Questions? Check:
  - OPTION_B_EXECUTION_PLAN.md (detailed timeline)
  - DIAGNOSTIC_SUMMARY.md (project analysis)
  - HEALTH_CHECK_REPORT.md (what needs fixing)

"@

Write-Host "Ready to begin? Start with Week 1 tasks! 💪" -ForegroundColor Green
