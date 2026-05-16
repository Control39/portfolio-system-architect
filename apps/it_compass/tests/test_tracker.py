import sys
import tempfile
from pathlib import Path

import pytest

sys.path.append(".")

from apps.it_compass.src.core.tracker import CareerTracker


def test_tracker_initialization():
    tracker = CareerTracker()
    # Теперь пути абсолютные, проверяем, что они содержат ожидаемые компоненты
    markers_dir_str = str(tracker.markers_dir)
    progress_file_str = str(tracker.progress_file)
    assert "it_compass" in markers_dir_str
    assert "src" in markers_dir_str
    assert "markers" in markers_dir_str
    assert "it_compass" in progress_file_str
    assert "src" in progress_file_str
    assert "user_progress.json" in progress_file_str


def test_progress_file_creation():
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_progress = Path(temp_dir) / "progress.json"
        tracker = CareerTracker(progress_file=str(temp_progress))

        # Создаем файл прогресса
        tracker._save_progress()
        assert tracker.progress_file.exists()
        assert tracker.progress["completed_markers"] == []
        assert tracker.progress["in_progress_markers"] == []


if __name__ == "__main__":
    pytest.main([__file__])
