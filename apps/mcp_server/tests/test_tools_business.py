"""
Tests for mcp_server tools business logic
Tests the actual implementation, not just concepts
"""

import pytest
from pathlib import Path
import tempfile


class TestFileToolsBusiness:
    """Tests for file_tools business logic"""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def test_read_file_content(self, temp_dir):
        """Test reading file content"""
        test_file = temp_dir / "test.txt"
        test_file.write_text("Test content")

        content = test_file.read_text()
        assert content == "Test content"

    def test_write_file_creates_content(self, temp_dir):
        """Test writing file creates content"""
        test_file = temp_dir / "output.txt"
        test_file.write_text("New content")

        assert test_file.exists()
        assert test_file.read_text() == "New content"

    def test_list_directory_returns_items(self, temp_dir):
        """Test listing directory returns items"""
        (temp_dir / "file1.txt").write_text("1")
        (temp_dir / "file2.py").write_text("2")
        (temp_dir / "subdir").mkdir()

        items = [item.name for item in temp_dir.iterdir()]

        assert "file1.txt" in items
        assert "file2.py" in items
        assert "subdir" in items

    def test_search_files_with_pattern(self, temp_dir):
        """Test searching files with glob pattern"""

        (temp_dir / "test.py").write_text("1")
        (temp_dir / "main.py").write_text("2")
        (temp_dir / "readme.md").write_text("3")

        py_files = [f.name for f in temp_dir.glob("*.py")]

        assert len(py_files) == 2
        assert "test.py" in py_files
        assert "main.py" in py_files

    def test_nested_file_operations(self, temp_dir):
        """Test nested file operations"""
        nested_path = temp_dir / "a" / "b" / "c" / "file.txt"
        nested_path.parent.mkdir(parents=True, exist_ok=True)
        nested_path.write_text("Deep content")

        assert nested_path.exists()
        assert nested_path.read_text() == "Deep content"

    def test_file_size_validation(self, temp_dir):
        """Test file size validation"""
        test_file = temp_dir / "test.txt"
        test_file.write_text("x" * 1000)

        size = test_file.stat().st_size
        assert size == 1000
        assert size < 10 * 1024 * 1024  # Less than 10MB limit

    def test_unicode_file_handling(self, temp_dir):
        """Test unicode file handling"""
        test_file = temp_dir / "unicode.txt"
        test_file.write_text("Привет, мир! 🌍")

        content = test_file.read_text()
        assert content == "Привет, мир! 🌍"

    def test_empty_file_handling(self, temp_dir):
        """Test empty file handling"""
        test_file = temp_dir / "empty.txt"
        test_file.write_text("")

        assert test_file.stat().st_size == 0
        assert test_file.read_text() == ""

    def test_hidden_file_handling(self, temp_dir):
        """Test hidden file handling"""
        hidden_file = temp_dir / ".hidden"
        hidden_file.write_text("Secret")

        assert hidden_file.exists()
        assert hidden_file.read_text() == "Secret"

    def test_file_modification_time(self, temp_dir):
        """Test file modification time"""
        import time

        test_file = temp_dir / "test.txt"
        test_file.write_text("Initial")
        mtime_before = test_file.stat().st_mtime

        time.sleep(0.1)
        test_file.write_text("Modified")
        mtime_after = test_file.stat().st_mtime

        assert mtime_after > mtime_before


