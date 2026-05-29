# apps/context_builder/tests/conftest.py
import pytest
from pathlib import Path
import tempfile
import shutil
import os

from apps.context_builder.config.settings import settings


@pytest.fixture(scope="session")
def test_dir():
    """Временная директория для тестов."""
    tmp_dir = Path(tempfile.mkdtemp(prefix="context_builder_test_"))
    yield tmp_dir
    shutil.rmtree(tmp_dir, ignore_errors=True)


@pytest.fixture(autouse=True)
def setup_test_env(test_dir):
    """Настройка окружения для тестов."""
    # Перенастраиваем пути
    settings.project_root = test_dir
    settings.output_dir = test_dir / "output"
    settings.output_dir.mkdir(exist_ok=True)
    os.chdir(test_dir)


@pytest.fixture
def sample_project_structure(test_dir):
    """Создаёт типичную структуру проекта."""
    (test_dir / "src" / "app").mkdir(parents=True)
    (test_dir / "docs").mkdir()
    (test_dir / ".git").mkdir()

    # Текстовые файлы
    (test_dir / "src" / "main.py").write_text('print("Hello")\n', encoding="utf-8")
    (test_dir / "README.md").write_text("# Project\n", encoding="utf-8")

    # Бинарный файл
    (test_dir / "image.png").write_bytes(b'\x89PNG\r\n\x1a\n' + b'\x00' * 100)

    # .gitignore
    (test_dir / ".gitignore").write_text("*.log\n__pycache__/\n", encoding="utf-8")

    # Лог-файл (будет проигнорирован)
    (test_dir / "app.log").write_text("error: something went wrong\n")

    return test_dir