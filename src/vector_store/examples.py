"""
Example usage of vector store for Cognitive Agent.

This script demonstrates how to use the vector store to:
1. Index documentation files
2. Search for relevant information
3. Use with planner for RAG-based reasoning
"""

import logging
from pathlib import Path

from src.vector_store import (
    DocumentChunker,
    DocumentLoader,
    get_vector_store,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def index_documents():
    """Index project documentation into vector store."""
    logger.info("Starting document indexing...")

    # Initialize vector store
    store = get_vector_store(
        store_type="chroma",
        config=None,  # Uses default config
    )

    # Load documents from files
    root_dir = Path(__file__).parent.parent.parent  # Go up to repo root
    documents = DocumentLoader.load_files(file_pattern="**/*.md", root_dir=str(root_dir))

    logger.info(f"Loaded {len(documents)} documents")

    # Chunk and index documents
    chunker = DocumentChunker(max_chunk_size=1000, overlap=100)
    indexed_count = 0

    for doc in documents:
        text = doc["text"]
        metadata = doc["metadata"]

        if not text.strip():
            continue

        # Chunk the document
        chunks = chunker.chunk_text(text)

        # Index each chunk
        for i, chunk in enumerate(chunks):
            chunk_metadata = metadata.copy()
            chunk_metadata["chunk_index"] = i
            chunk_metadata["total_chunks"] = len(chunks)

            doc_id = store.add_document(chunk, chunk_metadata)
            if doc_id:
                indexed_count += 1

    logger.info(f"Indexed {indexed_count} chunks from {len(documents)} documents")
    logger.info(f"Vector store stats: {store.get_stats()}")

    store.close()
    return indexed_count


def search_documents():
    """Search for relevant documents."""
    logger.info("Starting document search...")

    # Initialize vector store
    store = get_vector_store(store_type="chroma")

    # Example queries
    queries = [
        "How to integrate with IT-Compass?",
        "What is the architecture of Cognitive Agent?",
        "How to use GigaChat bridge?",
    ]

    for query in queries:
        logger.info(f"\n--- Query: {query} ---")
        results = store.search(query, top_k=3)

        for i, result in enumerate(results, 1):
            logger.info(f"Result {i} (score: {result['score']:.3f}):")
            logger.info(f"  Text: {result['text'][:100]}...")
            logger.info(f"  Source: {result['metadata'].get('source', 'N/A')}")

    store.close()


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Vector store demo for Cognitive Agent")
    parser.add_argument("--index", action="store_true", help="Index documents from files")
    parser.add_argument("--search", action="store_true", help="Search documents")
    parser.add_argument("--both", action="store_true", help="Index and then search")

    args = parser.parse_args()

    if args.index or args.both:
        index_documents()

    if args.search or args.both:
        search_documents()

    if not (args.index or args.search or args.both):
        logger.info("No action specified. Use --index, --search, or --both")
        logger.info("Example: python -m apps.cognitive_agent.scripts.vector_store_demo --both")


if __name__ == "__main__":
    main()
