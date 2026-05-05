"""Security checks."""

from typing import List

from tools.repo_audit.checker import BaseCheck, CheckResult


class SecurityCheck(BaseCheck):
    """Check for security best practices."""

    @property
    def check_id(self) -> str:
        return "sec_essential"

    @property
    def description(self) -> str:
        return "Essential security files and configurations"

    @property
    def category(self) -> str:
        return "security"

    def run(self) -> List[CheckResult]:
        self.results = []
        # 1. SECURITY.md
        self.check_file_exists("SECURITY.md")
        # 2. .gitignore (should exclude secrets)
        self.check_file_exists(".gitignore")
        # 3. .secrets.baseline (can be in root or config/tools/)
        if not self.check_file_exists(".secrets.baseline"):
            self.check_file_exists("config/tools/.secrets.baseline")
        # 4. .bandit.yml (can be in root or config/tools/)
        if not self.check_file_exists(".bandit.yml"):
            self.check_file_exists("config/tools/.bandit.yml")
        # 5. .trivyignore (can be in root or config/tools/)
        if not self.check_file_exists(".trivyignore"):
            self.check_file_exists("config/tools/.trivyignore")
        # 6. .pre-commit-config.yaml (can be in root or config/tools/)
        if not self.check_file_exists(".pre-commit-config.yaml"):
            self.check_file_exists("config/tools/.pre-commit-config.yaml")
        if self.check_file_exists(".pre-commit-config.yaml") or self.check_file_exists(
            "config/tools/.pre-commit-config.yaml"
        ):
            self.check_file_content(
                ".pre-commit-config.yaml",
                "detect-secrets",
                "Pre‑commit includes detect‑secrets",
            )
        # 7. deployment/secrets/ directory
        self.check_directory_exists("deployment/secrets")
        # 8. deployment/secrets/sealed-secrets/ (Kubernetes sealed secrets)
        if (self.repo_path / "deployment/secrets/sealed-secrets").is_dir():
            self._add_result(
                "PASS",
                "Sealed‑secrets directory exists",
                "deployment/secrets/sealed-secrets",
            )
        else:
            self._add_result(
                "WARNING",
                "Sealed‑secrets directory missing (optional)",
                "deployment/secrets/sealed-secrets",
            )
        # 9. No hardcoded secrets in .env files (sample check)
        env_example = self.repo_path / ".env.example"
        if env_example.exists():
            self._add_result("PASS", ".env.example exists", ".env.example")
        else:
            self._add_result("WARNING", ".env.example missing", ".env.example")
        # 10. Check for .env in .gitignore
        if self.check_file_content(".gitignore", ".env"):
            self._add_result("PASS", ".gitignore excludes .env", ".gitignore")
        else:
            self._add_result("FAIL", ".gitignore does not exclude .env", ".gitignore")
        return self.results


class DependencySecurityCheck(BaseCheck):
    """Check dependency security tools."""

    @property
    def check_id(self) -> str:
        return "sec_dependencies"

    @property
    def description(self) -> str:
        return "Dependency security scanning configured"

    @property
    def category(self) -> str:
        return "security"

    def run(self) -> List[CheckResult]:
        self.results = []
        # 1. pip-audit in requirements-dev.txt
        if self.check_file_exists("requirements-dev.txt"):
            if self.check_file_content("requirements-dev.txt", "pip-audit"):
                self._add_result("PASS", "pip‑audit in dev requirements", "requirements-dev.txt")
            else:
                self._add_result(
                    "WARNING",
                    "pip‑audit not in dev requirements",
                    "requirements-dev.txt",
                )
        # 2. bandit configuration (can be in root or config/tools/)
        if self.check_file_exists(".bandit.yml") or self.check_file_exists("config/tools/.bandit.yml"):
            self._add_result("PASS", "Bandit config exists", ".bandit.yml or config/tools/.bandit.yml")
        else:
            self._add_result("WARNING", "Bandit config missing", ".bandit.yml")
        # 3. trivy configuration (can be in root or config/tools/)
        if self.check_file_exists(".trivyignore") or self.check_file_exists("config/tools/.trivyignore"):
            self._add_result("PASS", "Trivy ignore file exists", ".trivyignore or config/tools/.trivyignore")
        else:
            self._add_result("WARNING", "Trivy ignore file missing", ".trivyignore")
        # 4. GitHub Actions security scanning
        workflows_dir = self.repo_path / ".github/workflows"
        if workflows_dir.is_dir():
            security_workflows = list(workflows_dir.glob("*security*.yml")) + list(
                workflows_dir.glob("*security*.yaml")
            )
            if security_workflows:
                self._add_result(
                    "PASS",
                    f"Security workflows found: {[w.name for w in security_workflows]}",
                    ".github/workflows",
                )
            else:
                self._add_result(
                    "WARNING",
                    "No dedicated security workflow",
                    ".github/workflows",
                )
        else:
            self._add_result(
                "FAIL",
                "GitHub Actions workflows directory missing",
                ".github/workflows",
            )
        return self.results
