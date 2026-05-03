#!/usr/bin/env python3
"""Quick test of the repository audit tool."""

import os
import sys

# Add project root to sys.path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

# ruff: noqa: E402

from tools.repo_audit.checker import RepositoryAuditor  # noqa: E402
from tools.repo_audit.checks.automation import AutomationCheck  # noqa: E402
from tools.repo_audit.checks.cicd import CICDCheck  # noqa: E402
from tools.repo_audit.checks.code_quality import CodeQualityCheck  # noqa: E402
from tools.repo_audit.checks.dependencies import DependenciesCheck  # noqa: E402
from tools.repo_audit.checks.documentation import (  # noqa: E402
    DocumentationCheck,
    ReadmeQualityCheck,
)
from tools.repo_audit.checks.licensing import LicensingCheck  # noqa: E402
from tools.repo_audit.checks.monitoring import MonitoringCheck  # noqa: E402
from tools.repo_audit.checks.security import DependencySecurityCheck, SecurityCheck  # noqa: E402
from tools.repo_audit.checks.structure import NamingConventionsCheck, StructureCheck  # noqa: E402
from tools.repo_audit.checks.testing import TestCoverageCheck, TestingCheck  # noqa: E402


def main():
    repo_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    print(f"Testing audit on: {repo_path}")

    auditor = RepositoryAuditor(repo_path)
    # Documentation (2)
    auditor.register_check(DocumentationCheck)
    auditor.register_check(ReadmeQualityCheck)
    # Security (2)
    auditor.register_check(SecurityCheck)
    auditor.register_check(DependencySecurityCheck)
    # Structure (2)
    auditor.register_check(StructureCheck)
    auditor.register_check(NamingConventionsCheck)
    # CI/CD (1)
    auditor.register_check(CICDCheck)
    # Code Quality (1)
    auditor.register_check(CodeQualityCheck)
    # Testing (2)
    auditor.register_check(TestingCheck)
    auditor.register_check(TestCoverageCheck)
    # Licensing (1)
    auditor.register_check(LicensingCheck)
    # Dependencies (1) - use DependenciesCheck, skip DependencySecurityCheck (already in security)
    auditor.register_check(DependenciesCheck)
    # Monitoring (1)
    auditor.register_check(MonitoringCheck)
    # Automation (1)
    auditor.register_check(AutomationCheck)

    results = auditor.run_all()
    print(f"Total checks: {len(results)}")

    score = auditor.score()
    print(f"Overall score: {score['score']:.1f}/{score['total']:.1f} ({score['percentage']:.2f}%)")

    for cat, cat_score in score.get("by_category", {}).items():
        msg = f"{cat}: {cat_score['score']:.1f}/{cat_score['total']:.1f}"
        msg += f" ({cat_score['percentage']:.2f}%)"
        print(msg)

    # Show failures
    fails = [r for r in results if r.status == "FAIL"]
    if fails:
        print("\nFAILURES:")
        for f in fails:
            print(f"  [{f.category}] {f.description}: {f.details}")

    warnings = [r for r in results if r.status == "WARNING"]
    if warnings:
        print(f"\nWARNINGS: {len(warnings)}")

    return 0 if score["percentage"] >= 80.0 else 1


if __name__ == "__main__":
    sys.exit(main())
