#!/usr/bin/env python3
"""Repository Audit Tool for Portfolio System Architect.

Evaluates repository maturity across three levels: base, professional, enterprise.
"""

import argparse
import json
import sys
from pathlib import Path


class RepositoryAudit:
    def __init__(self, repo_path: str = ".", level: str = "base"):
        self.repo_path = Path(repo_path).resolve()
        self.level = level
        self.results = []
        self.score = 0
        self.total = 0

    def check_file_exists(self, path: str, description: str) -> bool:
        """Check if a file exists."""
        full_path = self.repo_path / path
        exists = full_path.exists()
        self.total += 1
        if exists:
            self.score += 1
            self.results.append({
                "check": description,
                "status": "PASS",
                "path": path,
            })
            return True
        self.results.append({
            "check": description,
            "status": "FAIL",
            "path": path,
        })
        return False

    def check_directory_exists(self, path: str, description: str) -> bool:
        """Check if a directory exists."""
        full_path = self.repo_path / path
        exists = full_path.is_dir()
        self.total += 1
        if exists:
            self.score += 1
            self.results.append({
                "check": description,
                "status": "PASS",
                "path": path,
            })
            return True
        self.results.append({
            "check": description,
            "status": "FAIL",
            "path": path,
        })
        return False

    def check_file_content(self, path: str, description: str, keyword: str = None) -> bool:
        """Check if file contains specific keyword."""
        full_path = self.repo_path / path
        if not full_path.exists():
            self.total += 1
            self.results.append({
                "check": description,
                "status": "FAIL",
                "path": path,
                "note": "File missing",
            })
            return False
        try:
            content = full_path.read_text(encoding="utf-8")
            self.total += 1
            if (keyword and keyword in content) or not keyword:
                self.score += 1
                self.results.append({
                    "check": description,
                    "status": "PASS",
                    "path": path,
                })
                return True
            self.results.append({
                "check": description,
                "status": "FAIL",
                "path": path,
                "note": f"Keyword '{keyword}' not found",
            })
            return False
        except Exception as e:
            self.total += 1
            self.results.append({
                "check": description,
                "status": "ERROR",
                "path": path,
                "note": str(e),
            })
            return False

    def run_base_checks(self):
        """Base level checks (essential files)."""
        self.check_file_exists("README.md", "README file exists")
        self.check_file_exists("pyproject.toml", "pyproject.toml exists")
        self.check_file_exists("docker-compose.yml", "Docker Compose file exists")
        self.check_file_exists(".pre-commit-config.yaml", "Pre‑commit config exists")
        self.check_directory_exists("apps", "Apps directory exists")
        self.check_directory_exists("src", "Source directory exists")
        self.check_directory_exists("docs", "Documentation directory exists")
        self.check_file_exists("LICENSE", "License file exists")
        self.check_file_exists(".gitignore", ".gitignore exists")
        self.check_file_exists("requirements-dev.txt", "Development requirements exist")

    def run_professional_checks(self):
        """Professional level checks (CI/CD, testing)."""
        self.check_file_exists(".github/workflows/ci.yml", "GitHub Actions CI workflow exists")
        self.check_file_exists("Makefile", "Makefile exists")
        self.check_directory_exists("tests", "Tests directory exists")
        self.check_file_exists("pyproject.toml", "pyproject.toml contains pytest config",
                               keyword="[tool.pytest.ini_options]")
        self.check_file_exists("docker-compose.monitoring.yml", "Monitoring compose file exists")
        self.check_directory_exists("deployment/k8s", "Kubernetes manifests exist")

    def run_enterprise_checks(self):
        """Enterprise level checks (security, monitoring, advanced)."""
        self.check_file_exists("deployment/secrets/sealed-secrets/portfolio-secrets.example.yaml",
                               "Sealed secrets example exists")
        self.check_file_exists("monitoring/prometheus/prometheus.yml",
                               "Prometheus config exists")
        self.check_file_exists("monitoring/grafana/provisioning/dashboards/portfolio.yml",
                               "Grafana dashboard exists")
        self.check_file_exists(".coveragerc", "Coverage config exists")
        self.check_file_content("README.md", "README mentions repository audit",
                                keyword="repository audit tool")

    def run(self):
        """Run checks for the selected level."""
        if self.level == "base":
            self.run_base_checks()
        elif self.level == "professional":
            self.run_base_checks()
            self.run_professional_checks()
        elif self.level == "enterprise":
            self.run_base_checks()
            self.run_professional_checks()
            self.run_enterprise_checks()
        else:
            raise ValueError(f"Unknown level: {self.level}")

    def report(self, output_format: str = "console"):
        """Generate report."""
        percentage = (self.score / self.total * 100) if self.total > 0 else 0
        data = {
            "level": self.level,
            "score": self.score,
            "total": self.total,
            "percentage": round(percentage, 2),
            "results": self.results,
        }

        if output_format == "json":
            return json.dumps(data, indent=2, ensure_ascii=False)
        if output_format == "markdown":
            lines = [
                f"# Repository Audit Report – {self.level.upper()}",
                "",
                f"**Score**: {self.score}/{self.total} ({percentage:.2f}%)",
                "",
                "## Checks",
                "",
                "| Status | Check | Path | Note |",
                "|--------|-------|------|------|",
            ]
            for r in self.results:
                status = r["status"]
                check = r["check"]
                path = r.get("path", "")
                note = r.get("note", "")
                lines.append(f"| {status} | {check} | `{path}` | {note} |")
            return "\n".join(lines)
        # console
        print(f"\nRepository Audit – {self.level.upper()}")
        print(f"Score: {self.score}/{self.total} ({percentage:.2f}%)")
        print("\nDetailed results:")
        for r in self.results:
            status = r["status"]
            check = r["check"]
            path = r.get("path", "")
            note = f" – {r.get('note')}" if r.get("note") else ""
            print(f"  [{status}] {check} ({path}){note}")
        return ""

def main():
    parser = argparse.ArgumentParser(description="Repository audit tool")
    parser.add_argument("--level", choices=["base", "professional", "enterprise"],
                        default="base", help="Audit level")
    parser.add_argument("--output", choices=["console", "json", "markdown"],
                        default="console", help="Output format")
    parser.add_argument("--repo-path", default=".", help="Path to repository")
    parser.add_argument("--auto-fix", action="store_true", help="Auto‑fix missing files (not implemented)")
    args = parser.parse_args()

    audit = RepositoryAudit(repo_path=args.repo_path, level=args.level)
    audit.run()

    if args.output == "console":
        audit.report("console")
    elif args.output == "json":
        print(audit.report("json"))
    elif args.output == "markdown":
        print(audit.report("markdown"))

    # Exit with non‑zero if score below 80%
    if audit.total > 0 and (audit.score / audit.total) < 0.8:
        sys.exit(1)

if __name__ == "__main__":
    main()
