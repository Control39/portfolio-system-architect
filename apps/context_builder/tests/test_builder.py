# apps/context_builder/tests/test_builder.py
from pathlib import Path

from apps.context_builder.core.builder import ContextBuilder
from apps.context_builder.config.settings import settings


def test_builder_builds_markdown_context(sample_project_structure):
    builder = ContextBuilder(sample_project_structure)
    context = builder.build(structure_only=True)
    assert "КОНТЕКСТ ПРОЕКТА ДЛЯ LLM" in context
    assert "src/main.py" in context
    assert "README.md" in context
    assert "image.png" not in context


def test_builder_builds_json_context(sample_project_structure):
    builder = ContextBuilder(sample_project_structure)
    context = builder.build(format="json")
    import json
    data = json.loads(context)
    assert data["project_root"] == str(sample_project_structure)
    filenames = [f["path"] for f in data["files"]]
    assert "src/main.py" in filenames


def test_builder_includes_stats(sample_project_structure):
    builder = ContextBuilder(sample_project_structure)
    context = builder.build(include_stats=True)
    assert "📊 СТАТИСТИКА" in context
    assert "Всего файлов:" in context


def test_builder_handles_read_error(tmp_path):
    # Создадим файл, который нельзя прочитать
    restricted_file = tmp_path / "secret.txt"
    restricted_file.write_text("Secret content")
    restricted_file.chmod(0o000)  # Запрещаем чтение

    builder = ContextBuilder(tmp_path)
    context = builder.build()
    assert "[ОШИБКА ЧТЕНИЯ" in context