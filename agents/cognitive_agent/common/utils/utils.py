"""
Utils adapter for Cognitive Agent
Provides backward compatibility for the old utils.py interface
"""

from .file_utils import calculate_file_hash, find_files_by_extension, load_json_file
from .format_utils import format_bytes

__all__ = ["calculate_file_hash", "load_json_file", "find_files_by_extension", "format_bytes"]
