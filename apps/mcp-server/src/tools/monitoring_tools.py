#!/usr/bin/env python3
"""
Monitoring Tools для MCP Server

Инструменты для работы с Prometheus, Grafana и мониторингом проекта.
"""

import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List

from fastmcp import FastMCP


def init_monitoring_tools(mcp_server: FastMCP, project_root: Path) -> None:
    """Инициализация инструментов мониторинга"""

    monitoring_path = project_root / "monitoring"
    prometheus_path = monitoring_path / "prometheus"
    grafana_path = monitoring_path / "grafana"

    @mcp.tool()
    def get_prometheus_targets() -> List[Dict[str, Any]]:
        """
        Получение списка target'ов Prometheus

        Возвращает:
            Список target'ов со статусом
        """
        try:
            import requests

            response = requests.get("http://localhost:9090/api/v1/targets", timeout=5)

            if response.status_code == 200:
                data = response.json()
                targets = []

                for target in data.get("data", {}).get("activeTargets", []):
                    targets.append(
                        {
                            "job": target.get("labels", {}).get("job", "unknown"),
                            "instance": target.get("labels", {}).get("instance", "unknown"),
                            "health": target.get("health", "unknown"),
                            "last_scrape": target.get("lastScrape", ""),
                            "last_error": target.get("lastError", ""),
                        }
                    )

                return targets
            else:
                return [{"error": f"Prometheus API error: {response.status_code}"}]

        except ImportError:
            return [{"error": "requests library not installed"}]
        except Exception as e:
            return [{"error": f"Prometheus not available: {str(e)}"}]

    @mcp.tool()
    def get_prometheus_metrics(query: str = "up") -> List[Dict[str, Any]]:
        """
        Запрос метрик Prometheus

        Аргументы:
            query: PromQL запрос (по умолчанию "up")

        Возвращает:
            Результаты запроса
        """
        try:
            import requests

            response = requests.get(
                "http://localhost:9090/api/v1/query", params={"query": query}, timeout=5
            )

            if response.status_code == 200:
                data = response.json()
                results = data.get("data", {}).get("result", [])

                formatted = []
                for result in results:
                    formatted.append(
                        {
                            "metric": result.get("metric", {}),
                            "value": result.get("value", [None, None]),
                        }
                    )

                return formatted
            else:
                return [{"error": f"Prometheus API error: {response.status_code}"}]

        except Exception as e:
            return [{"error": f"Prometheus query failed: {str(e)}"}]

    @mcp.tool()
    def get_grafana_dashboards() -> List[Dict[str, Any]]:
        """
        Получение списка дашбордов Grafana

        Возвращает:
            Список дашбордов
        """
        try:
            import requests

            response = requests.get(
                "http://localhost:3000/api/search?type=dash-db",
                auth=("admin", "admin"),  # Default credentials, should be configured
                timeout=5,
            )

            if response.status_code == 200:
                dashboards = response.json()
                return [
                    {
                        "title": db.get("title", "unknown"),
                        "uid": db.get("uid", "unknown"),
                        "url": db.get("url", ""),
                        "folder": db.get("folderTitle", "General"),
                    }
                    for db in dashboards
                ]
            else:
                return [{"error": f"Grafana API error: {response.status_code}"}]

        except Exception as e:
            return [{"error": f"Grafana not available: {str(e)}"}]

    @mcp.tool()
    def check_monitoring_stack_status() -> Dict[str, Any]:
        """
        Проверка статуса стека мониторинга

        Возвращает:
            Статус компонентов (Prometheus, Grafana, Alertmanager)
        """
        services = {
            "prometheus": "http://localhost:9090/-/healthy",
            "grafana": "http://localhost:3000/api/health",
            "alertmanager": "http://localhost:9093/-/healthy",
        }

        status = {}

        try:
            import requests

            for service, url in services.items():
                try:
                    response = requests.get(url, timeout=3)
                    status[service] = {
                        "status": "up" if response.status_code == 200 else "down",
                        "status_code": response.status_code,
                    }
                except Exception as e:
                    status[service] = {"status": "down", "error": str(e)}

            return status

        except ImportError:
            return {"error": "requests library not installed"}
        except Exception as e:
            return {"error": f"Status check failed: {str(e)}"}

    @mcp.tool()
    def get_docker_container_stats() -> List[Dict[str, Any]]:
        """
        Получение статистики Docker контейнеров

        Возвращает:
            Статистика по контейнерам (CPU, memory, etc.)
        """
        try:
            result = subprocess.run(
                ["docker", "stats", "--no-stream", "--format", "{{json .}}"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                containers = []
                for line in result.stdout.strip().split("\n"):
                    if line:
                        try:
                            container = json.loads(line)
                            containers.append(
                                {
                                    "name": container.get("Name", "unknown"),
                                    "cpu_percent": container.get("CPUPerc", "0%"),
                                    "memory_usage": container.get("MemUsage", "0B"),
                                    "memory_percent": container.get("MemPerc", "0%"),
                                    "net_io": container.get("NetIO", "0B"),
                                    "block_io": container.get("BlockIO", "0B"),
                                }
                            )
                        except json.JSONDecodeError:
                            continue

                return containers
            else:
                return [{"error": f"Docker stats failed: {result.stderr}"}]

        except FileNotFoundError:
            return [{"error": "Docker not installed or not in PATH"}]
        except Exception as e:
            return [{"error": f"Docker stats failed: {str(e)}"}]

    @mcp.tool()
    def get_monitoring_config() -> Dict[str, Any]:
        """
        Получение конфигурации мониторинга

        Возвращает:
            Конфигурация Prometheus и Grafana
        """
        config = {"prometheus": {}, "grafana": {}, "alertmanager": {}}

        # Prometheus config
        prometheus_yml = prometheus_path / "prometheus.yml"
        if prometheus_yml.exists():
            try:
                import yaml

                with open(prometheus_yml, "r") as f:
                    config["prometheus"] = yaml.safe_load(f)
            except Exception as e:
                config["prometheus"] = {"error": str(e)}

        # Grafana datasources
        grafana_datasources = grafana_path / "provisioning" / "datasources"
        if grafana_datasources.exists():
            datasources = []
            for file in grafana_datasources.glob("*.yml"):
                try:
                    import yaml

                    with open(file, "r") as f:
                        datasources.append(yaml.safe_load(f))
                except:
                    pass
            config["grafana"]["datasources"] = datasources

        return config
