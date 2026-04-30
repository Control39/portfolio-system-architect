"""Code quality checks."""

from typing import List

from tools.repo_audit.checker import BaseCheck, CheckResult


class CodeQualityCheck(BaseCheck):
    """Check for code quality tools."""

    @property
    def check_id(self) -> str:
        return "quality_essential"

    @property
    def description(self) -> str:
        return "Code quality tools configured"

    @property
    def category(self) -> str:
        return "code_quality"

    def run(self) -> List[CheckResult]:
        self.results = []
        # Ruff
        if self.check_file_exists("pyproject.toml"):
            if self.check_file_content("pyproject.toml", "ruff"):
                self._add_result(
                    "PASS", "Ruff configured in pyproject.toml", "pyproject.toml"
                )
            else:
                self._add_result(
                    "WARNING", "Ruff not configured in pyproject.toml", "pyproject.toml"
                )
        else:
            self._add_result("FAIL", "pyproject.toml missing", "pyproject.toml")

        # Black
        if self.check_file_content("pyproject.toml", "black"):
            self._add_result("PASS", "Black configured", "pyproject.toml")
        else:
            self._add_result("WARNING", "Black not configured", "pyproject.toml")

        # isort
        if self.check_file_content("pyproject.toml", "isort"):
            self._add_result("PASS", "isort configured", "pyproject.toml")
        else:
            self._add_result("WARNING", "isort not configured", "pyproject.toml")

        # mypy / pyright
        if self.check_file_exists("pyrightconfig.json"):
            self._add_result("PASS", "Pyright config exists", "pyrightconfig.json")
        elif self.check_file_exists("mypy.ini"):
            self._add_result("PASS", "Mypy config exists", "mypy.ini")
        else:
            self._add_result("WARNING", "Type checker config missing", ".")

        # .editorconfig
        if self.check_file_exists(".editorconfig"):
            self._add_result("PASS", ".editorconfig exists", ".editorconfig")
        else:
            self._add_result("WARNING", ".editorconfig missing", ".editorconfig")

        # pre‑commit hooks for quality
        if self.check_file_exists(".pre-commit-config.yaml"):
            content = (self.repo_path / ".pre-commit-config.yaml").read_text(
                encoding="utf-8"
            )
            if "ruff" in content or "black" in content or "isort" in content:
                self._add_result(
                    "PASS",
                    "Pre‑commit includes quality hooks",
                    ".pre-commit-config.yaml",
                )
            else:
                self._add_result(
                    "WARNING",
                    "Pre‑commit missing quality hooks",
                    ".pre-commit-config.yaml",
                )
        return self.results
