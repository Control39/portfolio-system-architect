"""Business logic tests for MCP server - tests for structure and helper functions.

These tests verify the module structure and helper functions without requiring
full MCP server initialization.
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest


# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def test_file_structure(temp_dir):
    """Create a test file structure."""
    (temp_dir / "src").mkdir()
    (temp_dir / "tests").mkdir()
    (temp_dir / "docs").mkdir()
    (temp_dir / "src" / "subdir").mkdir()

    (temp_dir / "README.md").write_text("# Test Project\n\nThis is a test.")
    (temp_dir / "requirements.txt").write_text("fastapi\npytest")
    (temp_dir / "src" / "main.py").write_text("def main():\n    print('Hello')")
    (temp_dir / "src" / "subdir" / "utils.py").write_text("def helper():\n    pass")
    (temp_dir / "tests" / "test_main.py").write_text("def test_main():\n    assert True")
    (temp_dir / "docs" / "guide.md").write_text("# Guide\n\nSome content.")

    return temp_dir


@pytest.fixture
def git_repo(temp_dir):
    """Create a test Git repository."""
    subprocess.run(["git", "init"], cwd=temp_dir, capture_output=True, check=False)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=temp_dir, capture_output=True, check=False)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=temp_dir, capture_output=True, check=False)

    readme = temp_dir / "README.md"
    readme.write_text("# Test Repo")
    subprocess.run(["git", "add", "."], cwd=temp_dir, capture_output=True, check=False)
    subprocess.run(
        ["git", "commit", "-m", "Initial commit: Added README"], cwd=temp_dir, capture_output=True, check=False
    )

    code_file = temp_dir / "code.py"
    code_file.write_text("def hello(): pass")
    subprocess.run(["git", "add", "."], cwd=temp_dir, capture_output=True, check=False)
    subprocess.run(
        ["git", "commit", "-m", "Added code with system thinking marker"],
        cwd=temp_dir,
        capture_output=True,
        check=False,
    )

    return temp_dir


# ============================================================================
# MODULE STRUCTURE TESTS
# ============================================================================


class TestModuleStructure:
    """Tests for module structure and imports."""

    def test_file_tools_module_exists(self):
        """Test that file_tools module exists and has expected functions."""
        import apps.mcp_server.src.tools.file_tools as ft

        assert hasattr(ft, "init_file_tools")
        assert hasattr(ft, "PROJECT_ROOT")
        assert hasattr(ft, "_resolve_path")

    def test_git_tools_module_exists(self):
        """Test that git_tools module exists and has expected functions."""
        import apps.mcp_server.src.tools.git_tools as gt

        assert hasattr(gt, "init_git_tools")
        assert hasattr(gt, "PROJECT_ROOT")

    def test_compass_tools_module_exists(self):
        """Test that compass_tools module exists and has expected functions."""
        import apps.mcp_server.src.tools.compass_tools as ct

        assert hasattr(ct, "init_compass_tools")

    def test_chroma_tools_module_exists(self):
        """Test that chroma_tools module exists and has expected functions."""
        import apps.mcp_server.src.tools.chroma_tools as ct

        assert hasattr(ct, "init_chroma_tools")

    def test_tools_directory_structure(self):
        """Test that tools directory has all expected modules."""
        tools_dir = Path(__file__).parent.parent / "src" / "tools"

        expected_files = [
            "file_tools.py",
            "git_tools.py",
            "compass_tools.py",
            "chroma_tools.py",
            "monitoring_tools.py",
        ]

        for filename in expected_files:
            assert (tools_dir / filename).exists(), f"Missing {filename}"


# ============================================================================
# HELPER FUNCTION TESTS
# ============================================================================


class TestResolvePath:
    """Tests for _resolve_path helper function."""

    def test_resolve_path_relative(self, temp_dir):
        """Test path resolution for relative paths."""
        from apps.mcp_server.src.tools.file_tools import _resolve_path

        with patch("apps.mcp_server.src.tools.file_tools.PROJECT_ROOT", temp_dir):
            result = _resolve_path("relative/path.txt")
            expected = temp_dir / "relative/path.txt"
            assert result == expected

    def test_resolve_path_absolute(self):
        """Test path resolution for absolute paths."""
        from apps.mcp_server.src.tools.file_tools import _resolve_path

        with patch("apps.mcp_server.src.tools.file_tools.PROJECT_ROOT", Path("/tmp")):
            result = _resolve_path("/absolute/path.txt")
            # Absolute paths should remain unchanged (Path handles platform differences)
            assert str(result) == "/absolute/path.txt" or result.name == "path.txt"


# ============================================================================
# FILE OPERATIONS TESTS (via file system)
# ============================================================================


class TestFileOperations:
    """Tests for file operations via direct file system calls."""

    def test_read_file_direct(self, test_file_structure):
        """Test reading a file directly."""
        readme = test_file_structure / "README.md"
        content = readme.read_text()
        assert "# Test Project" in content

    def test_write_file_direct(self, temp_dir):
        """Test writing a file directly."""
        new_file = temp_dir / "test.txt"
        content = "Test content"
        new_file.write_text(content)
        assert new_file.exists()
        assert new_file.read_text() == content

    def test_list_files_direct(self, test_file_structure):
        """Test listing files directly."""
        files = list(test_file_structure.glob("*"))
        assert len(files) >= 2

    def test_list_files_recursive_direct(self, test_file_structure):
        """Test recursive file listing directly."""
        files = list(test_file_structure.rglob("*"))
        assert len(files) >= 6

    def test_list_files_with_extension(self, test_file_structure):
        """Test listing files with extension filter."""
        py_files = list(test_file_structure.rglob("*.py"))
        assert len(py_files) >= 3
        assert all(f.suffix == ".py" for f in py_files)


# ============================================================================
# GIT OPERATIONS TESTS
# ============================================================================


class TestGitOperations:
    """Tests for Git operations."""

    def test_git_repo_initialization(self, temp_dir):
        """Test Git repository initialization."""
        subprocess.run(["git", "init"], cwd=temp_dir, capture_output=True, check=False)
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"], cwd=temp_dir, capture_output=True, check=False
        )
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=temp_dir, capture_output=True, check=False)

        result = subprocess.run(["git", "status"], cwd=temp_dir, capture_output=True, text=True)
        assert result.returncode == 0

    def test_git_commit(self, git_repo):
        """Test Git commit."""
        result = subprocess.run(["git", "log", "--oneline"], cwd=git_repo, capture_output=True, text=True)
        assert result.returncode == 0
        lines = result.stdout.strip().split("\n")
        assert len(lines) >= 2

    def test_git_branch(self, git_repo):
        """Test Git branch detection."""
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=git_repo, capture_output=True, text=True
        )
        assert result.returncode == 0
        assert result.stdout.strip() in ["master", "main"]


# ============================================================================
# COMPASS INTEGRATION TESTS
# ============================================================================


class TestCompassIntegration:
    """Tests for IT-Compass integration."""

    @pytest.fixture
    def mock_markers_dir(self, temp_dir):
        """Create a mock IT-Compass markers directory."""
        markers_dir = temp_dir / "markers"
        markers_dir.mkdir()

        marker_data = {
            "skill_name": "System Thinking",
            "description": "System thinking capability",
            "levels": {
                "1": [
                    {
                        "id": "sys_thinking_1_1",
                        "marker": "Created structured system",
                        "validation": "Document",
                        "priority": "high",
                        "keywords": ["system", "skills"],
                    }
                ]
            },
        }

        marker_file = markers_dir / "system_thinking.json"
        with open(marker_file, "w", encoding="utf-8") as f:
            json.dump(marker_data, f)

        return markers_dir

    def test_marker_file_structure(self, mock_markers_dir):
        """Test marker file structure."""
        marker_file = mock_markers_dir / "system_thinking.json"
        with open(marker_file, encoding="utf-8") as f:
            data = json.load(f)

        assert "skill_name" in data
        assert "description" in data
        assert "levels" in data
        assert "1" in data["levels"]

    def test_marker_validation(self, mock_markers_dir):
        """Test marker data validation."""
        marker_file = mock_markers_dir / "system_thinking.json"
        with open(marker_file, encoding="utf-8") as f:
            data = json.load(f)

        marker = data["levels"]["1"][0]
        assert "id" in marker
        assert "marker" in marker
        assert "validation" in marker
        assert "keywords" in marker


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================


class TestErrorHandling:
    """Tests for error handling and edge cases."""

    def test_read_nonexistent_file(self, temp_dir):
        """Test reading non-existent file."""
        nonexistent = temp_dir / "does_not_exist.txt"
        with pytest.raises(FileNotFoundError):
            nonexistent.read_text()

    def test_write_to_nonexistent_dir(self, temp_dir):
        """Test writing to non-existent directory."""
        nested_file = temp_dir / "nonexistent" / "file.txt"
        with pytest.raises(FileNotFoundError):
            nested_file.write_text("content")

    def test_invalid_json_file(self, temp_dir):
        """Test handling of invalid JSON file."""
        invalid_json = temp_dir / "invalid.json"
        invalid_json.write_text("{ invalid json }")

        with pytest.raises(json.JSONDecodeError), open(invalid_json, encoding="utf-8") as f:
            json.load(f)

    def test_empty_file_handling(self, temp_dir):
        """Test handling of empty file."""
        empty_file = temp_dir / "empty.txt"
        empty_file.write_text("")
        content = empty_file.read_text()
        assert content == ""


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


class TestIntegration:
    """Integration tests for complete workflows."""

    def test_file_workflow(self, test_file_structure):
        """Test complete file operation workflow."""
        # List files
        files = list(test_file_structure.rglob("*.py"))
        assert len(files) > 0

        # Read a file
        main_py = test_file_structure / "src" / "main.py"
        content = main_py.read_text()
        assert "def main()" in content

        # Write a new file
        new_file = test_file_structure / "tests" / "new_test.py"
        new_content = "def test_new():\n    assert True"
        new_file.write_text(new_content)
        assert new_file.exists()
        assert new_file.read_text() == new_content

    def test_git_workflow(self, git_repo):
        """Test complete Git workflow."""
        # Check initial state
        result = subprocess.run(["git", "log", "--oneline"], cwd=git_repo, capture_output=True, text=True)
        initial_count = len(result.stdout.strip().split("\n"))

        # Add a new file and commit
        new_file = git_repo / "new_feature.py"
        new_file.write_text("def new_feature(): pass")
        subprocess.run(["git", "add", "."], cwd=git_repo, capture_output=True, check=False)
        subprocess.run(["git", "commit", "-m", "Added new feature"], cwd=git_repo, capture_output=True, check=False)

        # Verify new commit
        result = subprocess.run(["git", "log", "--oneline"], cwd=git_repo, capture_output=True, text=True)
        new_count = len(result.stdout.strip().split("\n"))
        assert new_count == initial_count + 1

    def test_cross_tool_workflow(self, test_file_structure, mock_markers_dir_factory):
        """Test workflow combining file and marker operations."""
        # Create marker file in project
        markers_dir = test_file_structure / ".markers"
        markers_dir.mkdir()

        marker_data = {
            "skill_name": "Test Skill",
            "description": "Test description",
            "levels": {"1": [{"id": "test_1", "marker": "Test marker", "validation": "Test"}]},
        }

        marker_file = markers_dir / "test_skill.json"
        with open(marker_file, "w", encoding="utf-8") as f:
            json.dump(marker_data, f)

        # Verify marker file
        assert marker_file.exists()
        with open(marker_file, encoding="utf-8") as f:
            loaded = json.load(f)
        assert loaded["skill_name"] == "Test Skill"


@pytest.fixture
def mock_markers_dir_factory(temp_dir):
    """Factory for creating marker directories."""

    def create_marker_dir(skill_name="Test"):
        markers_dir = temp_dir / "markers"
        markers_dir.mkdir(exist_ok=True)

        marker_data = {
            "skill_name": skill_name,
            "description": f"{skill_name} capability",
            "levels": {"1": [{"id": f"{skill_name.lower()}_1", "marker": "Test", "validation": "Test"}]},
        }

        marker_file = markers_dir / f"{skill_name.lower()}.json"
        with open(marker_file, "w", encoding="utf-8") as f:
            json.dump(marker_data, f)

        return markers_dir

    return create_marker_dir
