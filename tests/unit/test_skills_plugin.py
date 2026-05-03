"""Unit tests for skills plugin."""

import json
import sys
import tempfile
from pathlib import Path

# Add src to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from assistant_orchestrator.plugins.skills import analyze


def test_analyze_skills_no_markers():
    """Test analysis when markers directory doesn't exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        result = analyze(root)

        assert "error" in result
        assert result["total_count"] == 0
        assert result["categories"] == []
        assert result["markers"] == []


def test_analyze_skills_with_markers():
    """Test analysis with mock marker files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        markers_dir = root / "apps" / "it_compass" / "src" / "data" / "markers"
        markers_dir.mkdir(parents=True)

        # Create a mock Python skills marker file
        python_markers = {
            "levels": {
                "1": [
                    {
                        "id": "py-basics",
                        "description": "Basic Python syntax",
                        "evidence": [],
                    },
                    {
                        "id": "py-functions",
                        "description": "Define and use functions",
                        "evidence": [],
                    },
                ],
                "2": [
                    {
                        "id": "py-oop",
                        "description": "Object-oriented programming",
                        "evidence": [],
                    },
                ],
            },
        }

        with open(markers_dir / "python.json", "w", encoding="utf-8") as f:
            json.dump(python_markers, f)

        # Create a mock DevOps marker file
        devops_markers = {
            "levels": {
                "1": [
                    {
                        "id": "devops-ci",
                        "description": "Continuous Integration",
                        "evidence": [],
                    },
                ],
            },
        }

        with open(markers_dir / "devops.json", "w", encoding="utf-8") as f:
            json.dump(devops_markers, f)

        result = analyze(root)

        # Should find 3 markers total (2 + 1)
        assert result["total_count"] == 4
        # Should have 2 categories: "Python" and "Devops" (title case)
        assert len(result["categories"]) == 2
        assert "Python" in result["categories"]
        assert "Devops" in result["categories"]
        # Should have markers list
        assert len(result["markers"]) == 4
        # Each marker should have required fields
        for marker in result["markers"]:
            assert "id" in marker
            assert "category" in marker
            assert "level" in marker
            assert "description" in marker


def test_analyze_skills_invalid_json():
    """Test handling of invalid JSON files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        markers_dir = root / "apps" / "it_compass" / "src" / "data" / "markers"
        markers_dir.mkdir(parents=True)

        # Create invalid JSON
        with open(markers_dir / "invalid.json", "w", encoding="utf-8") as f:
            f.write("{ invalid json }")

        # Should not crash
        result = analyze(root)

        # Should still return empty results (or handle gracefully)
        assert "total_count" in result
        # The invalid file should be skipped


def test_analyze_skills_empty_markers():
    """Test analysis with empty marker file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        markers_dir = root / "apps" / "it_compass" / "src" / "data" / "markers"
        markers_dir.mkdir(parents=True)

        # Create empty markers
        empty_markers = {"levels": {}}

        with open(markers_dir / "empty.json", "w", encoding="utf-8") as f:
            json.dump(empty_markers, f)

        result = analyze(root)

        assert result["total_count"] == 0
        assert "Empty" in result["categories"]  # "Empty" from filename
        assert result["markers"] == []
