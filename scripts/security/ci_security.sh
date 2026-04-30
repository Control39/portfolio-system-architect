#!/bin/bash
set -e

echo "=== Running Security Checks ==="

# Detect secrets
if command -v detect-secrets &> /dev/null; then
    echo "--- Scanning for secrets ---"
    detect-secrets scan --baseline .secrets.baseline
    detect-secrets audit .secrets.baseline
else
    echo "detect-secrets not installed, skipping"
fi

# Safety scan
echo "--- Safety scan for Python dependencies ---"
safety check -r requirements-dev.txt --output json > safety-report.json || true
cat safety-report.json

# Pip-audit
echo "--- Pip-audit for vulnerabilities ---"
pip-audit -r requirements-dev.txt --format json --output pip-audit-report.json || true
cat pip-audit-report.json

# License check
echo "--- Checking licenses with liccheck ---"
if command -v liccheck &> /dev/null; then
    liccheck -r requirements-dev.txt -s licenses.ini
else
    echo "liccheck not installed, skipping"
fi

# Generate SBOM
echo "--- Generating SBOM with syft ---"
if command -v syft &> /dev/null; then
    syft . -o spdx-json=sbom.spdx.json
else
    echo "syft not installed, skipping"
fi

echo "=== Security checks completed ==="
