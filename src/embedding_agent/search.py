"""
Simple search interface for RAG system.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from .indexer import DocumentIndexer

logger = logging.getLogger(__name__)


class DocumentSearcher:
    """High-level search interface for RAG system."""

    def __init__(self, index_path: Optional[str] = None):
        """
        Initialize searcher.

        Args:
            index_path: Path to pre-built index. If None, creates empty index.
        """
        self.indexer = DocumentIndexer()
        self.index_path = Path(index_path) if index_path else None

        if index_path and Path(index_path).exists():
            logger.info(f"Loading index from {index_path}")
            self.indexer.load(index_path)
        else:
            logger.info("Starting with empty index")

    def build_index(self, file_pattern: str = "**/*.md", root_dir: str = ".") -> Dict[str, Any]:
        """
        Build index from files.

        Args:
            file_pattern: Glob pattern for files to index.
            root_dir: Root directory to search from.

        Returns:
            Statistics about the built index.
        """
        logger.info(f"Building index from {file_pattern} in {root_dir}")
        doc_ids = self.indexer.add_documents_from_files(file_pattern, root_dir)

        stats = self.indexer.get_stats()
        stats["files_indexed"] = len(doc_ids)

        # Auto-save if index path is set
        if self.index_path:
            self.indexer.save(str(self.index_path))

        return stats

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search the index.

        Args:
            query: Search query.
            top_k: Number of results to return.

        Returns:
            List of search results.
        """
        if not self.indexer.documents:
            logger.warning("Index is empty, no documents to search")
            return []

        logger.info(f"Searching for: '{query}'")
        results = self.indexer.search(query, top_k)
        logger.info(f"Found {len(results)} results")

        return results

    def save_index(self, path: Optional[str] = None) -> str:
        """
        Save index to disk.

        Args:
            path: Path to save index. If None, uses current index_path.

        Returns:
            Path where index was saved.
        """
        save_path = path or self.index_path
        if not save_path:
            # Default path
            save_path = Path("data/embeddings/index.pkl")
            save_path.parent.mkdir(parents=True, exist_ok=True)

        self.indexer.save(str(save_path))
        self.index_path = Path(save_path)

        return str(save_path)

    def get_document_count(self) -> int:
        """Get total number of documents in index."""
        return len(self.indexer.documents)

    def clear_index(self) -> None:
        """Clear all documents from index."""
        self.indexer.documents.clear()
        self.indexer.embeddings.clear()
        logger.info("Index cleared")


def search_demo():
    """Demo function to test the RAG system."""
    import sys

    # Setup logging
    logging.basicConfig(level=logging.INFO)

    # Create searcher
    searcher = DocumentSearcher()

    # Check if we should build index
    if len(sys.argv) > 1 and sys.argv[1] == "build":
        print("Building index from markdown files...")
        stats = searcher.build_index()
        print(f"Index built: {stats}")

        # Save index
        index_path = searcher.save_index()
        print(f"Index saved to: {index_path}")

    # Interactive search
    print("\n" + "=" * 60)
    print("RAG Search Demo")
    print("=" * 60)
    print(f"Index contains {searcher.get_document_count()} documents")
    print("Enter search queries (type 'exit' to quit)")

    while True:
        try:
            query = input("\n🔍 Search: ").strip()
            if query.lower() in ["exit", "quit", "q"]:
                break

            if not query:
                continue

            results = searcher.search(query, top_k=3)

            if not results:
                print("No results found.")
                continue

            print(f"\nFound {len(results)} results:")
            for i, result in enumerate(results):
                print(f"\n{i + 1}. Score: {result['score']:.3f}")
                print(f"   Source: {result['metadata'].get('source', 'Unknown')}")
                if "chunk" in result["metadata"]:
                    print(
                        f"   Chunk: {result['metadata']['chunk'] + 1}/{result['metadata'].get('total_chunks', 1)}"
                    )
                print(f"   Text: {result['text'][:200]}...")

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    search_demo()
