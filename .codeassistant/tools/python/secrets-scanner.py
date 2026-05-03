#!/usr/bin/env python3
"""
Secrets Scanner Tool

Scans codebase for potential secrets and sensitive data.
"""

import json
import os
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List

# Patterns for common secrets
SECRET_PATTERNS = {
    "aws_access_key": r"AKIA[0-9A-Z]{16}",
    "aws_secret_key": r"[0-9A-Za-z/+=]{40}",
    "github_token": r"gh[pousr]_[A-Za-z0-9_]{36,}",
    "gitlab_token": r"glpat-[A-Za-z0-9\-]{20,}",
    "slack_token": r"xox[baprs]-[0-9]{10,13}-[0-9]{10,13}[a-zA-Z0-9-]*",
    "slack_webhook": r"https://hooks\.slack\.com/services/T[a-zA-Z0-9_]{8,}/B[a-zA-Z0-9_]{8,}/[a-zA-Z0-9_]{24}",
    "google_api": r"AIza[0-9A-Za-z\-_]{35}",
    "google_oauth": r"[0-9]+-[0-9A-Za-z_]{32}\.apps\.googleusercontent\.com",
    "heroku_api": r"[hH][eE][rR][oO][kK][uU].*[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}",
    "mailgun_api": r"key-[0-9a-zA-Z]{32}",
    "mailchimp_api": r"[0-9a-f]{32}-us[0-9]{1,2}",
    "twilio_api": r"SK[0-9a-fA-F]{32}",
    "sendgrid_api": r"SG\.[0-9A-Za-z\-_]{22}\.[0-9A-Za-z\-_]{43}",
    "stripe_api": r"sk_live_[0-9a-zA-Z]{24}",
    "stripe_restricted": r"rk_live_[0-9a-zA-Z]{24}",
    "square_access": r"sq0atp-[0-9A-Za-z\-_]{22}",
    "square_oauth": r"sq0csp-[0-9A-Za-z\-_]{43}",
    "paypal_braintree": r"access_token\$production\$[0-9a-z]{16}\$[0-9a-f]{32}",
    "twilio_auth": r"AC[a-zA-Z0-9_]{32}",
    "ssh_private_key": r"-----BEGIN (?:RSA|DSA|EC|OPENSSH) PRIVATE KEY-----",
    "pgp_private_key": r"-----BEGIN PGP PRIVATE KEY BLOCK-----",
    "generic_secret": r"(?i)(password|passwd|pwd|secret|api_key|apikey|auth|token|access_token|refresh_token|private_key)\s*[:=]\s*['\"][^'\"]{8,}['\"]",
    "jwt_token": r"eyJ[A-Za-z0-9-_]+\.eyJ[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+",
    "base64_encoded": r"(?i)(?:^|[^a-zA-Z0-9+/])([A-Za-z0-9+/]{40,}={0,2})(?:[^a-zA-Z0-9+/]|$)",
}

# Files to skip
SKIP_PATTERNS = [
    r"\.git/",
    r"[/\\]venv[/\\]",  # Any venv directory (including mcp-server/venv/)
    r"[/\\]\.venv[/\\]",
    r"node_modules/",
    r"__pycache__/",
    r"\.pytest_cache/",
    r"\.tox/",
    r"dist/",
    r"build/",
    r"\.egg-info/",
    r"\.eggs/",
    r"\.mypy_cache/",
    r"\.ruff_cache/",
    r"\.coverage",
    r"coverage\.xml",
    r"htmlcov/",
    r"\.pyc$",
    r"\.pyo$",
    r"\.so$",
    r"\.dll$",
    r"\.whl$",
    r"\.lock$",
    r"package-lock\.json",
    r"pnpm-lock\.yaml",
    r"yarn\.lock",
    r"Cargo\.lock",
    r"composer\.lock",
    r"\.min\.",
    r"\.map$",
    r"\.gigacode/reports/",
    r"\.koda/logs/",
    r"\apps/cognitive-agent/data/",
    r"\apps/cognitive-agent/scans/",
]

# Directories to skip entirely
SKIP_DIRS = [
    "venv",
    ".venv",
    "node_modules",
    "__pycache__",
    ".git",
    ".pytest_cache",
    ".tox",
    "dist",
    "build",
    ".egg-info",
    ".eggs",
    ".mypy_cache",
    ".ruff_cache",
    "htmlcov",
    "reports",
    "logs",
]


@dataclass
class SecretFinding:
    file: str
    line: int
    pattern_name: str
    secret_preview: str
    severity: str  # "critical", "high", "medium", "low"


@dataclass
class ScanReport:
    files_scanned: int
    total_findings: int
    findings: List[Dict[str, Any]]
    summary: str
    false_positives_excluded: int


def should_skip(path: str) -> bool:
    """Check if file/directory should be skipped."""
    # Skip any venv directory (including nested like mcp-server/venv/)
    if re.search(r"[/\\]venv[/\\]", path):
        return True

    for pattern in SKIP_PATTERNS:
        if re.search(pattern, path):
            return True
    return False


def is_binary(file_path: Path) -> bool:
    """Check if file is binary."""
    try:
        with open(file_path, "rb") as f:
            chunk = f.read(1024)
            if b"\x00" in chunk:
                return True
    except Exception:
        return True
    return False


