# Test script to validate Trivy secret configuration (PowerShell version)

Write-Host "Testing Trivy secret configuration..." -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

# Check if trivy is installed
$trivyPath = Get-Command trivy -ErrorAction SilentlyContinue
if (-not $trivyPath) {
    Write-Host "Trivy is not installed. Please install it first:" -ForegroundColor Yellow
    Write-Host "  wing install trivy" -ForegroundColor Yellow
    Write-Host "  or download from: https://github.com/aquasecurity/trivy/releases" -ForegroundColor Yellow
    exit 1
}

# Validate YAML configuration
Write-Host "1. Validating trivy-secret.yaml YAML syntax..." -ForegroundColor Green
try {
    python -c "import yaml, sys; f=open('trivy-secret.yaml'); yaml.safe_load(f); print('✓ trivy-secret.yaml is valid YAML')"
} catch {
    Write-Host "  ✗ Error validating YAML: $_" -ForegroundColor Red
}

# Count custom rules
Write-Host "2. Checking custom rules..." -ForegroundColor Green
try {
    $rulesCount = python -c "import yaml; f=open('trivy-secret.yaml'); data=yaml.safe_load(f); print(len(data.get('rules', {}).get('custom', [])))"
    Write-Host "   Found $rulesCount custom secret detection rules" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Error counting rules: $_" -ForegroundColor Red
}

# Test with a sample file containing fake secrets
Write-Host "3. Creating test file with fake secrets..." -ForegroundColor Green
@"
# This is a test file with fake secrets
AWS_ACCESS_KEY=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
GITHUB_TOKEN=ghp_abcdefghijklmnopqrstuvwxyz0123456789
SLACK_TOKEN=xoxb-123456789012-123456789012-123456789012-abc123def456
PRIVATE_KEY=-----BEGIN PRIVATE KEY-----
DATABASE_PASSWORD=supersecret123
API_KEY=sk_test_abcdefghijklmnopqrstuvwxyz
"@ | Out-File -FilePath test-secrets.txt -Encoding UTF8

Write-Host "4. Running Trivy scan on test file..." -ForegroundColor Green
Write-Host "   (This might take a moment to download vulnerability databases)" -ForegroundColor Yellow
$output = trivy fs --secret-config trivy-secret.yaml test-secrets.txt 2>&1
if ($output -match "Secret") {
    Write-Host "   Secrets detected (expected):" -ForegroundColor Green
    $output | Select-String -Pattern "Secret" | ForEach-Object { Write-Host "   $_" -ForegroundColor Yellow }
} else {
    Write-Host "   No secrets detected or Trivy not fully configured" -ForegroundColor Yellow
}

# Cleanup
Write-Host "5. Cleaning up test file..." -ForegroundColor Green
Remove-Item test-secrets.txt -ErrorAction SilentlyContinue

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Test completed. Check output above for any issues." -ForegroundColor Cyan
Write-Host ""
Write-Host "To run full scan: trivy fs --secret-config trivy-secret.yaml ." -ForegroundColor Green
Write-Host "To scan without secret detection: trivy fs ." -ForegroundColor Green