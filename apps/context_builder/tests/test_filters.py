# apps/context_builder/tests/test_filters.py

from apps.context_builder.core.filters import FileFilter


def test_filter_includes_allowed_extension(sample_project_structure):
    filter_obj = FileFilter()
    py_file = sample_project_structure / "src" / "main.py"
    assert filter_obj.should_include(py_file, sample_project_structure) is True


def test_filter_excludes_by_size_limit(sample_project_structure):
    filter_obj = FileFilter()
    # Переопределим лимит
    filter_obj.max_size_bytes = 10
    small_file = sample_project_structure / "small.txt"
    small_file.write_text("Hi")
    large_file = sample_project_structure / "large.txt"
    large_file.write_text("A" * 100)
    assert filter_obj.should_include(small_file, sample_project_structure) is True
    assert filter_obj.should_include(large_file, sample_project_structure) is False


def test_filter_excludes_by_directory(sample_project_structure):
    filter_obj = FileFilter()
    pycache = sample_project_structure / "__pycache__" / "file.pyc"
    pycache.parent.mkdir(exist_ok=True)
    pycache.write_text("fake")
    assert filter_obj.should_include(pycache, sample_project_structure) is False


def test_filter_add_remove_extension():
    filter_obj = FileFilter()
    filter_obj.add_extension("xyz")
    assert ".xyz" in filter_obj.extensions
    filter_obj.remove_extension("xyz")
    assert ".xyz" not in filter_obj.extensions
