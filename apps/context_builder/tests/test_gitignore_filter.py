# apps/context_builder/tests/test_gitignore_filter.py
from pathlib import Path

from apps.context_builder.core.gitignore_filter import GitIgnoreFilter


def test_gitignore_filter_ignores_pattern(sample_project_structure):
    gitignore_filter = GitIgnoreFilter(sample_project_structure)
    log_file = sample_project_structure / "app.log"
    assert gitignore_filter.is_ignored(log_file) is True


def test_gitignore_filter_allows_allowed_file(sample_project_structure):
    gitignore_filter = GitIgnoreFilter(sample_project_structure)
    main_py = sample_project_structure / "src" / "main.py"
    assert gitignore_filter.is_ignored(main_py) is False


def test_missing_gitignore_returns_false():
    non_existent = Path("/tmp/non-existent-project")
    gitignore_filter = GitIgnoreFilter(non_existent)
    assert gitignore_filter.is_ignored(Path("any.txt")) is False
