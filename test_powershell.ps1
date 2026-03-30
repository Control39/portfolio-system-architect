# Test PowerShell script for VS Code integration
Write-Host "=== PowerShell Test Script ===" -ForegroundColor Green
Write-Host "PowerShell Version: $($PSVersionTable.PSVersion)"
Write-Host "Execution Policy: $(Get-ExecutionPolicy -Scope CurrentUser)"
Write-Host "Current Directory: $(Get-Location)"
Write-Host "VS Code Integration Test: PASSED" -ForegroundColor Green

# Test basic commands
$testCommands = @(
    "Get-Command",
    "Get-Module",
    "Write-Output 'Test completed'"
)

foreach ($cmd in $testCommands) {
    try {
        Invoke-Expression $cmd | Out-Null
        Write-Host "  ✅ $cmd" -ForegroundColor Cyan
    }
    catch {
        Write-Host "  ❌ $cmd - Error: $_" -ForegroundColor Red
    }
}

Write-Host "`n=== Test Complete ===" -ForegroundColor Yellow