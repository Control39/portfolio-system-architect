"""
RAG Advisor plugin for Assistant Orchestrator.
Provides intelligent search and recommendations based on project documentation.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

# Try to import embedding_agent, but make it optional
try:
    from src.embedding_agent.search import DocumentSearcher

    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False
    DocumentSearcher = None

logger = logging.getLogger(__name__)


class RAGAdvisor:
    """RAG-based advisor for project documentation."""

    def __init__(self, project_root: Path):
        self.root = project_root
        self.searcher: Optional[DocumentSearcher] = None
        self.index_path = project_root / ".cache" / "rag_index.pkl"

        if RAG_AVAILABLE:
            self._initialize_searcher()
        else:
            logger.warning(
                "RAG dependencies not available. Install sentence-transformers and chromadb."
            )

    def _initialize_searcher(self):
        """Initialize the document searcher."""
        try:
            # Create cache directory
            self.index_path.parent.mkdir(parents=True, exist_ok=True)

            # Try to load existing index
            if self.index_path.exists():
                self.searcher = DocumentSearcher(str(self.index_path))
                logger.info(f"Loaded RAG index from {self.index_path}")
            else:
                self.searcher = DocumentSearcher()
                logger.info(
                    "Created new RAG searcher (index will be built on first use)"
                )
        except Exception as e:
            logger.error(f"Failed to initialize RAG searcher: {e}")
            self.searcher = None

    def build_index(self, force_rebuild: bool = False) -> Dict[str, Any]:
        """
        Build or rebuild the document index.

        Args:
            force_rebuild: If True, rebuild index even if it exists.

        Returns:
            Statistics about the built index.
        """
        if not RAG_AVAILABLE or not self.searcher:
            return {"error": "RAG dependencies not available"}

        if not force_rebuild and self.index_path.exists():
            logger.info("Index already exists, skipping rebuild")
            return {"status": "already_exists", "path": str(self.index_path)}

        try:
            # Build index from markdown files
            stats = self.searcher.build_index(
                file_pattern="**/*.md", root_dir=str(self.root)
            )

            # Save index
            save_path = self.searcher.save_index(str(self.index_path))

            stats["status"] = "built"
            stats["path"] = save_path
            logger.info(f"RAG index built: {stats}")
            return stats

        except Exception as e:
            logger.error(f"Failed to build RAG index: {e}")
            return {"error": str(e), "status": "failed"}

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search project documentation.

        Args:
            query: Search query.
            top_k: Number of results to return.

        Returns:
            List of search results with metadata.
        """
        if not RAG_AVAILABLE or not self.searcher:
            return [{"error": "RAG dependencies not available"}]

        if self.searcher.get_document_count() == 0:
            # Auto-build index if empty
            self.build_index()

        try:
            results = self.searcher.search(query, top_k)

            # Format results for the orchestrator
            formatted_results = []
            for result in results:
                formatted = {
                    "score": result.get("score", 0.0),
                    "text": result.get("text", "")[:500],  # Truncate
                    "source": result.get("metadata", {}).get("source", "unknown"),
                    "chunk": result.get("metadata", {}).get("chunk", 0),
                    "total_chunks": result.get("metadata", {}).get("total_chunks", 1),
                }
                formatted_results.append(formatted)

            return formatted_results

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return [{"error": str(e)}]

    def get_advice(self, topic: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Get AI-powered advice on a specific topic.

        Args:
            topic: The topic to get advice about (e.g., "microservices", "testing").
            context: Optional context to refine the search.

        Returns:
            Advice with relevant documentation references.
        """
        # Build search query
        query = f"{topic} {context or ''}".strip()

        # Search for relevant documentation
        results = self.search(query, top_k=3)

        if not results or "error" in results[0]:
            return {
                "topic": topic,
                "advice": "No relevant documentation found. Consider adding documentation on this topic.",
                "references": [],
                "confidence": 0.0,
            }

        # Generate simple advice based on search results
        references = []
        total_score = 0.0

        for result in results:
            if "error" not in result:
                references.append(
                    {
                        "source": result.get("source", "unknown"),
                        "relevance": result.get("score", 0.0),
                        "excerpt": result.get("text", "")[:200],
                    }
                )
                total_score += result.get("score", 0.0)

        avg_score = total_score / len(references) if references else 0.0

        # Generate advice text
        if avg_score > 0.7:
            advice = f"Project has strong documentation on {topic}. Review the referenced documents for best practices."
        elif avg_score > 0.4:
            advice = f"Project has some documentation on {topic}. Consider expanding coverage based on the references."
        else:
            advice = f"Limited documentation found on {topic}. Consider creating comprehensive documentation."

        return {
            "topic": topic,
            "advice": advice,
            "references": references,
            "confidence": avg_score,
            "search_query": query,
        }

    def analyze_project_gaps(self) -> List[Dict[str, Any]]:
        """
        Analyze documentation gaps in the project.

        Returns:
            List of identified gaps with recommendations.
        """
        # Common architecture topics to check
        topics = [
            "architecture",
            "microservices",
            "api design",
            "testing",
            "deployment",
            "monitoring",
            "security",
            "database",
            "scalability",
            "documentation",
        ]

        gaps = []

        for topic in topics:
            advice = self.get_advice(topic)

            if advice["confidence"] < 0.5:
                gaps.append(
                    {
                        "topic": topic,
                        "confidence": advice["confidence"],
                        "recommendation": f"Add comprehensive documentation on {topic}",
                        "references": advice["references"],
                    }
                )

        return gaps

    def get_stats(self) -> Dict[str, Any]:
        """Get RAG system statistics."""
        if not RAG_AVAILABLE or not self.searcher:
            return {"available": False}

        return {
            "available": True,
            "document_count": self.searcher.get_document_count(),
            "index_path": str(self.index_path),
            "index_exists": self.index_path.exists(),
        }


def analyze(root: Path) -> Dict[str, Any]:
    """
    Plugin entry point for Assistant Orchestrator.

    Args:
        root: Project root directory.

    Returns:
        RAG analysis results.
    """
    logger.info(f"Running RAG advisor analysis for {root}")

    advisor = RAGAdvisor(root)
    stats = advisor.get_stats()

    # Only build index if RAG is available and no index exists
    if stats.get("available") and not stats.get("index_exists"):
        build_result = advisor.build_index()
        stats["build_result"] = build_result

    # Analyze common documentation gaps
    gaps = []
    if stats.get("available"):
        gaps = advisor.analyze_project_gaps()

    # Get sample advice for architecture
    architecture_advice = {}
    if stats.get("available"):
        architecture_advice = advisor.get_advice("architecture")

    return {
        "rag_available": stats.get("available", False),
        "document_count": stats.get("document_count", 0),
        "index_exists": stats.get("index_exists", False),
        "documentation_gaps": gaps[:5],  # Top 5 gaps
        "architecture_advice": architecture_advice,
        "stats": stats,
    }


def search_docs(root: Path, query: str) -> List[Dict[str, Any]]:
    """
    Search project documentation (alternative entry point).

    Args:
        root: Project root directory.
        query: Search query.

    Returns:
        Search results.
    """
    advisor = RAGAdvisor(root)
    return advisor.search(query)


if __name__ == "__main__":
    # Test the plugin

    test_root = Path(".").resolve()
    advisor = RAGAdvisor(test_root)

    print("RAG Advisor Test")
    print("=" * 60)

    stats = advisor.get_stats()
    print(f"RAG Available: {stats.get('available')}")
    print(f"Document Count: {stats.get('document_count')}")

    if stats.get("available"):
        # Build index if needed
        if not stats.get("index_exists"):
            print("\nBuilding index...")
            build_result = advisor.build_index()
            print(f"Build result: {build_result}")

        # Test search
        print("\nTesting search...")
        results = advisor.search("microservices architecture", top_k=2)
        for i, result in enumerate(results):
            if "error" not in result:
                print(
                    f"{i+1}. {result.get('source')} (score: {result.get('score'):.3f})"
                )
                print(f"   {result.get('text')[:100]}...")

        # Test advice
        print("\nTesting advice...")
        advice = advisor.get_advice("testing")
        print(f"Topic: {advice.get('topic')}")
        print(f"Advice: {advice.get('advice')}")
        print(f"Confidence: {advice.get('confidence'):.3f}")

        # Analyze gaps
        print("\nAnalyzing documentation gaps...")
        gaps = advisor.analyze_project_gaps()
        for gap in gaps[:3]:
            print(
                f"- {gap['topic']} (confidence: {gap['confidence']:.3f}): {gap['recommendation']}"
            )
    else:
        print("\nRAG dependencies not available. Install:")
        print("  pip install sentence-transformers chromadb")
