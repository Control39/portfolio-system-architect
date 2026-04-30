"""Documentation checks."""

from typing import List

from tools.repo_audit.checker import BaseCheck, CheckResult


class DocumentationCheck(BaseCheck):
    """Check for essential documentation files."""

    @property
    def check_id(self) -> str:
        return "doc_essential"

    @property
    def description(self) -> str:
        return "Essential documentation files exist"

    @property
    def category(self) -> str:
        return "documentation"

    def run(self) -> List[CheckResult]:
        self.results = []
        # 1. README
        self.check_file_exists("README.md")
        # 2. README in Russian (optional)
        if (self.repo_path / "README.ru.md").exists():
            self._add_result("PASS", "Russian README exists", "README.ru.md")
        else:
            self._add_result(
                "WARNING", "Russian README missing (optional)", "README.ru.md"
            )
        # 3. CONTRIBUTING
        self.check_file_exists("CONTRIBUTING.md")
        # 4. CODE_OF_CONDUCT
        self.check_file_exists("CODE_OF_CONDUCT.md")
        # 5. CHANGELOG
        self.check_file_exists("CHANGELOG.md")
        # 6. ARCHITECTURE
        self.check_file_exists("ARCHITECTURE.md")
        # 7. LICENSE
        self.check_file_exists("LICENSE")
        # 8. SECURITY
        self.check_file_exists("SECURITY.md")
        # 9. docs/ directory
        self.check_directory_exists("docs")
        # 10. docs/architecture/decisions/ (ADR)
        if (self.repo_path / "docs/architecture/decisions").is_dir():
            self._add_result(
                "PASS", "ADR directory exists", "docs/architecture/decisions"
            )
        else:
            self._add_result(
                "WARNING",
                "ADR directory missing (optional)",
                "docs/architecture/decisions",
            )
        return self.results


class ReadmeQualityCheck(BaseCheck):
    """Check README quality indicators."""

    @property
    def check_id(self) -> str:
        return "doc_readme_quality"

    @property
    def description(self) -> str:
        return "README contains key sections"

    @property
    def category(self) -> str:
        return "documentation"

    def run(self) -> List[CheckResult]:
        self.results = []
        readme_path = self.repo_path / "README.md"
        if not readme_path.exists():
            self._add_result("FAIL", "README.md missing", "README.md")
            return self.results

        content = readme_path.read_text(encoding="utf-8", errors="ignore")
        checks = [
            ("# ", "Has at least one heading"),
            ("## ", "Has sub‑headings"),
            ("```", "Has code blocks"),
            ("https://", "Has links"),
            ("![", "Has images"),
            ("Installation", "Has installation section"),
            ("Usage", "Has usage section"),
            ("Contributing", "Has contributing section"),
            ("License", "Has license section"),
        ]
        for keyword, desc in checks:
            if keyword in content:
                self._add_result("PASS", f"README contains '{keyword}'", "README.md")
            else:
                self._add_result("WARNING", f"README missing '{desc}'", "README.md")
        return self.results
