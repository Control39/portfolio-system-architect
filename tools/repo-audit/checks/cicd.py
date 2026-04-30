"""CI/CD checks."""

from typing import List

from tools.repo_audit.checker import BaseCheck, CheckResult


class CICDCheck(BaseCheck):
    """Check for CI/CD configuration."""

    @property
    def check_id(self) -> str:
        return "cicd_essential"

    @property
    def description(self) -> str:
        return "CI/CD pipelines configured"

    @property
    def category(self) -> str:
        return "cicd"

    def run(self) -> List[CheckResult]:
        self.results = []
        # GitHub Actions
        workflows_dir = self.repo_path / ".github/workflows"
        if workflows_dir.is_dir():
            workflows = list(workflows_dir.glob("*.yml")) + list(
                workflows_dir.glob("*.yaml")
            )
            if workflows:
                self._add_result(
                    "PASS",
                    f"GitHub Actions workflows found: {len(workflows)}",
                    ".github/workflows",
                )
                # Check for essential workflows
                essential = ["ci", "test", "security", "deploy"]
                found = []
                for w in workflows:
                    name = w.stem.lower()
                    for e in essential:
                        if e in name:
                            found.append(e)
                for e in essential:
                    if e in found:
                        self._add_result(
                            "PASS", f"Workflow '{e}' present", ".github/workflows"
                        )
                    else:
                        self._add_result(
                            "WARNING", f"Workflow '{e}' missing", ".github/workflows"
                        )
            else:
                self._add_result(
                    "FAIL", "No GitHub Actions workflows", ".github/workflows"
                )
        else:
            self._add_result(
                "FAIL", "GitHub Actions directory missing", ".github/workflows"
            )

        # Docker
        if self.check_file_exists("docker-compose.yml"):
            self._add_result("PASS", "Docker Compose file exists", "docker-compose.yml")
        else:
            self._add_result(
                "WARNING", "Docker Compose file missing", "docker-compose.yml"
            )

        # Kubernetes
        if self.check_directory_exists("deployment/k8s"):
            self._add_result("PASS", "Kubernetes manifests exist", "deployment/k8s")
        else:
            self._add_result(
                "WARNING", "Kubernetes manifests missing", "deployment/k8s"
            )

        # Makefile
        if self.check_file_exists("Makefile"):
            self._add_result("PASS", "Makefile exists", "Makefile")
        else:
            self._add_result("WARNING", "Makefile missing", "Makefile")

        # Pre-commit
        if self.check_file_exists(".pre-commit-config.yaml"):
            self._add_result(
                "PASS", "Pre‑commit config exists", ".pre-commit-config.yaml"
            )
        else:
            self._add_result(
                "WARNING", "Pre‑commit config missing", ".pre-commit-config.yaml"
            )

        return self.results