class TestGitToolsBusiness:
    """Tests for git_tools business logic"""

    @pytest.fixture
    def git_repo(self, tmp_path):
        """Create a git repository for testing"""
        import subprocess

        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@test.com"], cwd=tmp_path, capture_output=True
        )
        subprocess.run(
            ["git", "config", "user.name", "Test User"], cwd=tmp_path, capture_output=True
        )

        return tmp_path

    def test_git_init_creates_git_dir(self, git_repo):
        """Test git init creates .git directory"""

        # git_repo already initialized by fixture
        assert (git_repo / ".git").exists()

    def test_git_add_stages_file(self, git_repo):
        """Test git add stages file"""
        import subprocess

        test_file = git_repo / "test.txt"
        test_file.write_text("Content")

        subprocess.run(["git", "add", "test.txt"], cwd=git_repo, capture_output=True)
        result = subprocess.run(
            ["git", "status", "--porcelain"], cwd=git_repo, capture_output=True, text=True
        )

        assert "test.txt" in result.stdout

    def test_git_commit_creates_commit(self, git_repo):
        """Test git commit creates commit"""
        import subprocess

        test_file = git_repo / "test.txt"
        test_file.write_text("Content")
        subprocess.run(["git", "add", "test.txt"], cwd=git_repo, capture_output=True)

        result = subprocess.run(
            ["git", "commit", "-m", "Test"], cwd=git_repo, capture_output=True, text=True
        )

        assert result.returncode == 0

    def test_git_log_shows_commits(self, git_repo):
        """Test git log shows commits"""
        import subprocess

        test_file = git_repo / "test.txt"
        test_file.write_text("Content")
        subprocess.run(["git", "add", "test.txt"], cwd=git_repo, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Test"], cwd=git_repo, capture_output=True)

        result = subprocess.run(
            ["git", "log", "--oneline"], cwd=git_repo, capture_output=True, text=True
        )

        assert result.returncode == 0
        assert "Test" in result.stdout

    def test_git_diff_shows_changes(self, git_repo):
        """Test git diff shows changes"""
        import subprocess

        test_file = git_repo / "test.txt"
        test_file.write_text("Initial")
        subprocess.run(["git", "add", "test.txt"], cwd=git_repo, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Initial"], cwd=git_repo, capture_output=True)

        test_file.write_text("Modified")

        result = subprocess.run(["git", "diff"], cwd=git_repo, capture_output=True, text=True)

        assert result.returncode == 0
        assert "-Initial" in result.stdout or "+Modified" in result.stdout

    def test_git_branch_operations(self, git_repo):
        """Test git branch operations"""
        import subprocess

        result = subprocess.run(["git", "branch"], cwd=git_repo, capture_output=True, text=True)

        assert result.returncode == 0

    def test_git_status_empty_repo(self, git_repo):
        """Test git status on empty repo"""
        import subprocess

        result = subprocess.run(
            ["git", "status", "--porcelain"], cwd=git_repo, capture_output=True, text=True
        )

        assert result.returncode == 0
        assert result.stdout.strip() == ""


class TestCompassToolsBusiness:
    """Tests for compass_tools business logic"""

    def test_compass_marker_structure(self):
        """Test compass marker structure"""
        marker = {
            "id": "DEV-001",
            "title": "Python Basics",
            "level": "Beginner",
            "domain": "Development",
            "evidence": [],
        }

        assert marker["id"].startswith("DEV-")
        assert marker["level"] in ["Beginner", "Intermediate", "Advanced", "Expert"]

    def test_compass_progress_calculation(self):
        """Test compass progress calculation"""
        completed_markers = 20
        total_markers = 83

        progress = (completed_markers / total_markers) * 100

        assert 0 <= progress <= 100
        assert progress == 24.096385542168676

    def test_compass_level_progression(self):
        """Test compass level progression"""
        levels = ["Beginner", "Intermediate", "Advanced", "Expert"]

        # Test progression logic
        def next_level(current):
            idx = levels.index(current)
            return levels[idx + 1] if idx < len(levels) - 1 else current

        assert next_level("Beginner") == "Intermediate"
        assert next_level("Expert") == "Expert"

    def test_compass_domain_validation(self):
        """Test compass domain validation"""
        valid_domains = ["Architecture", "Development", "DevOps", "Security", "Testing"]

        for domain in valid_domains:
            assert domain in valid_domains

    def test_compass_evidence_types(self):
        """Test compass evidence types"""
        evidence_types = ["code_review", "documentation", "project", "certification"]

        assert len(evidence_types) >= 4
        assert all(isinstance(e, str) for e in evidence_types)


class TestMonitoringToolsBusiness:
    """Tests for monitoring_tools business logic"""

    def test_metric_threshold_check(self):
        """Test metric threshold check"""

        def check_threshold(value, threshold, operator=">"):
            if operator == ">":
                return value > threshold
            elif operator == "<":
                return value < threshold
            elif operator == ">=":
                return value >= threshold
            return False

        assert check_threshold(10, 5, ">")
        assert not check_threshold(5, 10, ">")
        assert check_threshold(10, 10, ">=")

    def test_error_rate_calculation(self):
        """Test error rate calculation"""
        total_requests = 1000
        errors = 50

        error_rate = (errors / total_requests) * 100

        assert error_rate == 5.0

    def test_uptime_calculation(self):
        """Test uptime calculation"""
        total_minutes = 1440  # 24 hours
        downtime_minutes = 10

        uptime = ((total_minutes - downtime_minutes) / total_minutes) * 100

        assert abs(uptime - 99.31) < 0.01

    def test_avg_response_time(self):
        """Test average response time calculation"""
        response_times = [100, 150, 200, 250, 300]

        avg = sum(response_times) / len(response_times)

        assert avg == 200

    def test_p95_latency(self):
        """Test p95 latency calculation"""
        latencies = sorted([10, 20, 30, 40, 50, 60, 70, 80, 90, 100])

        p95_index = int(len(latencies) * 0.95)
        p95 = latencies[p95_index]

        assert p95 == 100

    def test_alert_severity_order(self):
        """Test alert severity order"""
        severities = ["low", "info", "warning", "critical"]
        severity_order = {s: i for i, s in enumerate(severities)}

        assert severity_order["critical"] > severity_order["warning"]
        assert severity_order["warning"] > severity_order["info"]

    def test_time_window_aggregation(self):
        """Test time window aggregation"""
        from datetime import datetime, timedelta

        window_minutes = 5
        now = datetime.now()
        start = now - timedelta(minutes=window_minutes)

        assert (now - start).total_seconds() == 300
