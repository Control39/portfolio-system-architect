"""Dependency management checks."""

from typing import List

from tools.repo_audit.checker import BaseCheck, CheckResult


class DependenciesCheck(BaseCheck):
    """Check for dependency management best practices."""

    @property
    def check_id(self) -> str:
        return "deps_essential"

    @property
    def description(self) -> str:
        return "Dependency management configured"

    @property
    def category(self) -> str:
        return "dependencies"

    def run(self) -> List[CheckResult]:
        self.results = []
        # 1. requirements.txt
        if self.check_file_exists("requirements.txt"):
            self._add_result("PASS", "requirements.txt exists", "requirements.txt")
        else:
            self._add_result("WARNING", "requirements.txt missing", "requirements.txt")

        # 2. requirements-dev.txt
        if self.check_file_exists("requirements-dev.txt"):
            self._add_result("PASS", "requirements-dev.txt exists", "requirements-dev.txt")
        else:
            self._add_result("WARNING", "requirements-dev.txt missing", "requirements-dev.txt")

        # 3. pyproject.toml (modern Python)
        if self.check_file_exists("pyproject.toml"):
            self._add_result("PASS", "pyproject.toml exists", "pyproject.toml")
        else:
            self._add_result("WARNING", "pyproject.toml missing", "pyproject.toml")

        # 4. Pipfile / Pipfile.lock (optional)
        if self.check_file_exists("Pipfile"):
            self._add_result("PASS", "Pipfile exists", "Pipfile")
        else:
            self._add_result("INFO", "Pipfile missing (optional)", "Pipfile")

        # 5. poetry.lock (optional)
        if self.check_file_exists("poetry.lock"):
            self._add_result("PASS", "poetry.lock exists", "poetry.lock")
        else:
            self._add_result("INFO", "poetry.lock missing (optional)", "poetry.lock")

        # 6. .python-version or runtime.txt
        if self.check_file_exists(".python-version"):
            self._add_result("PASS", ".python-version exists", ".python-version")
        elif self.check_file_exists("runtime.txt"):
            self._add_result("PASS", "runtime.txt exists", "runtime.txt")
        else:
            self._add_result("INFO", "Python version file missing (optional)", ".python-version")

        # 7. Dependabot configuration
        dependabot_dir = self.repo_path / ".github/dependabot.yml"
        if dependabot_dir.exists():
            self._add_result("PASS", "Dependabot config exists", ".github/dependabot.yml")
        else:
            self._add_result("WARNING", "Dependabot config missing", ".github/dependabot.yml")

        # 8. Renovate configuration
        if self.check_file_exists("renovate.json") or self.check_file_exists(".renovaterc"):
            self._add_result("PASS", "Renovate config exists", "renovate.json")
        else:
            self._add_result("INFO", "Renovate config missing (optional)", "renovate.json")

        # 9. pip-audit in dev requirements (already checked in security, but repeat)
        if self.check_file_exists("requirements-dev.txt"):
            content = (self.repo_path / "requirements-dev.txt").read_text(
                encoding="utf-8", errors="ignore"
            )
            if "pip-audit" in content.lower():
                self._add_result("PASS", "pip-audit in dev requirements", "requirements-dev.txt")
            else:
                self._add_result(
                    "WARNING",
                    "pip-audit not in dev requirements",
                    "requirements-dev.txt",
                )

        # 10. .gitignore excludes virtual environments
        if self.check_file_content(".gitignore", ".venv") or self.check_file_content(
            ".gitignore", "venv"
        ):
            self._add_result("PASS", ".gitignore excludes virtual environments", ".gitignore")
        else:
            self._add_result(
                "WARNING",
                ".gitignore does not exclude virtual environments",
                ".gitignore",
            )

        return self.results


class DependencySecurityCheck(BaseCheck):
    """Check dependency security scanning."""

    @property
    def check_id(self) -> str:
        return "deps_security"

    @property
    def description(self) -> str:
        return "Dependency security scanning configured"

    @property
    def category(self) -> str:
        return "dependencies"

    def run(self) -> List[CheckResult]:
        self.results = []
        # 1. GitHub Actions dependency review
        workflows_dir = self.repo_path / ".github/workflows"
        if workflows_dir.is_dir():
            dep_review = list(workflows_dir.glob("*dependency*")) + list(
                workflows_dir.glob("*dependabot*")
            )
            if dep_review:
                self._add_result(
                    "PASS",
                    f"Dependency review workflows: {[w.name for w in dep_review]}",
                    ".github/workflows",
                )
            else:
                self._add_result(
                    "WARNING",
                    "No dependency review workflow",
                    ".github/workflows",
                )
        # 2. Snyk, Trivy, etc. configuration
        if self.check_file_exists(".trivyignore"):
            self._add_result("PASS", "Trivy ignore file exists", ".trivyignore")
        else:
            self._add_result("INFO", "Trivy ignore file missing", ".trivyignore")
        # 3. .snyk file
        if self.check_file_exists(".snyk"):
            self._add_result("PASS", "Snyk config exists", ".snyk")
        else:
            self._add_result("INFO", "Snyk config missing", ".snyk")
        # 4. OSS Index, etc.
        return self.results
