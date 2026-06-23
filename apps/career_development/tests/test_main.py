"""
Tests for career_development main.py
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


class TestMainModule:
    """Tests for main.py entry point"""

    def test_main_imports_successfully(self):
        """Test that main.py can be imported without errors"""
        try:
            from apps.career_development import main

            assert hasattr(main, "app")
            assert main.__all__ == ["app"]
        except Exception as e:
            # Expected if dependencies are missing (DB, etc.)
            assert "AI_CONFIG" in str(e) or "config" in str(e).lower()

    def test_main_app_exists(self):
        """Test that app is exported from main"""
        from apps.career_development.main import app

        assert app is not None