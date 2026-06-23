"""
Core analyzer class for Assistant Orchestrator.
"""

import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from ..models.types import AnalysisResult
from .evidence_collector import EvidenceCollector, EvidenceCollectorError

logger = logging.getLogger(__name__)


class OrchestratorError(Exception):
    """Custom exception for orchestrator errors."""

    pass


@dataclass
class AnalysisMetrics:
    """Metrics for analysis run."""

    start_time: float = 0.0
    end_time: float = 0.0
    components: dict[str, float] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)

    @property
    def duration(self) -> float:
        """Total duration in seconds."""
        return self.end_time - self.start_time if self.end_time > 0 else 0.0

    def add_component_time(self, component: str, duration: float) -> None:
        """Add timing for a component."""
        self.components[component] = duration

    def add_error(self, error: str) -> None:
        """Add error message."""
        self.errors.append(error)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "duration": self.duration,
            "components": self.components,
            "errors": self.errors,
        }


class AssistantOrchestrator:
    """Основной класс оркестратора для анализа архитектуры проекта."""

    # Configuration defaults
    DEFAULT_CONFIG = {
        "parallel_collection": True,
        "max_workers": 4,
        "timeout": 60,
        "cache_results": False,
        "collect_metrics": True,
    }

    def __init__(self, project_root: str = ".", config: dict[str, Any] | None = None):
        """
        Initialize orchestrator.

        Args:
            project_root: Root directory of the project to analyze
            config: Configuration dictionary (overrides defaults)

        Raises:
            OrchestratorError: If initialization fails
        """
        self.project_root = project_root
        self.config = {**self.DEFAULT_CONFIG, **(config or {})}

        try:
            self.collector = EvidenceCollector(
                project_root,
                collect_parallel=self.config["parallel_collection"],
                max_workers=self.config["max_workers"],
                timeout=self.config["timeout"],
            )
        except EvidenceCollectorError as e:
            raise OrchestratorError(f"Failed to initialize evidence collector: {e}")

        self.metrics = AnalysisMetrics() if self.config["collect_metrics"] else None

        logger.info(f"Initialized AssistantOrchestrator for project root: {project_root}")
        logger.debug(f"Configuration: {self.config}")

    def run_full_analysis(self) -> AnalysisResult:
        """
        Собирает все доказательства и возвращает результат.

        Returns:
            AnalysisResult with all collected evidence

        Raises:
            OrchestratorError: If analysis fails critically
        """
        logger.info("Starting full analysis...")

        if self.metrics:
            self.metrics.start_time = time.time()

        # Collect all evidence with timing
        results = {}

        results = self._collect_parallel() if self.config["parallel_collection"] else self._collect_sequential()

        # Build result object
        try:
            result = self._build_analysis_result(results)

            if self.metrics:
                self.metrics.end_time = time.time()
                logger.info(f"Analysis completed in {self.metrics.duration:.2f} seconds")

                # Log component timings
                for component, duration in self.metrics.components.items():
                    logger.debug(f"  {component}: {duration:.2f}s")

                if self.metrics.errors:
                    logger.warning(f"Encountered {len(self.metrics.errors)} errors during analysis")

            return result

        except Exception as e:
            logger.error(f"Failed to build analysis result: {e}")
            raise OrchestratorError(f"Analysis failed: {e}")

    def _collect_parallel(self) -> dict[str, Any]:
        """Collect evidence in parallel."""
        results = {}

        with ThreadPoolExecutor(max_workers=self.config["max_workers"]) as executor:
            futures = {}

            # Submit all collection tasks
            collection_methods = {
                "microservices": self.collector.collect_microservices,
                "skill_markers": self.collector.collect_skill_markers,
                "architecture_docs": self.collector.collect_architecture_docs,
                "git_stats": self.collector.collect_git_stats,
                "dependencies": self.collector.collect_dependencies,
            }

            for name, method in collection_methods.items():
                future = executor.submit(self._collect_with_timing, name, method)
                futures[future] = name

            # Collect results
            for future in as_completed(futures, timeout=self.config["timeout"]):
                name = futures[future]
                try:
                    result = future.result(timeout=10)
                    results[name] = result
                except Exception as e:
                    logger.error(f"Failed to collect {name}: {e}")
                    results[name] = self._create_error_result(str(e))
                    if self.metrics:
                        self.metrics.add_error(f"{name}: {e}")

        return results

    def _collect_sequential(self) -> dict[str, Any]:
        """Collect evidence sequentially."""
        results = {}

        collection_methods = [
            ("microservices", self.collector.collect_microservices),
            ("skill_markers", self.collector.collect_skill_markers),
            ("architecture_docs", self.collector.collect_architecture_docs),
            ("git_stats", self.collector.collect_git_stats),
            ("dependencies", self.collector.collect_dependencies),
        ]

        for name, method in collection_methods:
            try:
                result = self._collect_with_timing(name, method)
                results[name] = result
            except Exception as e:
                logger.error(f"Failed to collect {name}: {e}")
                results[name] = self._create_error_result(str(e))
                if self.metrics:
                    self.metrics.add_error(f"{name}: {e}")

        return results

    def _collect_with_timing(self, name: str, method) -> dict[str, Any]:
        """Collect evidence with timing measurement."""
        start_time = time.time()

        try:
            result = method()
            duration = time.time() - start_time

            if self.metrics:
                self.metrics.add_component_time(name, duration)

            logger.debug(f"Collected {name} in {duration:.2f}s")
            return result

        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Error collecting {name} after {duration:.2f}s: {e}")
            raise

    def _create_error_result(self, error: str) -> dict[str, Any]:
        """Create error result dictionary."""
        return {"success": False, "error": error, "data": None}

    def _extract_data(self, result: dict[str, Any], default: Any = None) -> Any:
        """Extract data from collection result."""
        if isinstance(result, dict):
            if result.get("success", False):
                return result.get("data", default)
            else:
                logger.warning(f"Collection failed: {result.get('error', 'Unknown error')}")
                return default
        return result if result is not None else default

    def _build_analysis_result(self, collected: dict[str, Any]) -> AnalysisResult:
        """
        Build AnalysisResult from collected evidence.

        Args:
            collected: Dictionary of collected evidence

        Returns:
            AnalysisResult object
        """
        # Extract data with fallbacks
        microservices = self._extract_data(
            collected.get("microservices", {}), {"services": [], "error": "Collection failed"}
        )

        skill_markers = self._extract_data(
            collected.get("skill_markers", {}), {"total_count": 0, "categories": [], "markers": []}
        )

        architecture_docs = self._extract_data(collected.get("architecture_docs", {}), [])

        git_stats = self._extract_data(
            collected.get("git_stats", {}),
            {"total_commits": 0, "recent_activity_days": 0, "contributors": []},
        )

        dependencies = self._extract_data(collected.get("dependencies", {}), {"services": [], "dependencies": {}})

        # Ensure proper types
        if not isinstance(microservices, dict):
            microservices = {"services": [], "error": "Invalid data type"}

        if not isinstance(skill_markers, dict):
            skill_markers = {"total_count": 0, "categories": [], "error": "Invalid data type"}

        if not isinstance(architecture_docs, list):
            architecture_docs = []

        if not isinstance(git_stats, dict):
            git_stats = {
                "total_commits": 0,
                "recent_activity_days": 0,
                "error": "Invalid data type",
            }

        if not isinstance(dependencies, dict):
            dependencies = {"services": [], "error": "Invalid data type"}

        # Build result
        return AnalysisResult(
            timestamp=self._get_timestamp(),
            microservices=microservices,
            skill_markers=skill_markers,
            architecture_docs=architecture_docs,
            git_stats=git_stats,
            dependencies=dependencies,
        )

    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        return datetime.now().isoformat()

    def get_analysis_metrics(self) -> dict[str, Any] | None:
        """
        Get metrics from the last analysis run.

        Returns:
            Dictionary with metrics or None if metrics not collected
        """
        if self.metrics:
            return self.metrics.to_dict()
        return None

    @contextmanager
    def analysis_context(self):
        """
        Context manager for running analysis with automatic cleanup.

        Yields:
            AssistantOrchestrator instance

        Example:
            with orchestrator.analysis_context() as orch:
                result = orch.run_full_analysis()
        """
        try:
            logger.info("Entering analysis context")
            yield self
        except Exception as e:
            logger.error(f"Analysis context error: {e}")
            raise
        finally:
            logger.info("Exiting analysis context")
            self._cleanup()

    def _cleanup(self) -> None:
        """Cleanup resources after analysis."""
        logger.debug("Cleaning up orchestrator resources")
        # Add any cleanup logic here

    def run_quick_analysis(self) -> dict[str, Any]:
        """
        Run a quick analysis with minimal data collection.

        Returns:
            Dictionary with essential metrics only
        """
        logger.info("Running quick analysis...")

        try:
            # Only collect basic info
            microservices = self.collector.collect_microservices()
            git_stats = self.collector.collect_git_stats()

            services = microservices.get("data", {}).get("services", [])
            if not isinstance(services, list):
                services = []

            return {
                "timestamp": self._get_timestamp(),
                "services_count": len(services),
                "production_ready_count": sum(
                    1 for s in services if isinstance(s, dict) and s.get("is_production_ready", False)
                ),
                "total_commits": git_stats.get("data", {}).get("total_commits", 0),
                "recent_activity": git_stats.get("data", {}).get("recent_activity_days", 0),
            }
        except Exception as e:
            logger.error(f"Quick analysis failed: {e}")
            return {"error": str(e), "timestamp": self._get_timestamp()}

    def validate_project_structure(self) -> dict[str, bool]:
        """
        Validate project structure and required files.

        Returns:
            Dictionary with validation results
        """
        from pathlib import Path

        root = Path(self.project_root)

        return {
            "exists": root.exists(),
            "is_directory": root.is_dir(),
            "has_readme": (root / "README.md").exists(),
            "has_git": (root / ".git").exists(),
            "has_docker_compose": (root / "docker-compose.yml").exists() or (root / "docker-compose.yaml").exists(),
            "has_makefile": (root / "Makefile").exists(),
            "has_requirements": (root / "requirements.txt").exists() or (root / "pyproject.toml").exists(),
        }


# Convenience function
def analyze_project(project_root: str = ".", parallel: bool = True, quick: bool = False) -> AnalysisResult:
    """
    Quick project analysis function.

    Args:
        project_root: Root directory of the project
        parallel: Whether to collect evidence in parallel
        quick: Whether to run quick analysis (returns dict instead of AnalysisResult)

    Returns:
        AnalysisResult or dict for quick analysis

    Raises:
        OrchestratorError: If analysis fails
    """
    config = {"parallel_collection": parallel} if parallel else {}
    orchestrator = AssistantOrchestrator(project_root, config)

    if quick:
        return orchestrator.run_quick_analysis()
    else:
        return orchestrator.run_full_analysis()
