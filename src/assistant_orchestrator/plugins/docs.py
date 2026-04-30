"""
Documentation plugin for finding architecture documentation.
"""

import logging
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)


def find_docs(root: Path) -> List[str]:
    """Find architecture documentation files."""
    doc_patterns = [
        "**/ARCHITECTURE*.md",
        "**/architecture*.md",
        "**/DESIGN*.md",
        "**/design*.md",
        "**/docs/architecture/**/*.md",
        "**/docs/design/**/*.md",
        "**/*.architecture.md",
    ]

    found_docs = []

    for pattern in doc_patterns:
        try:
            for doc in root.glob(pattern):
                if doc.is_file():
                    # Skip very large files
                    if doc.stat().st_size > 10 * 1024 * 1024:  # 10 MB
                        continue
                    rel_path = str(doc.relative_to(root))
                    found_docs.append(rel_path)
        except Exception as e:
            logger.debug(f"Error scanning for pattern {pattern}: {e}")

    # Remove duplicates (same file may match multiple patterns)
    found_docs = list(set(found_docs))

    # Also check for specific known architecture docs
    known_docs = [
        root / "docs" / "architecture.md",
        root / "ARCHITECTURE.md",
        root / "DESIGN.md",
        root / "docs" / "ARCHITECTURE.md",
    ]

    for doc in known_docs:
        if doc.exists() and str(doc.relative_to(root)) not in found_docs:
            found_docs.append(str(doc.relative_to(root)))

    logger.info(f"Found {len(found_docs)} architecture documents")
    return sorted(found_docs)