def scan_file(file_path: Path, base_path: Path) -> List[SecretFinding]:
    """Scan a single file for secrets."""
    findings = []

    try:
        # Skip binary files
        if is_binary(file_path):
            return findings

        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()

        for line_num, line in enumerate(lines, 1):
            for pattern_name, pattern in SECRET_PATTERNS.items():
                matches = re.finditer(pattern, line)
                for match in matches:
                    secret = match.group(0)

                    # Skip if it looks like a test/example
                    if any(
                        x in line.lower()
                        for x in [
                            "example",
                            "test",
                            "fake",
                            "dummy",
                            "placeholder",
                            "your_",
                        ]
                    ):
                        continue

                    # Skip common false positives for base64
                    if pattern_name == "base64_encoded":
                        # Skip if it looks like a path, URL, or common string
                        if any(
                            x in line
                            for x in [
                                "src/",
                                "src\\",
                                ".com",
                                ".org",
                                ".net",
                                "http",
                                "import",
                                "from",
                                "def ",
                                "class ",
                            ]
                        ):
                            continue
                        # Skip if too short or too long
                        if len(secret) < 40 or len(secret) > 200:
                            continue

                    # Determine severity
                    if pattern_name in [
                        "ssh_private_key",
                        "pgp_private_key",
                        "aws_access_key",
                        "github_token",
                    ]:
                        severity = "critical"
                    elif pattern_name in [
                        "aws_secret_key",
                        "google_api",
                        "stripe_api",
                        "generic_secret",
                    ]:
                        severity = "high"
                    elif pattern_name in ["jwt_token", "slack_token", "sendgrid_api"]:
                        severity = "medium"
                    else:
                        severity = "low"

                    # Create preview (mask most of the secret)
                    if len(secret) > 8:
                        preview = secret[:4] + "..." + secret[-4:]
                    else:
                        preview = secret[:4] + "..."

                    findings.append(
                        SecretFinding(
                            file=str(file_path.relative_to(base_path)),
                            line=line_num,
                            pattern_name=pattern_name,
                            secret_preview=preview,
                            severity=severity,
                        )
                    )

    except Exception as e:
        print(f"  ⚠️  Error reading {file_path}: {e}", file=sys.stderr)

    return findings


def scan_directory(base_path: Path) -> ScanReport:
    """Scan directory for secrets."""
    all_findings = []
    files_scanned = 0
    false_positives_excluded = 0

    for root, dirs, files in os.walk(base_path):
        # Skip hidden directories and common exclusions
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in SKIP_DIRS]

        for file in files:
            file_path = Path(root) / file
            rel_path = str(file_path.relative_to(base_path))

            if should_skip(rel_path):
                false_positives_excluded += 1
                continue

            files_scanned += 1
            findings = scan_file(file_path, base_path)
            all_findings.extend(findings)

    # Sort by severity
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    all_findings.sort(key=lambda f: (severity_order.get(f.severity, 4), f.file, f.line))

    # Generate summary
    if not all_findings:
        summary = "✅ No secrets detected"
    else:
        critical = sum(1 for f in all_findings if f.severity == "critical")
        high = sum(1 for f in all_findings if f.severity == "high")
        medium = sum(1 for f in all_findings if f.severity == "medium")
        low = sum(1 for f in all_findings if f.severity == "low")
        summary = f"❌ Found {len(all_findings)} potential secrets ({critical} critical, {high} high, {medium} medium, {low} low)"

    return ScanReport(
        files_scanned=files_scanned,
        total_findings=len(all_findings),
        findings=[asdict(f) for f in all_findings],
        summary=summary,
        false_positives_excluded=false_positives_excluded,
    )


def main():
    """Main entry point."""
    base_path = Path.cwd()

    print("=" * 70)
    print("🔍 SECRETS SCAN")
    print("=" * 70)
    print(f"\n📁 Scanning: {base_path}")
    print("🚫 Excluded: venv/, .venv/, node_modules/, .git/, reports/, logs/")
    print()

    report = scan_directory(base_path)

    print(f"📈 Files scanned: {report.files_scanned}")
    print(f"🚫 False positives excluded: {report.false_positives_excluded}")
    print(f"\n{report.summary}\n")

    if report.findings:
        print("🚨 FINDINGS:")
        current_file = None
        for finding in report.findings:
            if finding["file"] != current_file:
                current_file = finding["file"]
                print(f"\n  📄 {current_file}:")

            severity_icon = {
                "critical": "🔴",
                "high": "🟠",
                "medium": "🟡",
                "low": "🟢",
            }
            icon = severity_icon.get(finding["severity"], "⚪")
            print(
                f"    {icon} Line {finding['line']}: {finding['pattern_name']} ({finding['secret_preview']})"
            )
        print()
    else:
        print("✅ No real secrets found in source code!")

    # Save report
    report_path = base_path / ".gigacode" / "reports" / "secrets-scan.json"
    report_path.parent.mkdir(exist_ok=True)

    with open(report_path, "w") as f:
        json.dump(asdict(report), f, indent=2)

    print(f"💾 Report saved: {report_path}")

    # Exit with error if secrets found
    has_critical_or_high = any(f["severity"] in ["critical", "high"] for f in report.findings)
    sys.exit(1 if has_critical_or_high else 0)


if __name__ == "__main__":
    main()
