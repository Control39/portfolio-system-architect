#!/usr/bin/env python3
"""
Repository Structure Audit Tool

Analyzes repository structure and checks compliance with rules.
"""

import json
import os
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List


@dataclass
class AuditResult:
    path: str
    depth: int
    issues: List[str]
    status: str  # "pass", "warning", "fail"


@dataclass
class AuditReport:
    total_dirs: int
    max_depth: int
    violations: List[Dict[str, Any]]
    warnings: List[Dict[str, Any]]
    passed: List[str]
    summary: str


def get_directory_depth(base_path: Path, target_path: Path) -> int:
    """Calculate depth relative to base path."""
    try:
        relative = target_path.relative_to(base_path)
        return len(relative.parts)
    except ValueError:
        return 0


def check_depth_violation(path: Path, base_path: Path, max_depth: int) -> bool:
    """Check if path exceeds maximum depth."""
    depth = get_directory_depth(base_path, path)
    return depth > max_depth


def scan_directory(base_path: Path, max_depth: int = 5) -> List[AuditResult]:
    """Scan directory structure and find violations."""
    results = []

    for root, dirs, files in os.walk(base_path):
        current_path = Path(root)
        depth = get_directory_depth(base_path, current_path)

        # Skip hidden directories and common exclusions
        if any(part.startswith(".") for part in current_path.parts):
            continue
        if any(
            part in ["__pycache__", "node_modules", ".venv", "venv"] for part in current_path.parts
        ):
            continue

        issues = []
        status = "pass"

        # Check depth
        if depth > max_depth:
            issues.append(f"Depth {depth} exceeds maximum {max_depth}")
            status = "fail"

        # Check for semantic duplication
        parts = current_path.parts
        if len(parts) >= 2 and parts[-1] == parts[-2]:
            issues.append(f"Semantic duplication: {parts[-1]}")
            status = "warning" if status == "pass" else status

        results.append(
            AuditResult(
                path=str(current_path.relative_to(base_path)),
                depth=depth,
                issues=issues,
                status=status,
            )
        )

    return results


def generate_report(results: List[AuditResult]) -> AuditReport:
    """Generate audit report from results."""
    violations = [asdict(r) for r in results if r.status == "fail"]
    warnings = [asdict(r) for r in results if r.status == "warning"]
    passed = [r.path for r in results if r.status == "pass"]

    max_depth = max(r.depth for r in results) if results else 0

    if violations:
        summary = f"❌ Found {len(violations)} violations, {len(warnings)} warnings"
    elif warnings:
        summary = f"⚠️  Found {len(warnings)} warnings"
    else:
        summary = "✅ All checks passed"

    return AuditReport(
        total_dirs=len(results),
        max_depth=max_depth,
        violations=violations,
        warnings=warnings,
        passed=passed,
        summary=summary,
    )


def main():
    """Main entry point."""
    base_path = Path.cwd()
    apps_path = base_path / "apps"

    print("=" * 70)
    print("📊 REPOSITORY STRUCTURE AUDIT")
    print("=" * 70)

    if apps_path.exists():
        print(f"\n📁 Scanning: {apps_path}")
        print("📏 Max depth: 5 levels\n")

        results = scan_directory(apps_path, max_depth=5)
        report = generate_report(results)

        print(f"📈 Total directories: {report.total_dirs}")
        print(f"📏 Maximum depth: {report.max_depth}")
        print(f"\n{report.summary}\n")

        if report.violations:
            print("❌ VIOLATIONS:")
            for v in report.violations:
                print(f"  - {v['path']} (depth: {v['depth']})")
                for issue in v["issues"]:
                    print(f"    → {issue}")
            print()

        if report.warnings:
            print("⚠️  WARNINGS:")
            for w in report.warnings:
                print(f"  - {w['path']}")
                for issue in w["issues"]:
                    print(f"    → {issue}")
            print()

        # Save report
        report_path = base_path / ".gigacode" / "reports" / "audit-report.json"
        report_path.parent.mkdir(exist_ok=True)

        with open(report_path, "w") as f:
            json.dump(asdict(report), f, indent=2)

        print(f"💾 Report saved: {report_path}")

        # Exit with error if violations found
        sys.exit(1 if report.violations else 0)
    else:
        print(f"❌ Directory not found: {apps_path}")
        sys.exit(1)


if __name__ == "__main__":
    main()
