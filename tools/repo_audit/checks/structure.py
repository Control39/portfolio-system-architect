"""Repository structure checks."""

from typing import List

from tools.repo_audit.checker import BaseCheck, CheckResult


class StructureCheck(BaseCheck):
    """Check repository layout and organization."""

    @property
    def check_id(self) -> str:
        return "struct_essential"

    @property
    def description(self) -> str:
        return "Repository follows standard structure"

    @property
    def category(self) -> str:
        return "structure"

    def run(self) -> List[CheckResult]:
        self.results = []
        # Essential directories
        dirs = [
            ("apps", "Applications directory"),
            ("src", "Source code directory"),
            ("tests", "Tests directory"),
            ("docs", "Documentation directory"),
            ("deployment", "Deployment configurations"),
            ("docker", "Docker configurations"),
            ("monitoring", "Monitoring configurations"),
            ("scripts", "Utility scripts"),
            ("tools", "Development tools"),
            ("config", "Configuration files"),
        ]
        for path, desc in dirs:
            if (self.repo_path / path).is_dir():
                self._add_result("PASS", f"{desc} exists", path)
            else:
                self._add_result("WARNING", f"{desc} missing", path)

        # Check for clutter in root
        root_files = list(self.repo_path.iterdir())
        allowed_extensions = {
            ".md",
            ".yml",
            ".yaml",
            ".toml",
            ".ini",
            ".txt",
            ".json",
            ".py",
            ".ps1",
            ".sh",
        }
        clutter = []
        for f in root_files:
            if (
                f.is_file()
                and f.suffix not in allowed_extensions
                and f.name
                not in {
                    "LICENSE",
                    "Dockerfile",
                    "Makefile",
                    "docker-compose.yml",
                    ".gitignore",
                    ".gitattributes",
                    ".pre-commit-config.yaml",
                    ".bandit.yml",
                    ".trivyignore",
                    ".secrets.baseline",
                    ".codecov.yml",
                    "pyproject.toml",
                    "pytest.ini",
                    "pyrightconfig.json",
                    "requirements.txt",
                    "requirements-dev.txt",
                    "requirements.in",
                    "requirements-dev.in",
                    "mkdocs.yml",
                    "sonar-project.properties",
                }
            ):
                clutter.append(f.name)
        if clutter:
            self._add_result(
                "WARNING",
                f"Potential clutter in root: {', '.join(clutter[:5])}",
                ".",
            )
        else:
            self._add_result("PASS", "Root directory is clean", ".")
        return self.results


class NamingConventionsCheck(BaseCheck):
    """Check naming conventions."""

    @property
    def check_id(self) -> str:
        return "struct_naming"

    @property
    def description(self) -> str:
        return "Files and directories follow naming conventions"

    @property
    def category(self) -> str:
        return "structure"

    def run(self) -> List[CheckResult]:
        self.results = []
        # Check for uppercase directories (should be lowercase)
        for d in self.repo_path.iterdir():
            if d.is_dir() and d.name.isupper() and d.name not in {"LICENSES", "DEPLOYMENT", "DOCS"}:
                self._add_result(
                    "WARNING",
                    f"Directory name is uppercase: {d.name}",
                    d.name,
                )
        # Check for spaces in filenames
        for f in self.repo_path.rglob("*"):
            if f.is_file() and " " in f.name:
                self._add_result(
                    "FAIL",
                    f"File name contains space: {f.relative_to(self.repo_path)}",
                    str(f.relative_to(self.repo_path)),
                )
        # Check for special characters
        for f in self.repo_path.rglob("*"):
            if f.is_file() and any(c in f.name for c in "!@#$%^&*()+=[]{}|;:'\"<>?"):
                self._add_result(
                    "WARNING",
                    f"File name contains special characters: {f.relative_to(self.repo_path)}",
                    str(f.relative_to(self.repo_path)),
                )
        if not any(r.status == "FAIL" for r in self.results):
            self._add_result("PASS", "Naming conventions generally followed", ".")
        return self.results
