"""
Evidence collector for gathering project evidence.
"""
import logging
from pathlib import Path
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class EvidenceCollector:
    """Collects evidence from various sources in the project."""
    
    def __init__(self, project_root: str):
        self.root = Path(project_root).resolve()
        logger.debug(f"EvidenceCollector root: {self.root}")
    
    def collect_microservices(self) -> Dict[str, Any]:
        """Collect microservices information."""
        try:
            # Try to import plugin
            from ..plugins import microservices
            return microservices.analyze(self.root)
        except ImportError as e:
            logger.warning(f"Microservices plugin not available: {e}")
            return {"services": [], "error": "Plugin not implemented"}
        except Exception as e:
            logger.error(f"Error collecting microservices: {e}")
            return {"services": [], "error": str(e)}
    
    def collect_skill_markers(self) -> Dict[str, Any]:
        """Collect skill markers from IT-Compass."""
        try:
            from ..plugins import skills
            return skills.analyze(self.root)
        except ImportError as e:
            logger.warning(f"Skills plugin not available: {e}")
            return {"total_count": 0, "categories": [], "markers": []}
        except Exception as e:
            logger.error(f"Error collecting skill markers: {e}")
            return {"total_count": 0, "categories": [], "error": str(e)}
    
    def collect_architecture_docs(self) -> List[str]:
        """Collect architecture documentation files."""
        try:
            from ..plugins import docs
            return docs.find_docs(self.root)
        except ImportError as e:
            logger.warning(f"Docs plugin not available: {e}")
            return []
        except Exception as e:
            logger.error(f"Error collecting architecture docs: {e}")
            return []
    
    def collect_git_stats(self) -> Dict[str, Any]:
        """Collect Git repository statistics."""
        try:
            from ..plugins import git_history
            return git_history.get_stats(self.root)
        except ImportError as e:
            logger.warning(f"Git history plugin not available: {e}")
            return {"total_commits": 0, "recent_activity_days": 0, "contributors": []}
        except Exception as e:
            logger.error(f"Error collecting git stats: {e}")
            return {"error": str(e)}
    
    def collect_dependencies(self) -> Dict[str, List[str]]:
        """Collect dependencies from Docker Compose, requirements, etc."""
        try:
            from ..utils.helpers import parse_docker_compose
            return parse_docker_compose(self.root)
        except ImportError as e:
            logger.warning(f"Helpers module not available: {e}")
            return {}
        except Exception as e:
            logger.error(f"Error collecting dependencies: {e}")
            return {}
