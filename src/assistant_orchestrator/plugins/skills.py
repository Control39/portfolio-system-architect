"""
Skills plugin for analyzing IT-Compass markers.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)


def analyze(root: Path) -> Dict[str, Any]:
    """Analyze skill markers from IT-Compass."""
    markers_dir = root / "apps" / "it_compass" / "src" / "data" / "markers"

    if not markers_dir.exists():
        logger.warning(f"Markers directory not found: {markers_dir}")
        return {
            "error": "markers dir not found",
            "total_count": 0,
            "categories": [],
            "markers": [],
        }

    markers = []
    categories = set()
    total_markers = 0

    for file in markers_dir.glob("*.json"):
        category = file.stem.replace("_", " ").title()
        categories.add(category)

        try:
            with open(file, "r", encoding="utf-8-sig") as f:
                data = json.load(f)

            # Count markers across all levels
            levels = data.get("levels", {})
            for level_num, level_markers in levels.items():
                if isinstance(level_markers, list):
                    total_markers += len(level_markers)
                    for marker in level_markers:
                        if isinstance(marker, dict):
                            markers.append(
                                {
                                    "id": marker.get("id", ""),
                                    "category": category,
                                    "level": int(level_num),
                                    "description": marker.get("description", ""),
                                    "evidence": marker.get("evidence", []),
                                }
                            )
        except Exception as e:
            logger.error(f"Failed to parse {file}: {e}")
            continue

    logger.info(f"Found {total_markers} markers in {len(categories)} categories")

    return {
        "total_count": total_markers,
        "categories": sorted(list(categories)),
        "markers": markers[:100],  # Limit to first 100 for performance
    }
