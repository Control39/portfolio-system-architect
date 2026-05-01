"""Licensing checks."""

from typing import List

from tools.repo_audit.checker import BaseCheck, CheckResult


class LicensingCheck(BaseCheck):
    """Check for licensing files and compliance."""

    @property
    def check_id(self) -> str:
        return "licensing_essential"

    @property
    def description(self) -> str:
        return "Licensing files and compliance"

    @property
    def category(self) -> str:
        return "licensing"

    def run(self) -> List[CheckResult]:
        self.results = []
        # 1. LICENSE file
        license_path = self.repo_path / "LICENSE"
        if license_path.exists():
            self._add_result("PASS", "LICENSE file exists", "LICENSE")
            # Check license type
            content = license_path.read_text(encoding="utf-8", errors="ignore")
            common_licenses = [
                "MIT License",
                "Apache License",
                "GNU General Public License",
                "BSD License",
                "Creative Commons",
                "Mozilla Public License",
            ]
            found = False
            for lic in common_licenses:
                if lic in content:
                    self._add_result("PASS", f"License appears to be {lic}", "LICENSE")
                    found = True
                    break
            if not found:
                self._add_result("WARNING", "License type not recognized", "LICENSE")
        else:
            self._add_result("FAIL", "LICENSE file missing", "LICENSE")

        # 2. LICENSE in README
        readme_path = self.repo_path / "README.md"
        if readme_path.exists():
            content = readme_path.read_text(encoding="utf-8", errors="ignore")
            if "license" in content.lower():
                self._add_result("PASS", "README mentions license", "README.md")
            else:
                self._add_result(
                    "WARNING", "README does not mention license", "README.md"
                )

        # 3. NOTICE file (optional)
        if self.check_file_exists("NOTICE"):
            self._add_result("PASS", "NOTICE file exists", "NOTICE")
        else:
            self._add_result("INFO", "NOTICE file missing (optional)", "NOTICE")

        # 4. COPYING file (optional, GPL)
        if self.check_file_exists("COPYING"):
            self._add_result("PASS", "COPYING file exists", "COPYING")
        else:
            self._add_result("INFO", "COPYING file missing (optional)", "COPYING")

        # 5. License headers in source files (sample check)
        py_files = list(self.repo_path.rglob("*.py"))[:5]  # limit to 5 files
        headers_checked = 0
        for py_file in py_files:
            try:
                content = py_file.read_text(encoding="utf-8", errors="ignore")
                if "Copyright" in content or "license" in content.lower():
                    headers_checked += 1
            except Exception:
                pass
        if headers_checked > 0:
            self._add_result(
                "INFO",
                f"License headers found in {headers_checked} sample Python files",
                "src/",
            )
        else:
            self._add_result(
                "WARNING",
                "No license headers found in sample Python files",
                "src/",
            )

        # 6. SPDX identifier in package metadata
        pyproject_path = self.repo_path / "pyproject.toml"
        if pyproject_path.exists():
            content = pyproject_path.read_text(encoding="utf-8", errors="ignore")
            if "license" in content.lower():
                self._add_result(
                    "PASS", "pyproject.toml contains license field", "pyproject.toml"
                )
            else:
                self._add_result(
                    "WARNING", "pyproject.toml missing license field", "pyproject.toml"
                )

        # 7. Open source compliance (presence of .reuse/dep5)
        if (self.repo_path / ".reuse").is_dir():
            self._add_result("PASS", "REUSE compliance directory exists", ".reuse")
        else:
            self._add_result("INFO", "REUSE compliance not configured", ".reuse")

        return self.results
