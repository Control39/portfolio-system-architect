"""
Microservices plugin for analyzing microservices architecture.
"""

import logging
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)


def analyze(root: Path) -> Dict[str, Any]:
    """Analyze microservices in the project."""
    services = []

    # Look for Docker Compose files
    docker_compose_paths = [
        root / "docker-compose.yml",
        root / "docker-compose.yaml",
        root / "docker" / "docker-compose.yml",
    ]

    has_docker_compose = any(p.exists() for p in docker_compose_paths)

    # Look for Kubernetes manifests
    k8s_dirs = [
        root / "k8s",
        root / "kubernetes",
        root / "deployment" / "k8s",
    ]

    has_kubernetes = any(d.exists() and any(d.iterdir()) for d in k8s_dirs)

    # Scan apps directory for potential microservices
    apps_dir = root / "apps"
    if apps_dir.exists():
        for app in apps_dir.iterdir():
            if app.is_dir():
                # Check if it looks like a service
                has_docker = (app / "Dockerfile").exists()
                has_requirements = (app / "requirements.txt").exists() or (
                    app / "pyproject.toml"
                ).exists()
                has_tests = (app / "tests").exists() or (app / "test").exists()

                if has_docker or has_requirements:
                    services.append(
                        {
                            "name": app.name,
                            "path": str(app.relative_to(root)),
                            "is_production_ready": has_docker and has_tests,
                            "has_tests": has_tests,
                            "has_docker": has_docker,
                            "has_kubernetes": has_kubernetes and (app / "k8s").exists(),
                            "language": _detect_language(app),
                        }
                    )

    logger.info(f"Found {len(services)} potential microservices")

    return {
        "services": services,
        "has_docker_compose": has_docker_compose,
        "has_kubernetes": has_kubernetes,
        "total_count": len(services),
    }


def _detect_language(path: Path) -> str:
    """Detect primary programming language of a service."""
    if (path / "requirements.txt").exists() or (path / "pyproject.toml").exists():
        return "Python"
    elif (path / "package.json").exists():
        return "JavaScript/TypeScript"
    elif (path / "go.mod").exists():
        return "Go"
    elif (path / "Cargo.toml").exists():
        return "Rust"
    elif (path / "pom.xml").exists() or (path / "build.gradle").exists():
        return "Java"
    else:
        return "unknown"
