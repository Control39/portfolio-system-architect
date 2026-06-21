"""
File utilities for Cognitive Agent
"""

import hashlib
import json
import logging
from pathlib import Path
from typing import Any


def calculate_file_hash(file_path: Path) -> str:
    """
    Calculate SHA256 hash of a file to detect changes.

    Args:
        file_path: Path to the file

    Returns:
        Hexadecimal string of the file hash
    """
    hash_sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()


def load_json_file(file_path: Path) -> dict[str, Any] | None:
    """
    Load a JSON file with error handling.

    Args:
        file_path: Path to the JSON file

    Returns:
        Dictionary with JSON data or None if error occurred
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logging.warning(f"File {file_path} not found")
        return None
    except json.JSONDecodeError as e:
        logging.error(f"JSON parsing error in {file_path}: {e}")
        return None


def find_files_by_extension(directory: Path, extensions: list[str]) -> list[Path]:
    """
    Find files with specified extensions in a directory recursively.

    Args:
        directory: Root directory to search in
        extensions: List of extensions (with or without dot, e.g., ['.py', 'txt'])

    Returns:
        List of Path objects matching the extensions
    """
    files = []
    for ext in extensions:
        # Normalize extension: remove leading dot if present
        normalized_ext = ext.lstrip(".")
        files.extend(directory.rglob(f"*.{normalized_ext}"))
    return files
