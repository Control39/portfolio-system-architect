#!/usr/bin/env python3
"""Command‑line interface for repository audit tool."""

import argparse
import sys
from pathlib import Path

# Add parent directory to sys.path to allow imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tools.repo_audit.checker import RepositoryAuditor  # noqa: E402
from tools.repo_audit.checks import cicd  # noqa: E402
from tools.repo_audit.checks import code_quality  # noqa: E402
from tools.repo_audit.checks import documentation  # noqa: E402
from tools.repo_audit.checks import security  # noqa: E402
from tools.repo_audit.checks import structure  # noqa: E402; noqa: E402
from tools.repo_audit.report import ReportGenerator  # noqa: E402


def main():
    parser = argparse.ArgumentParser(
        description="Audit repository for best‑practice compliance."
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to repository (default: current directory)",
    )
    parser.add_argument(
        "--format",
        choices=["console", "json", "markdown"],
        default="console",
        help="Output format (default: console)",
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Save report to file (inferred from format if not given)",
    )
    parser.add_argument(
        "--list-checks",
        action="store_true",
        help="List available checks and exit",
    )
    args = parser.parse_args()

    if args.list_checks:
        print("Available check categories:")
        print("  - documentation")
        print("  - security")
        print("  - structure")
        print("  - cicd")
        print("  - code_quality")
        # TODO: add more as they are implemented
        return 0

    repo_path = Path(args.path).resolve()
    if not repo_path.exists():
        print(f"Error: path '{repo_path}' does not exist.", file=sys.stderr)
        return 1

    auditor = RepositoryAuditor(repo_path)
    # Register checks
    auditor.register_check(documentation.DocumentationCheck)
    auditor.register_check(documentation.ReadmeQualityCheck)
    auditor.register_check(security.SecurityCheck)
    auditor.register_check(security.DependencySecurityCheck)
    auditor.register_check(structure.StructureCheck)
    auditor.register_check(structure.NamingConventionsCheck)
    auditor.register_check(cicd.CICDCheck)
    auditor.register_check(code_quality.CodeQualityCheck)

    print(f"Running audit on {repo_path}...", file=sys.stderr)
    results = auditor.run_all()
    print(f"Completed {len(results)} checks.", file=sys.stderr)

    report = ReportGenerator(auditor)

    if args.output:
        out_path = Path(args.output)
        saved = report.save(out_path, format=args.format)
        print(f"Report saved to {saved}", file=sys.stderr)
    else:
        if args.format == "json":
            print(report.to_json())
        elif args.format == "markdown":
            print(report.to_markdown())
        else:
            print(report.to_console())

    # Exit with non‑zero if score below 80%
    score = auditor.score()
    if score["percentage"] < 80.0:
        print(
            f"Score {score['percentage']:.2f}% is below 80% – audit failed.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
