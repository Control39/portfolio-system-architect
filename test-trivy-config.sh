#!/bin/bash
# Test script to validate Trivy secret configuration

echo "Testing Trivy secret configuration..."
echo "====================================="

# Check if trivy is installed
if ! command -v trivy &> /dev/null; then
    echo "Trivy is not installed. Installing via curl..."
    curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin
fi

# Validate YAML configuration
echo "1. Validating trivy-secret.yaml YAML syntax..."
python3 -c "import yaml, sys; f=open('trivy-secret.yaml'); yaml.safe_load(f); print('✓ trivy-secret.yaml is valid YAML')"

# Count custom rules
echo "2. Checking custom rules..."
RULES_COUNT=$(python3 -c "import yaml; f=open('trivy-secret.yaml'); data=yaml.safe_load(f); print(len(data.get('rules', {}).get('custom', [])))")
echo "   Found $RULES_COUNT custom secret detection rules"

# Test with a sample file containing fake secrets
echo "3. Creating test file with fake secrets..."
cat > test-secrets.txt << 'EOF'
# This is a test file with fake secrets
AWS_ACCESS_KEY=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
GITHUB_TOKEN=ghp_abcdefghijklmnopqrstuvwxyz0123456789
SLACK_TOKEN=xoxb-123456789012-123456789012-123456789012-abc123def456
PRIVATE_KEY=-----BEGIN PRIVATE KEY-----
DATABASE_PASSWORD=supersecret123
API_KEY=sk_test_abcdefghijklmnopqrstuvwxyz
EOF

echo "4. Running Trivy scan on test file..."
echo "   (This might take a moment to download vulnerability databases)"
trivy fs --secret-config trivy-secret.yaml test-secrets.txt 2>&1 | grep -A5 -B5 "Secret" || echo "   No secrets detected or Trivy not fully configured"

# Cleanup
echo "5. Cleaning up test file..."
rm -f test-secrets.txt

echo "====================================="
echo "Test completed. Check output above for any issues."
echo ""
echo "To run full scan: trivy fs --secret-config trivy-secret.yaml ."
echo "To scan without secret detection: trivy fs ."