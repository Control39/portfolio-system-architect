"""
Evidence collector for gathering project evidence.
"""

import importlib
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class EvidenceCollectorError(Exception):
    """Custom exception for evidence collection errors."""

    pass


@dataclass
class CollectionResult:
    """Result of evidence collection."""

    success: bool
    data: Any = None
    error: str | None = None
    duration: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        result = {"success": self.success}
        if self.data is not None:
            result["data"] = self.data
        if self.error:
            result["error"] = self.error
        result["duration"] = self.duration
        return result


class EvidenceCollector:
    """Collects evidence from various sources in the project."""

    # Plugin configuration
    PLUGINS = {
        "microservices": {
            "module": "..plugins.microservices",
            "function": "analyze",
            "timeout": 30,
        },
        "skills": {
            "module": "..plugins.skills",
            "function": "analyze",
            "timeout": 30,
        },
        "docs": {
            "module": "..plugins.docs",
            "function": "find_docs",
            "timeout": 10,
        },
        "git": {
            "module": "..plugins.git_history",
            "function": "get_stats",
            "timeout": 30,
        },
    }

    def __init__(
        self,
        project_root: str,
        collect_parallel: bool = True,
        max_workers: int = 4,
        timeout: int = 60,
    ):
        """
        Initialize evidence collector.

        Args:
            project_root: Root directory of the project
            collect_parallel: Whether to collect evidence in parallel
            max_workers: Maximum number of parallel workers
            timeout: Global timeout for all collections

        Raises:
            EvidenceCollectorError: If project_root is invalid
        """
        root_path = Path(project_root)
        if not root_path.exists():
            raise EvidenceCollectorError(f"Project root does not exist: {project_root}")

        if not root_path.is_dir():
            raise EvidenceCollectorError(f"Project root is not a directory: {project_root}")

        self.root = root_path.resolve()
        self.collect_parallel = collect_parallel
        self.max_workers = max_workers
        self.timeout = timeout

        logger.info(f"EvidenceCollector initialized: {self.root}")
        logger.debug(f"Parallel collection: {collect_parallel}, workers: {max_workers}")

    def collect_all(self) -> dict[str, Any]:
        """
        Collect all evidence using parallel execution.

        Returns:
            Dictionary with all collected evidence
        """
        if self.collect_parallel:
            return self._collect_all_parallel()
        else:
            return self._collect_all_sequential()

    def _collect_all_parallel(self) -> dict[str, Any]:
        """Collect all evidence in parallel."""
        results = {}

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_method = {
                executor.submit(self._collect_single, method): method
                for method in [
                    "microservices",
                    "skills",
                    "architecture_docs",
                    "git_stats",
                    "dependencies",
                ]
            }

            for future in as_completed(future_to_method, timeout=self.timeout):
                method = future_to_method[future]
                try:
                    result = future.result(timeout=10)
                    results[method] = result
                    logger.debug(f"Collected {method}: success={result.get('success', False)}")
                except Exception as e:
                    logger.error(f"Failed to collect {method}: {e}")
                    results[method] = self._create_error_result(str(e))

        return results

    def _collect_all_sequential(self) -> dict[str, Any]:
        """Collect all evidence sequentially."""
        results = {}

        methods = [
            ("microservices", self.collect_microservices),
            ("skills", self.collect_skill_markers),
            ("architecture_docs", self.collect_architecture_docs),
            ("git_stats", self.collect_git_stats),
            ("dependencies", self.collect_dependencies),
        ]

        for name, method in methods:
            try:
                result = method()
                results[name] = self._ensure_result_format(result)
                logger.debug(f"Collected {name}: success={results[name].get('success', False)}")
            except Exception as e:
                logger.error(f"Failed to collect {name}: {e}")
                results[name] = self._create_error_result(str(e))

        return results

    def _collect_single(self, method: str) -> dict[str, Any]:
        """Collect single evidence type."""
        if method == "microservices":
            return self.collect_microservices()
        elif method == "skills":
            return self.collect_skill_markers()
        elif method == "architecture_docs":
            return self.collect_architecture_docs()
        elif method == "git_stats":
            return self.collect_git_stats()
        elif method == "dependencies":
            return self.collect_dependencies()
        else:
            return self._create_error_result(f"Unknown method: {method}")

    def _ensure_result_format(self, result: Any) -> dict[str, Any]:
        """Ensure result is in proper format."""
        if isinstance(result, dict) and "success" in result:
            return result
        return {"success": True, "data": result}

    def _create_error_result(self, error: str) -> dict[str, Any]:
        """Create error result dictionary."""
        return {"success": False, "error": error, "data": None}

    def collect_microservices(self) -> dict[str, Any]:
        """
        Collect microservices information.

        Returns:
            Dictionary with microservices data or error info
        """
        try:
            result = self._load_and_execute_plugin("microservices")

            # Validate result structure
            if isinstance(result, dict):
                if "services" not in result:
                    result["services"] = []
                return {"success": True, "data": result}
            elif isinstance(result, list):
                return {"success": True, "data": {"services": result}}
            else:
                return {"success": True, "data": {"services": []}}

        except EvidenceCollectorError as e:
            logger.error(f"Microservices collection failed: {e}")
            return self._create_error_result(str(e))
        except Exception as e:
            logger.error(f"Unexpected error in microservices collection: {e}")
            return self._create_error_result(f"Unexpected error: {e}")

    def collect_skill_markers(self) -> dict[str, Any]:
        """
        Collect skill markers from IT-Compass.

        Returns:
            Dictionary with skill markers data or error info
        """
        try:
            result = self._load_and_execute_plugin("skills")

            # Default structure
            default_result = {"total_count": 0, "categories": [], "markers": []}

            if isinstance(result, dict):
                # Merge with defaults
                return {
                    "success": True,
                    "data": {
                        "total_count": result.get("total_count", 0),
                        "categories": result.get("categories", []),
                        "markers": result.get("markers", []),
                    },
                }
            else:
                return {"success": True, "data": default_result}

        except EvidenceCollectorError as e:
            logger.error(f"Skills collection failed: {e}")
            return self._create_error_result(str(e))
        except Exception as e:
            logger.error(f"Unexpected error in skills collection: {e}")
            return self._create_error_result(f"Unexpected error: {e}")

    def collect_architecture_docs(self) -> dict[str, Any]:
        """
        Collect architecture documentation files.

        Returns:
            Dictionary with list of documentation files or error info
        """
        try:
            result = self._load_and_execute_plugin("docs")

            if isinstance(result, list):
                # Filter and validate paths
                valid_docs = []
                for doc in result:
                    doc_path = Path(doc)
                    if doc_path.exists():
                        valid_docs.append(str(doc_path))
                return {"success": True, "data": valid_docs}
            else:
                return {"success": True, "data": []}

        except EvidenceCollectorError as e:
            logger.error(f"Documentation collection failed: {e}")
            return self._create_error_result(str(e))
        except Exception as e:
            logger.error(f"Unexpected error in documentation collection: {e}")
            return self._create_error_result(f"Unexpected error: {e}")

    def collect_git_stats(self) -> dict[str, Any]:
        """
        Collect Git repository statistics.

        Returns:
            Dictionary with git statistics or error info
        """
        try:
            result = self._load_and_execute_plugin("git")

            default_stats = {
                "total_commits": 0,
                "recent_activity_days": 0,
                "contributors": [],
                "branches": [],
                "last_commit_date": None,
            }

            if isinstance(result, dict):
                return {
                    "success": True,
                    "data": {
                        "total_commits": result.get("total_commits", 0),
                        "recent_activity_days": result.get("recent_activity_days", 0),
                        "contributors": result.get("contributors", []),
                        "branches": result.get("branches", []),
                        "last_commit_date": result.get("last_commit_date"),
                    },
                }
            else:
                return {"success": True, "data": default_stats}

        except EvidenceCollectorError as e:
            logger.error(f"Git statistics collection failed: {e}")
            return self._create_error_result(str(e))
        except Exception as e:
            logger.error(f"Unexpected error in git statistics collection: {e}")
            return self._create_error_result(f"Unexpected error: {e}")

    def collect_dependencies(self) -> dict[str, Any]:
        """
        Collect dependencies from Docker Compose, requirements, etc.

        Returns:
            Dictionary with dependencies data or error info
        """
        try:
            result = self._load_and_execute_helper("parse_docker_compose")

            default_deps = {
                "services": [],
                "dependencies": {},
                "docker_compose_exists": False,
                "kubernetes_exists": False,
            }

            if isinstance(result, dict):
                return {
                    "success": True,
                    "data": {
                        "services": result.get("services", []),
                        "dependencies": result.get("dependencies", {}),
                        "docker_compose_exists": result.get("docker_compose_exists", False),
                        "kubernetes_exists": self._check_kubernetes_exists(),
                    },
                }
            else:
                return {
                    "success": True,
                    "data": {**default_deps, "kubernetes_exists": self._check_kubernetes_exists()},
                }

        except EvidenceCollectorError as e:
            logger.error(f"Dependencies collection failed: {e}")
            return self._create_error_result(str(e))
        except Exception as e:
            logger.error(f"Unexpected error in dependencies collection: {e}")
            return self._create_error_result(f"Unexpected error: {e}")

    def _load_and_execute_plugin(self, plugin_name: str) -> Any:
        """
        Load plugin module and execute its main function.

        Args:
            plugin_name: Name of the plugin (key in PLUGINS dict)

        Returns:
            Result of plugin execution

        Raises:
            EvidenceCollectorError: If plugin cannot be loaded or executed
        """
        if plugin_name not in self.PLUGINS:
            raise EvidenceCollectorError(f"Unknown plugin: {plugin_name}")

        plugin_config = self.PLUGINS[plugin_name]

        try:
            module = importlib.import_module(plugin_config["module"], package=__package__)
            func_name = plugin_config["function"]

            if not hasattr(module, func_name):
                raise EvidenceCollectorError(f"Plugin {plugin_name} has no function {func_name}")

            func = getattr(module, func_name)
            result = func(self.root)

            return result

        except ImportError as e:
            logger.warning(f"Plugin {plugin_name} not available: {e}")
            raise EvidenceCollectorError(f"Plugin not installed: {plugin_name}")
        except Exception as e:
            logger.error(f"Error executing plugin {plugin_name}: {e}")
            raise EvidenceCollectorError(f"Plugin execution failed: {e}")

    def _load_and_execute_helper(self, helper_name: str) -> Any:
        """
        Load helper function and execute.

        Args:
            helper_name: Name of the helper function

        Returns:
            Result of helper execution

        Raises:
            EvidenceCollectorError: If helper cannot be loaded or executed
        """
        try:
            from ..utils import helpers

            if not hasattr(helpers, helper_name):
                raise EvidenceCollectorError(f"Helper function not found: {helper_name}")

            func = getattr(helpers, helper_name)
            result = func(self.root)
            return result

        except ImportError as e:
            logger.warning(f"Helpers module not available: {e}")
            raise EvidenceCollectorError(f"Helpers module not available: {e}")
        except Exception as e:
            logger.error(f"Error executing helper {helper_name}: {e}")
            raise EvidenceCollectorError(f"Helper execution failed: {e}")

    def _check_kubernetes_exists(self) -> bool:
        """Check if Kubernetes manifests exist in the project."""
        k8s_paths = [
            self.root / "k8s",
            self.root / "kubernetes",
            self.root / "deploy" / "k8s",
            self.root / "manifests",
        ]

        for path in k8s_paths:
            if path.exists() and path.is_dir():
                # Check for yaml/yml files
                if any(path.glob("*.yaml")) or any(path.glob("*.yml")):
                    return True

        return False

    def get_project_info(self) -> dict[str, Any]:
        """
        Get basic project information.

        Returns:
            Dictionary with project metadata
        """
        return {
            "root": str(self.root),
            "name": self.root.name,
            "exists": self.root.exists(),
            "is_git_repo": (self.root / ".git").exists(),
            "has_docker": self._check_kubernetes_exists(),  # Reuse for docker check
        }

    @lru_cache(maxsize=1)
    def collect_all_cached(self) -> dict[str, Any]:
        """
        Collect all evidence with caching.

        Returns:
            Cached dictionary with all collected evidence
        """
        logger.info("Collecting all evidence (cached)")
        return self.collect_all()


# Convenience function
def collect_evidence(project_root: str, parallel: bool = True, cache: bool = False) -> dict[str, Any]:
    """
    Quick evidence collection.

    Args:
        project_root: Root directory of the project
        parallel: Whether to collect in parallel
        cache: Whether to cache results

    Returns:
        Dictionary with all collected evidence
    """
    collector = EvidenceCollector(project_root, collect_parallel=parallel)

    if cache:
        return collector.collect_all_cached()
    else:
        return collector.collect_all()
