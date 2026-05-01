"""Testing checks."""

from typing import List

from tools.repo_audit.checker import BaseCheck, CheckResult


class TestingCheck(BaseCheck):
    """Check for testing configuration and coverage."""

    @property
    def check_id(self) -> str:
        return "testing_essential"

    @property
    def description(self) -> str:
        return "Testing infrastructure configured"

    @property
    def category(self) -> str:
        return "testing"

    def run(self) -> List[CheckResult]:
        self.results = []
        # 1. tests/ directory
        self.check_directory_exists("tests")
        # 2. pytest configuration
        if self.check_file_exists("pytest.ini"):
            self._add_result("PASS", "pytest.ini exists", "pytest.ini")
        else:
            self._add_result("WARNING", "pytest.ini missing", "pytest.ini")
        # 3. coverage configuration
        if self.check_file_exists(".coveragerc"):
            self._add_result("PASS", ".coveragerc exists", ".coveragerc")
        else:
            self._add_result("WARNING", ".coveragerc missing", ".coveragerc")
        # 4. test files pattern
        test_files = list(self.repo_path.rglob("test_*.py")) + list(
            self.repo_path.rglob("*_test.py")
        )
        if test_files:
            self._add_result("PASS", f"Test files found: {len(test_files)}", "tests/")
        else:
            self._add_result("FAIL", "No test files found", "tests/")
        # 5. requirements-dev.txt includes testing packages
        if self.check_file_exists("requirements-dev.txt"):
            content = (self.repo_path / "requirements-dev.txt").read_text(
                encoding="utf-8", errors="ignore"
            )
            packages = ["pytest", "coverage", "pytest-cov", "pytest-asyncio"]
            found = []
            for pkg in packages:
                if pkg in content.lower():
                    found.append(pkg)
            if found:
                self._add_result(
                    "PASS",
                    f"Testing packages in dev requirements: {', '.join(found)}",
                    "requirements-dev.txt",
                )
            else:
                self._add_result(
                    "WARNING",
                    "No testing packages in dev requirements",
                    "requirements-dev.txt",
                )
        # 6. GitHub Actions test workflow
        workflows_dir = self.repo_path / ".github/workflows"
        if workflows_dir.is_dir():
            test_workflows = list(workflows_dir.glob("*test*.yml")) + list(
                workflows_dir.glob("*test*.yaml")
            )
            if test_workflows:
                self._add_result(
                    "PASS",
                    f"Test workflows found: {[w.name for w in test_workflows]}",
                    ".github/workflows",
                )
            else:
                self._add_result("WARNING", "No dedicated test workflow", ".github/workflows")
        # 7. tox configuration (optional)
        if self.check_file_exists("tox.ini"):
            self._add_result("PASS", "tox.ini exists", "tox.ini")
        else:
            self._add_result("INFO", "tox.ini missing (optional)", "tox.ini")
        return self.results


class TestCoverageCheck(BaseCheck):
    """Check for test coverage reporting."""

    @property
    def check_id(self) -> str:
        return "testing_coverage"

    @property
    def description(self) -> str:
        return "Test coverage reporting configured"

    @property
    def category(self) -> str:
        return "testing"

    def run(self) -> List[CheckResult]:
        self.results = []
        # 1. codecov or coveralls configuration
        if self.check_file_exists(".codecov.yml"):
            self._add_result("PASS", "Codecov config exists", ".codecov.yml")
        else:
            self._add_result("WARNING", "Codecov config missing", ".codecov.yml")
        # 2. coverage badge in README
        readme_path = self.repo_path / "README.md"
        if readme_path.exists():
            content = readme_path.read_text(encoding="utf-8", errors="ignore")
            if "coverage" in content.lower() or "codecov" in content.lower():
                self._add_result("PASS", "README mentions coverage", "README.md")
            else:
                self._add_result("INFO", "README does not mention coverage", "README.md")
        # 3. coverage report directory
        if (self.repo_path / "htmlcov").is_dir():
            self._add_result(
                "WARNING",
                "htmlcov directory exists (should be in .gitignore)",
                "htmlcov",
            )
        # 4. .gitignore excludes coverage files
        if self.check_file_content(".gitignore", "htmlcov"):
            self._add_result("PASS", ".gitignore excludes htmlcov", ".gitignore")
        else:
            self._add_result("WARNING", ".gitignore does not exclude htmlcov", ".gitignore")
        return self.results
