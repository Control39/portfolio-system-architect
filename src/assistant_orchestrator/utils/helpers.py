"""Helper functions for Assistant Orchestrator.
"""
import json
import logging
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)


def parse_docker_compose(root: Path) -> dict[str, list[str]]:
    """Parse Docker Compose file to extract services and dependencies."""
    compose_files = [
        root / "docker-compose.yml",
        root / "docker-compose.yaml",
        root / "docker" / "docker-compose.yml",
    ]

    for compose_file in compose_files:
        if compose_file.exists():
            try:
                with open(compose_file, encoding="utf-8") as f:
                    content = f.read()

                # Simple YAML parsing
                data = yaml.safe_load(content)
                services = data.get("services", {})

                result = {}
                for service_name, service_config in services.items():
                    dependencies = []
                    # Check for depends_on
                    if "depends_on" in service_config:
                        deps = service_config["depends_on"]
                        if isinstance(deps, list):
                            dependencies.extend(deps)
                        elif isinstance(deps, dict):
                            dependencies.extend(deps.keys())

                    # Check for links
                    if "links" in service_config:
                        links = service_config["links"]
                        if isinstance(links, list):
                            dependencies.extend(links)

                    result[service_name] = dependencies

                logger.info(f"Parsed Docker Compose: {len(result)} services")
                return result
            except Exception as e:
                logger.error(f"Failed to parse {compose_file}: {e}")
                continue

    # Fallback: scan for Dockerfiles
    return _scan_for_dockerfiles(root)


def _scan_for_dockerfiles(root: Path) -> dict[str, list[str]]:
    """Scan for Dockerfiles as fallback."""
    dockerfiles = list(root.glob("**/Dockerfile"))
    services = {}

    for dockerfile in dockerfiles:
        service_name = dockerfile.parent.name
        services[service_name] = []

    logger.info(f"Found {len(services)} Dockerfiles")
    return services


def safe_read_json(path: Path) -> dict[str, Any] | None:
    """Safely read JSON file, return None on error."""
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.debug(f"Failed to read JSON {path}: {e}")
        return None


def find_files_with_pattern(root: Path, pattern: str) -> list[Path]:
    """Find files matching pattern recursively."""
    try:
        return list(root.glob(pattern))
    except Exception as e:
        logger.debug(f"Error searching for pattern {pattern}: {e}")
        return []


def calculate_maturity_score(analysis: dict[str, Any]) -> int:
    """Calculate a simple maturity score (0-5)."""
    score = 0

    # Microservices
    services = analysis.get("microservices", {}).get("services", [])
    if len(services) >= 3:
        score += 1
    if any(s.get("is_production_ready") for s in services):
        score += 1

    # Skills
    skill_count = analysis.get("skill_markers", {}).get("total_count", 0)
    if skill_count > 20:
        score += 1

    # Documentation
    doc_count = len(analysis.get("architecture_docs", []))
    if doc_count > 0:
        score += 1

    # Git activity
    git_commits = analysis.get("git_stats", {}).get("total_commits", 0)
    if git_commits > 100:
        score += 1

    return min(score, 5)

