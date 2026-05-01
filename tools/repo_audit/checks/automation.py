"""Automation and scripting checks."""

from typing import List

from tools.repo_audit.checker import BaseCheck, CheckResult


class AutomationCheck(BaseCheck):
    """Check for automation scripts and tools."""

    @property
    def check_id(self) -> str:
        return "automation_essential"

    @property
    def description(self) -> str:
        return "Automation scripts and tools configured"

    @property
    def category(self) -> str:
        return "automation"

    def run(self) -> List[CheckResult]:
        self.results = []
        # 1. scripts/ directory
        if self.check_directory_exists("scripts"):
            self._add_result("PASS", "scripts directory exists", "scripts")
        else:
            self._add_result("WARNING", "scripts directory missing", "scripts")

        # 2. Makefile
        if self.check_file_exists("Makefile"):
            self._add_result("PASS", "Makefile exists", "Makefile")
        else:
            self._add_result("WARNING", "Makefile missing", "Makefile")

        # 3. Taskfile, Justfile, or similar
        if self.check_file_exists("Taskfile.yml") or self.check_file_exists("Justfile"):
            self._add_result("PASS", "Task runner exists", "Taskfile.yml")
        else:
            self._add_result("INFO", "Task runner missing (optional)", "Taskfile.yml")

        # 4. Pre-commit hooks
        if self.check_file_exists(".pre-commit-config.yaml"):
            self._add_result("PASS", "Pre‑commit config exists", ".pre-commit-config.yaml")
        else:
            self._add_result("WARNING", "Pre‑commit config missing", ".pre-commit-config.yaml")

        # 5. CI/CD automation (GitHub Actions, GitLab CI, etc.)
        workflows_dir = self.repo_path / ".github/workflows"
        if workflows_dir.is_dir():
            workflows = list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))
            if workflows:
                self._add_result(
                    "PASS",
                    f"CI/CD workflows found: {len(workflows)}",
                    ".github/workflows",
                )
            else:
                self._add_result("WARNING", "No CI/CD workflows", ".github/workflows")
        else:
            self._add_result("WARNING", "GitHub Actions directory missing", ".github/workflows")

        # 6. Docker automation
        if self.check_file_exists("docker-compose.yml"):
            self._add_result("PASS", "Docker Compose exists", "docker-compose.yml")
        else:
            self._add_result("INFO", "Docker Compose missing", "docker-compose.yml")

        # 7. Kubernetes automation (Helm, Kustomize)
        if self.check_directory_exists("deployment/k8s"):
            self._add_result("PASS", "Kubernetes manifests exist", "deployment/k8s")
        else:
            self._add_result("INFO", "Kubernetes manifests missing", "deployment/k8s")

        # 8. Infrastructure as Code (Terraform, Pulumi)
        terraform_files = list(self.repo_path.rglob("*.tf"))
        if terraform_files:
            self._add_result(
                "PASS",
                f"Terraform files found: {len(terraform_files)}",
                "infrastructure/",
            )
        else:
            self._add_result("INFO", "Terraform files missing", "infrastructure/")

        # 9. Scripts with shebang and executable bit (sample check)
        script_files = list(self.repo_path.rglob("scripts/*.sh")) + list(
            self.repo_path.rglob("scripts/*.py")
        )
        executable_count = 0
        for script in script_files[:10]:  # limit
            try:
                if script.is_file() and script.stat().st_mode & 0o111:
                    executable_count += 1
            except Exception:
                pass
        if executable_count > 0:
            self._add_result(
                "PASS",
                f"Executable scripts found: {executable_count}",
                "scripts/",
            )
        else:
            self._add_result("INFO", "No executable scripts detected", "scripts/")

        # 10. Automation documentation
        readme_path = self.repo_path / "README.md"
        if readme_path.exists():
            content = readme_path.read_text(encoding="utf-8", errors="ignore")
            automation_keywords = ["make", "script", "automate", "ci/cd", "docker"]
            found = [kw for kw in automation_keywords if kw in content.lower()]
            if found:
                self._add_result(
                    "PASS",
                    f"README mentions automation: {', '.join(found[:3])}",
                    "README.md",
                )
            else:
                self._add_result("INFO", "README does not mention automation", "README.md")

        return self.results
