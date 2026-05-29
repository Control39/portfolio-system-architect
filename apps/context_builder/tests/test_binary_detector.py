# apps/context_builder/tests/test_binary_detector.py
from pathlib import Path
import pytest

from apps.context_builder.core.binary_detector import is_binary_file


def test_text_file_is_not_binary(tmp_path):
    file = tmp_path / "text.txt"
    file.write_text("Hello, this is a text file.", encoding="utf-8")
    assert is_binary_file(file) is False


def test_binary_file_with_null_bytes(tmp_path):
    file = tmp_path / "binary.dat"
    file.write_bytes(b"Hello\x00World")
    assert is_binary_file(file) is True


def test_png_file_is_binary(tmp_path):
    file = tmp_path / "image.png"
    file.write_bytes(b'\x89PNG\r\n\x1a\n' + b'\x00' * 50)
    assert is_binary_file(file) is True


def test_pdf_file_is_binary(tmp_path):
    file = tmp_path / "doc.pdf"
    file.write_bytes(b'%PDF-1.4' + b'\x00' * 100)
    assert is_binary_file(file) is True


def test_nonexistent_file():
    assert is_binary_file(Path("/does/not/exist")) is True