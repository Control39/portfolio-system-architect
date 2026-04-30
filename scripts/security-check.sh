#!/bin/bash

# Security check script for portfolio-system-architect
# Run this script to perform security checks locally

set -e

echo "🔒 Starting security checks for portfolio-system-architect"
echo "=========================================================="

# Check if required tools are installed
check_tool() {
    if ! command -v $1 &> /dev/null; then
        echo "❌ $1 is not installed. Please install it first."
        exit 1
    fi
    echo "✅ $1 is installed"
}

echo "1. Checking required tools..."
check_tool "bandit"
check_tool "safety"
check_tool "trivy"

echo ""
echo "2. Running Bandit security scan..."
bandit -r . -f json -o bandit-report.json || true
echo "Bandit scan completed. Report saved to bandit-report.json"

echo ""
echo "3. Checking Python dependencies with safety..."
safety check --full-report || true

echo ""
echo "4. Running Trivy vulnerability scan..."
trivy fs . --severity HIGH,CRITICAL --format table || true

echo ""
echo "5. Checking for secrets in code..."
if [ -f ".secrets.baseline" ]; then
    detect-secrets scan --baseline .secrets.baseline
else
    echo "⚠️  No secrets baseline found. Creating one..."
    detect-secrets scan > .secrets.baseline
fi

echo ""
echo "6. Checking Docker images..."
if [ -f "gateway/Dockerfile" ]; then
    echo "Scanning gateway/Dockerfile..."
    trivy config gateway/Dockerfile
fi

if [ -f "api/Dockerfile" ]; then
    echo "Scanning api/Dockerfile..."
    trivy config api/Dockerfile
fi

echo ""
echo "7. Checking for outdated dependencies..."
pip list --outdated || true

echo ""
echo "=========================================================="
echo "🔒 Security checks completed!"
echo ""
echo "Summary:"
echo "- Bandit report: bandit-report.json"
echo "- Dependency vulnerabilities: Check safety output above"
echo "- Container vulnerabilities: Check Trivy output above"
echo ""
echo "To fix issues:"
echo "1. Update vulnerable dependencies: pip install --upgrade <package>"
echo "2. Fix security issues reported by Bandit"
echo "3. Update Docker base images if needed"
echo "=========================================================="
