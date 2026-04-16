import pytest
import json
import tempfile
from pathlib import Path
import sys

sys.path.append(".")

from src.core.tracker import CareerTracker


def test_tracker_initialization():
    tracker = CareerTracker()
    assert tracker.markers_dir == Path("src/data/markers")
    assert tracker.progress_file == Path("src/data/user_progress.json")


def test_progress_file_creation():
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_progress = Path(temp_dir) / "progress.json"
        tracker = CareerTracker(progress_file=str(temp_progress))

        assert tracker.progress_file.exists()
        assert tracker.progress["completed_markers"] == []
        assert tracker.progress["in_progress_markers"] == []


if __name__ == "__main__":
    pytest.main([__file__])

