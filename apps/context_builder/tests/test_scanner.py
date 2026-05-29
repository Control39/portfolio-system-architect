# apps/context_builder/tests/test_scanner.py
from pathlib import Path

from apps.context_builder.core.scanner import ProjectScanner
from apps.context_builder.config.settings import settings


def test_scanner_finds_text_files(sample_project_structure):
    scanner = ProjectScanner(sample_project_structure, respect_gitignore=True)
    files = list(scanner.scan())
    paths = [f.rel_path for f in files]
    assert "src/main.py" in paths
    assert "README.md" in paths


def test_scanner_skips_binary_files(sample_project_structure):
    scanner = ProjectScanner(sample_project_structure, respect_gitignore=True)
    files = list(scanner.scan())
    paths = [f.rel_path for f in files]
    assert "image.png" not in paths


def test_scanner_skips_gitignore_files(sample_project_structure):
    scanner = ProjectScanner(sample_project_structure, respect_gitignore=True)
    files = list(scanner.scan())
    paths = [f.rel_path for f in files]
    assert "app.log" not in paths


def test_scanner_get_structure_only(sample_project_structure):
    scanner = ProjectScanner(sample_project_structure, respect_gitignore=True)
    structure = scanner.get_structure_only()
    assert "src/main.py" in structure
    assert "README.md" in structure
    assert "image.png" not in structure