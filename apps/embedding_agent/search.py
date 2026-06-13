"""
Simple search interface for RAG system.
"""

import logging
from pathlib import Path
from typing import Any

from .indexer import DocumentIndexer

logger = logging.getLogger(__name__)


class DocumentSearcher:
    """High-level search interface for RAG system."""

    def __init__(self, index_path: str | None = None) -> None:
        """
        Initialize searcher.

        Args:
            index_path: Path to pre-built index. If None, creates empty index.
        """
        self.indexer = DocumentIndexer()
        self.index_path: Path | None = Path(index_path) if index_path else None

        if self.index_path and self.index_path.exists():
            logger.info("Loading index from %s", index_path)
            self.indexer.load(str(self.index_path))
        else:
            logger.info("Starting with empty index")

    def build_index(
        self,
        file_pattern: str = "**/*.md",
        root_dir: str = ".",
        save: bool = True,
    ) -> dict[str, Any]:
        """
        Build index from files.

        Args:
            file_pattern: Glob pattern for files to index.
            root_dir: Root directory to search from.
            save: Whether to save index automatically after building.

        Returns:
            Statistics about the built index.
        """
        logger.info("Building index from %s in %s", file_pattern, root_dir)
        doc_ids = self.indexer.add_documents_from_files(file_pattern, root_dir)

        stats = self.indexer.get_stats()
        stats["files_indexed"] = len(doc_ids)
        stats["documents_added"] = len(doc_ids)

        # Auto-save if index path is set and save=True
        if save and self.index_path:
            self.save_index()

        logger.info(
            "Index built: %d documents from %d files",
            stats["total_documents"],
            len(doc_ids),
        )
        return stats

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
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

        if not query or not query.strip():
            logger.warning("Empty search query")
            return []

        logger.info("Searching for: '%s'", query)
        results = self.indexer.search(query, top_k)
        logger.info("Found %d results", len(results))

        return results

    def save_index(self, path: str | None = None) -> str:
        """
        Save index to disk.

        Args:
            path: Path to save index. If None, uses current index_path.

        Returns:
            Path where index was saved.
        """
        save_path: Path
        if path:
            save_path = Path(path)
        elif self.index_path:
            save_path = self.index_path
        else:
            # Default path
            save_path = Path("data/embeddings/index.pkl")
            save_path.parent.mkdir(parents=True, exist_ok=True)
            self.index_path = save_path

        self.indexer.save(str(save_path))
        self.index_path = save_path

        logger.info("Index saved to %s", save_path)
        return str(save_path)

    def load_index(self, path: str | None = None) -> None:
        """
        Load index from disk.

        Args:
            path: Path to load index from. If None, uses current index_path.
        """
        load_path: Path
        if path:
            load_path = Path(path)
        elif self.index_path:
            load_path = self.index_path
        else:
            raise ValueError("No index path provided or configured")

        if not load_path.exists():
            raise FileNotFoundError(f"Index file not found: {load_path}")

        self.indexer.load(str(load_path))
        self.index_path = load_path
        logger.info("Index loaded from %s", load_path)

    def get_document_count(self) -> int:
        """Get total number of documents in index."""
        return len(self.indexer.documents)

    def clear_index(self) -> None:
        """Clear all documents from index."""
        self.indexer.clear()
        logger.info("Index cleared")

    def get_stats(self) -> dict[str, Any]:
        """
        Get index statistics.

        Returns:
            Dictionary with index statistics.
        """
        stats = self.indexer.get_stats()
        stats["index_path"] = str(self.index_path) if self.index_path else None
        return stats

    def search_with_context(
        self,
        query: str,
        top_k: int = 5,
        include_metadata: bool = True,
    ) -> list[dict[str, Any]]:
        """
        Search and return results with context information.

        Args:
            query: Search query.
            top_k: Number of results to return.
            include_metadata: Whether to include full metadata.

        Returns:
            List of search results with context.
        """
        results = self.search(query, top_k)

        # Enhance results with additional context
        for result in results:
            if include_metadata:
                # Ensure metadata has required fields
                if "source" not in result["metadata"]:
                    result["metadata"]["source"] = "unknown"
                if "file_type" not in result["metadata"]:
                    result["metadata"]["file_type"] = "unknown"

            # Add snippet (first 100 chars)
            result["snippet"] = result["text"][:100] + "..." if len(result["text"]) > 100 else result["text"]

        return results


def search_demo() -> None:
    """Demo function to test the RAG system."""
    import sys

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

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

    # Check if we should load index
    elif len(sys.argv) > 1 and sys.argv[1] == "load" and len(sys.argv) > 2:
        try:
            searcher.load_index(sys.argv[2])
            print(f"Index loaded from: {sys.argv[2]}")
        except Exception as e:
            print(f"Failed to load index: {e}")
            return

    # Interactive search
    print("\n" + "=" * 60)
    print("RAG Search Demo")
    print("=" * 60)

    try:
        doc_count = searcher.get_document_count()
        print(f"Index contains {doc_count} documents")
    except Exception:
        print("Index is empty. Use 'build' command to create an index.")
        return

    if doc_count == 0:
        print("\n⚠️  Index is empty. Add documents using the 'build' command.")
        print("Example: python searcher.py build\n")

    print("\nEnter search queries (type 'exit' to quit)")
    print("Commands:")
    print("  /stats    - Show index statistics")
    print("  /clear    - Clear index")
    print("  /help     - Show this help")

    while True:
        try:
            user_input = input("\n🔍 Search: ").strip()
            if not user_input:
                continue

            # Handle commands
            if user_input.lower() in ["exit", "quit", "q"]:
                break
            elif user_input.lower() == "/stats":
                stats = searcher.get_stats()
                print("\n📊 Index Statistics:")
                for key, value in stats.items():
                    print(f"  {key}: {value}")
                continue
            elif user_input.lower() == "/clear":
                searcher.clear_index()
                print("✓ Index cleared")
                continue
            elif user_input.lower() == "/help":
                print("\nCommands:")
                print("  /stats    - Show index statistics")
                print("  /clear    - Clear index")
                print("  /help     - Show this help")
                print("  exit/q    - Exit the program")
                continue

            # Perform search
            results = searcher.search_with_context(user_input, top_k=3)

            if not results:
                print("❌ No results found.")
                continue

            print(f"\n✅ Found {len(results)} results:")
            for i, result in enumerate(results, start=1):
                print(f"\n📄 Result {i} (Score: {result['score']:.3f})")
                print(f"   Source: {result['metadata'].get('source', 'Unknown')}")
                print(f"   Type: {result['metadata'].get('file_type', 'Unknown')}")

                if "chunk" in result["metadata"]:
                    chunk_info = result["metadata"]["chunk"] + 1
                    total_chunks = result["metadata"].get("total_chunks", 1)
                    print(f"   Chunk: {chunk_info}/{total_chunks}")

                print(f"   Text: {result['snippet']}")

        except KeyboardInterrupt:
            print("\n\n👋 Exiting...")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            logger.exception("Search demo error")


if __name__ == "__main__":
    search_demo()
