"""
Document utilities for chunking and loading.
"""

import logging
from pathlib import Path
from typing import Any


logger = logging.getLogger(__name__)


class DocumentChunker:
    """Utilities for chunking documents into smaller pieces."""

    def __init__(self, max_chunk_size: int = 1000, overlap: int = 100):
        """
        Initialize chunker.

        Args:
            max_chunk_size: Maximum chunk size in characters.
            overlap: Overlap between chunks in characters.
        """
        self.max_chunk_size = max_chunk_size
        self.overlap = overlap

    def chunk_text(self, text: str) -> list[str]:
        """
        Split text into chunks.

        Args:
            text: Text to chunk.

        Returns:
            List of text chunks.
        """
        if len(text) <= self.max_chunk_size:
            return [text]

        chunks = []
        paragraphs = text.split("\n\n")
        current_chunk = ""

        for para in paragraphs:
            if len(current_chunk) + len(para) + 2 <= self.max_chunk_size:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = para + "\n\n"

        if current_chunk:
            chunks.append(current_chunk.strip())

        # If any chunk is still too large, split by sentences
        final_chunks = []
        for chunk in chunks:
            if len(chunk) > self.max_chunk_size * 2:
                # Fallback to character-based chunking
                for i in range(0, len(chunk), self.max_chunk_size):
                    final_chunks.append(chunk[i : i + self.max_chunk_size])
            else:
                final_chunks.append(chunk)

        # Add overlap
        if self.overlap > 0 and len(final_chunks) > 1:
            chunked_with_overlap = []
            for i, chunk in enumerate(final_chunks):
                if i > 0:
                    prev_chunk = final_chunks[i - 1][-self.overlap :]
                    chunk = prev_chunk + "\n\n" + chunk
                chunked_with_overlap.append(chunk)
            return chunked_with_overlap

        return final_chunks


class DocumentLoader:
    """Load documents from various sources."""

    @staticmethod
    def load_file(file_path: str | Path) -> dict[str, Any]:
        """
        Load a single file.

        Args:
            file_path: Path to file.

        Returns:
            Dict with 'text' and 'metadata'.
        """
        file_path = Path(file_path)

        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return {"text": "", "metadata": {}}

        try:
            content = file_path.read_text(encoding="utf-8")
            metadata = {
                "source": str(file_path),
                "file_size": file_path.stat().st_size,
                "last_modified": file_path.stat().st_mtime,
                "file_type": file_path.suffix,
                "file_name": file_path.name,
            }

            return {"text": content, "metadata": metadata}

        except Exception as e:
            logger.error(f"Error loading file {file_path}: {e}")
            return {"text": "", "metadata": {}}

    @staticmethod
    def load_files(file_pattern: str = "**/*.md", root_dir: str = ".") -> list[dict[str, Any]]:
        """
        Load multiple files matching pattern.

        Args:
            file_pattern: Glob pattern for files.
            root_dir: Root directory to search from.

        Returns:
            List of dicts with 'text' and 'metadata'.
        """
        root = Path(root_dir)
        file_paths = list(root.glob(file_pattern))
        logger.info(f"Found {len(file_paths)} files matching {file_pattern}")

        documents = []
        for file_path in file_paths:
            doc = DocumentLoader.load_file(file_path)
            if doc["text"]:
                documents.append(doc)

        return documents
