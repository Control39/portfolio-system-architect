#!/usr/bin/env python3
"""Quick test of the repository audit tool."""

import os
import sys

# Add project root to sys.path
project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, project_root)

from tools.repo_audit.checker import RepositoryAuditor  # noqa: E402
from tools.repo_audit.checks import (  # noqa: E402
    cicd,
    code_quality,
    documentation,
    security,
    structure,
)


def main():
    repo_path = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    print(f"Testing audit on: {repo_path}")

    auditor = RepositoryAuditor(repo_path)
    auditor.register_check(documentation.DocumentationCheck)
    auditor.register_check(documentation.ReadmeQualityCheck)
    auditor.register_check(security.SecurityCheck)
    auditor.register_check(security.DependencySecurityCheck)
    auditor.register_check(structure.StructureCheck)
    auditor.register_check(structure.NamingConventionsCheck)
    auditor.register_check(cicd.CICDCheck)
    auditor.register_check(code_quality.CodeQualityCheck)

    results = auditor.run_all()
    print(f"Total checks: {len(results)}")

    score = auditor.score()
    print(
        f"Overall score: {score['score']:.1f}/{score['total']:.1f} ({score['percentage']:.2f}%)"
    )

    for cat, cat_score in score.get("by_category", {}).items():
        print(
            f"  {cat}: {cat_score['score']:.1f}/{cat_score['total']:.1f} ({cat_score['percentage']:.2f}%)"
        )

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
