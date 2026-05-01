"""Monitoring and observability checks."""

from typing import List

from tools.repo_audit.checker import BaseCheck, CheckResult


class MonitoringCheck(BaseCheck):
    """Check for monitoring and observability configuration."""

    @property
    def check_id(self) -> str:
        return "monitoring_essential"

    @property
    def description(self) -> str:
        return "Monitoring and observability configured"

    @property
    def category(self) -> str:
        return "monitoring"

    def run(self) -> List[CheckResult]:
        self.results = []
        # 1. monitoring/ directory
        if self.check_directory_exists("monitoring"):
            self._add_result("PASS", "monitoring directory exists", "monitoring")
        else:
            self._add_result("WARNING", "monitoring directory missing", "monitoring")

        # 2. Prometheus configuration
        prometheus_files = list(self.repo_path.rglob("prometheus*.yml")) + list(
            self.repo_path.rglob("prometheus*.yaml")
        )
        if prometheus_files:
            self._add_result(
                "PASS",
                f"Prometheus configs found: {[f.name for f in prometheus_files[:3]]}",
                "monitoring/",
            )
        else:
            self._add_result("INFO", "Prometheus config missing", "monitoring/")

        # 3. Grafana dashboards
        grafana_files = list(self.repo_path.rglob("*dashboard*.json"))
        if grafana_files:
            self._add_result(
                "PASS",
                f"Grafana dashboards found: {len(grafana_files)}",
                "monitoring/",
            )
        else:
            self._add_result("INFO", "Grafana dashboards missing", "monitoring/")

        # 4. Alerting rules
        alert_files = list(self.repo_path.rglob("*alert*.yml")) + list(
            self.repo_path.rglob("*alert*.yaml")
        )
        if alert_files:
            self._add_result(
                "PASS",
                f"Alerting rules found: {[f.name for f in alert_files[:3]]}",
                "monitoring/",
            )
        else:
            self._add_result("INFO", "Alerting rules missing", "monitoring/")

        # 5. Logging configuration
        if self.check_file_exists("logging.conf") or self.check_file_exists("log_config.yaml"):
            self._add_result("PASS", "Logging config exists", "logging.conf")
        else:
            self._add_result("INFO", "Logging config missing", "logging.conf")

        # 6. Health check endpoints
        # Check for common health endpoints in code (simplified)
        health_files = list(self.repo_path.rglob("*health*.py")) + list(
            self.repo_path.rglob("*health*.yml")
        )
        if health_files:
            self._add_result(
                "PASS",
                f"Health check files found: {[f.name for f in health_files[:3]]}",
                "src/",
            )
        else:
            self._add_result("INFO", "Health check files missing", "src/")

        # 7. APM / Tracing (OpenTelemetry, Jaeger)
        if self.check_file_exists("opentelemetry.yaml") or self.check_file_exists(
            "jaeger-config.yaml"
        ):
            self._add_result("PASS", "APM/Tracing config exists", "monitoring/")
        else:
            self._add_result("INFO", "APM/Tracing config missing", "monitoring/")

        # 8. Metrics exposure (e.g., /metrics endpoint)
        # Check for prometheus_client in requirements
        if self.check_file_exists("requirements.txt"):
            content = (self.repo_path / "requirements.txt").read_text(
                encoding="utf-8", errors="ignore"
            )
            if "prometheus-client" in content.lower():
                self._add_result(
                    "PASS",
                    "prometheus-client in requirements",
                    "requirements.txt",
                )
            else:
                self._add_result(
                    "INFO",
                    "prometheus-client not in requirements",
                    "requirements.txt",
                )

        # 9. Docker Compose monitoring services
        docker_compose = self.repo_path / "docker-compose.yml"
        if docker_compose.exists():
            content = docker_compose.read_text(encoding="utf-8", errors="ignore")
            monitoring_services = ["prometheus", "grafana", "alertmanager", "loki"]
            found = [s for s in monitoring_services if s in content.lower()]
            if found:
                self._add_result(
                    "PASS",
                    f"Docker Compose includes monitoring services: {', '.join(found)}",
                    "docker-compose.yml",
                )
            else:
                self._add_result(
                    "INFO",
                    "Docker Compose lacks monitoring services",
                    "docker-compose.yml",
                )

        return self.results
