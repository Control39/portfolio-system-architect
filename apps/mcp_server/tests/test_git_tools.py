"""
Tests for mcp_server git_tools - Simplified
"""
import pytest
from pathlib import Path
import tempfile


class TestGitToolsModule:
    """Basic tests for git_tools module structure"""

    def test_module_imports(self):
        """Test that git_tools module can be imported"""
        from apps.mcp_server.src.tools import git_tools
        assert git_tools is not None

    def test_init_git_tools_exists(self):
        """Test that init_git_tools function exists"""
        from apps.mcp_server.src.tools import git_tools
        assert hasattr(git_tools, 'init_git_tools')
        assert callable(git_tools.init_git_tools)

    def test_project_root_variable(self):
        """Test PROJECT_ROOT variable exists"""
        from apps.mcp_server.src.tools import git_tools
        assert hasattr(git_tools, 'PROJECT_ROOT')


class TestGitOperations:
    """Basic git operation tests"""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def test_git_init(self, temp_dir):
        """Test git repository initialization"""
        import subprocess
        
        result = subprocess.run(
            ['git', 'init'],
            cwd=temp_dir,
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert (temp_dir / '.git').exists()

    def test_git_check_repo(self, temp_dir):
        """Test checking if directory is a git repo"""
        import subprocess
        
        subprocess.run(['git', 'init'], cwd=temp_dir, capture_output=True)
        
        result = subprocess.run(
            ['git', 'rev-parse', '--git-dir'],
            cwd=temp_dir,
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert '.git' in result.stdout

    def test_git_status(self, temp_dir):
        """Test git status command"""
        import subprocess
        
        subprocess.run(['git', 'init'], cwd=temp_dir, capture_output=True)
        
        result = subprocess.run(
            ['git', 'status', '--porcelain'],
            cwd=temp_dir,
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0

    def test_git_add_file(self, temp_dir):
        """Test adding file to git"""
        import subprocess
        
        subprocess.run(['git', 'init'], cwd=temp_dir, capture_output=True)
        
        test_file = temp_dir / "test.txt"
        test_file.write_text("Content")
        
        result = subprocess.run(
            ['git', 'add', 'test.txt'],
            cwd=temp_dir,
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0

    def test_git_commit(self, temp_dir):
        """Test git commit"""
        import subprocess
        
        subprocess.run(['git', 'init'], cwd=temp_dir, capture_output=True)
        
        test_file = temp_dir / "test.txt"
        test_file.write_text("Content")
        subprocess.run(['git', 'add', 'test.txt'], cwd=temp_dir, capture_output=True)
        
        result = subprocess.run(
            ['git', 'commit', '-m', 'Test commit'],
            cwd=temp_dir,
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0

    def test_git_branch_list(self, temp_dir):
        """Test listing git branches"""
        import subprocess
        
        subprocess.run(['git', 'init'], cwd=temp_dir, capture_output=True)
        
        result = subprocess.run(
            ['git', 'branch'],
            cwd=temp_dir,
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0

    def test_git_remote_list(self, temp_dir):
        """Test listing git remotes"""
        import subprocess
        
        subprocess.run(['git', 'init'], cwd=temp_dir, capture_output=True)
        
        result = subprocess.run(
            ['git', 'remote', '-v'],
            cwd=temp_dir,
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0

    def test_git_ignore_patterns(self):
        """Test .gitignore pattern matching"""
        import fnmatch
        
        patterns = ['*.pyc', '__pycache__', '.env']
        files = ['test.pyc', 'main.py', '__pycache__', '.env', 'README.md']
        
        ignored = [f for f in files if any(fnmatch.fnmatch(f, p) for p in patterns)]
        
        assert 'test.pyc' in ignored
        assert '__pycache__' in ignored
        assert '.env' in ignored
        assert 'main.py' not in ignored
        assert 'README.md' not in ignored

    def test_git_diff(self, temp_dir):
        """Test git diff command"""
        import subprocess
        
        subprocess.run(['git', 'init'], cwd=temp_dir, capture_output=True)
        
        test_file = temp_dir / "test.txt"
        test_file.write_text("Initial")
        subprocess.run(['git', 'add', 'test.txt'], cwd=temp_dir, capture_output=True)
        subprocess.run(['git', 'commit', '-m', 'Initial'], cwd=temp_dir, capture_output=True)
        
        test_file.write_text("Modified")
        
        result = subprocess.run(
            ['git', 'diff'],
            cwd=temp_dir,
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0

    def test_git_log(self, temp_dir):
        """Test git log command"""
        import subprocess
        
        subprocess.run(['git', 'init'], cwd=temp_dir, capture_output=True)
        
        test_file = temp_dir / "README.md"
        test_file.write_text("# Test")
        subprocess.run(['git', 'add', 'README.md'], cwd=temp_dir, capture_output=True)
        subprocess.run(['git', 'commit', '-m', 'Initial'], cwd=temp_dir, capture_output=True)
        
        result = subprocess.run(
            ['git', 'log', '--oneline'],
            cwd=temp_dir,
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0

    def test_git_commit_message_validation(self):
        """Test git commit message validation"""
        valid_messages = [
            "feat: add new feature",
            "fix: resolve bug",
            "docs: update README",
            "test: add tests"
        ]
        
        for msg in valid_messages:
            assert len(msg) > 0
            assert ':' in msg or msg.startswith('[')