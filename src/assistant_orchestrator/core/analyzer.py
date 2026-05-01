"""
Core analyzer class for Assistant Orchestrator.
"""

import logging
from datetime import datetime

from ..models.types import AnalysisResult
from .evidence_collector import EvidenceCollector

logger = logging.getLogger(__name__)


class AssistantOrchestrator:
    """Основной класс оркестратора"""

    def __init__(self, project_root: str = "."):
        self.project_root = project_root
        self.collector = EvidenceCollector(project_root)
        logger.info(f"Initialized AssistantOrchestrator for project root: {project_root}")

    def run_full_analysis(self) -> AnalysisResult:
        """Собирает все доказательства и возвращает результат"""
        logger.info("Starting full analysis...")

        try:
            microservices = self.collector.collect_microservices()
            logger.info(f"Collected microservices: {len(microservices.get('services', []))}")
        except Exception as e:
            logger.error(f"Failed to collect microservices: {e}")
            microservices = {"error": str(e), "services": []}

        try:
            skill_markers = self.collector.collect_skill_markers()
            logger.info(f"Collected skill markers: {skill_markers.get('total_count', 0)}")
        except Exception as e:
            logger.error(f"Failed to collect skill markers: {e}")
            skill_markers = {"error": str(e), "total_count": 0, "categories": []}

        try:
            architecture_docs = self.collector.collect_architecture_docs()
            logger.info(f"Found architecture docs: {len(architecture_docs)}")
        except Exception as e:
            logger.error(f"Failed to collect architecture docs: {e}")
            architecture_docs = []

        try:
            git_stats = self.collector.collect_git_stats()
            logger.info(f"Collected git stats: {git_stats.get('total_commits', 0)} commits")
        except Exception as e:
            logger.error(f"Failed to collect git stats: {e}")
            git_stats = {"error": str(e)}

        try:
            dependencies = self.collector.collect_dependencies()
            logger.info(f"Collected dependencies: {len(dependencies)} services")
        except Exception as e:
            logger.error(f"Failed to collect dependencies: {e}")
            dependencies = {}

        result = AnalysisResult(
            timestamp=self._get_timestamp(),
            microservices=microservices,
            skill_markers=skill_markers,
            architecture_docs=architecture_docs,
            git_stats=git_stats,
            dependencies=dependencies,
        )

        logger.info("Full analysis completed successfully")
        return result

    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        return datetime.now().isoformat()
