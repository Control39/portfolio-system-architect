#!/usr/bin/env python3
"""
File Type Validator module
Safe file type validation
"""

import mimetypes
import re
from dataclasses import dataclass
from pathlib import Path


class FileTypeValidationError(Exception):
    """Raised when file type validation fails"""

    pass


@dataclass
class AllowedFileTypes:
    """Configuration for allowed file types"""

    extensions: set[str]
    mime_types: set[str]
    max_size_mb: float = 100.0
    require_extension: bool = True


class FileTypeValidator:
    """
    Validate file types for security

    Prevents dangerous file uploads and ensures
    only allowed file types are processed.

    Examples:
        >>> validator = FileTypeValidator(allowed_extensions={".py", ".txt"})
        >>> validator.validate(Path("script.py"))
    """

    # Dangerous file types
    DANGEROUS_EXTENSIONS: set[str] = {
        ".exe",
        ".dll",
        ".so",
        ".dylib",  # Executables
        ".bat",
        ".cmd",
        ".sh",
        ".bash",  # Shell scripts
        ".ps1",
        ".psm1",  # PowerShell
        ".scr",
        ".pif",
        ".com",  # Windows executables
        ".vbs",
        ".vbe",
        ".js",
        ".jse",  # Scripts
        ".wsf",
        ".wsh",
        ".vxd",  # Windows scripts
        ".cpl",
        ".msi",
        ".msp",  # Windows installers
        ".hta",
        ".html",  # HTML/HTA
        ".jar",
        ".war",
        ".ear",  # Java archives
        ".apk",
        ".ipa",  # Mobile packages
        ".iso",
        ".img",  # Disk images
        ".deb",
        ".rpm",
        ".pkg",  # Package managers
        ".reg",  # Registry files
        ".inf",  # Setup info
        ".ade",
        ".adp",
        ".as",
        ".asp",  # Active files
        ".bas",
        ".c",
        ".cc",
        ".cgi",  # Source files
        ".cfm",
        ".cfmx",  # ColdFusion
        ".doc",
        ".docx",
        ".xls",
        ".xlsx",
        ".ppt",
        ".pptx",  # Office (potential macros)
        ".pub",
        ".mdb",
        ".accdb",  # Database
        ".sqlite",
        ".db",
        ".sql",  # Database files
        ".dmg",  # Disk images
    }

    # Dangerous MIME types
    DANGEROUS_MIME_TYPES: set[str] = {
        "application/x-executable",
        "application/x-dosexec",
        "application/x-msdownload",
        "application/x-sh",
        "application/x-perl",
        "application/x-php",
        "application/x-ruby",
        "application/x-python",
        "text/x-shellscript",
        "application/javascript",
        "application/x-javascript",
        "application/x-web-config",
        "application/x-httpd-php",
    }

    def __init__(
        self,
        allowed_extensions: set[str] | None = None,
        allowed_mime_types: set[str] | None = None,
        max_size_mb: float = 100.0,
        strict_mode: bool = True,
    ):
        self.allowed_extensions = allowed_extensions or {".txt", ".md", ".py", ".js", ".css", ".html"}
        self.allowed_mime_types = allowed_mime_types or {
            "text/plain",
            "text/markdown",
            "text/x-python",
            "text/javascript",
            "text/css",
            "text/html",
            "application/json",
            "application/xml",
            "application/yaml",
            "application/x-yaml",
            "image/png",
            "image/jpeg",
            "image/gif",
            "image/webp",
            "application/pdf",
        }
        self.max_size_mb = max_size_mb
        self.strict_mode = strict_mode

    def validate(self, file_path: Path) -> bool:
        """
        Validate a file for security

        Args:
            file_path: Path to file to validate

        Returns:
            True if file is safe

        Raises:
            FileTypeValidationError: If validation fails
        """
        # Check file exists
        if not file_path.exists():
            raise FileTypeValidationError(f"File does not exist: {file_path}")

        # Check file size
        self._check_size(file_path)

        # Check extension
        self._check_extension(file_path)

        # Check MIME type
        self._check_mime_type(file_path)

        # Check content for dangerous patterns
        self._check_content(file_path)

        return True

    def _check_size(self, file_path: Path) -> None:
        """Check file size is within limits"""
        size_mb = file_path.stat().st_size / (1024 * 1024)

        if size_mb > self.max_size_mb:
            raise FileTypeValidationError(f"File too large: {size_mb:.2f}MB > {self.max_size_mb}MB")

    def _check_extension(self, file_path: Path) -> None:
        """Check file extension is allowed"""
        ext = file_path.suffix.lower()

        if self.strict_mode and ext not in self.allowed_extensions:
            raise FileTypeValidationError(
                f"Disallowed file extension: {ext}. " f"Allowed: {', '.join(sorted(self.allowed_extensions))}"
            )

        # Always block dangerous extensions
        if ext in self.DANGEROUS_EXTENSIONS:
            raise FileTypeValidationError(f"Dangerous file extension: {ext}")

    def _check_mime_type(self, file_path: Path) -> None:
        """Check MIME type is allowed"""
        mime_type, _ = mimetypes.guess_type(str(file_path))

        if mime_type and mime_type in self.DANGEROUS_MIME_TYPES:
            raise FileTypeValidationError(f"Dangerous MIME type: {mime_type}")

        if self.strict_mode and mime_type not in self.allowed_mime_types and not self._is_unknown_allowed(file_path):
            raise FileTypeValidationError(f"Unknown or disallowed MIME type: {mime_type}")

    def _is_unknown_allowed(self, file_path: Path) -> bool:
        """Check if unknown MIME type is allowed based on extension"""
        ext = file_path.suffix.lower()

        # If extension is in allowed list, allow unknown MIME type
        return ext in self.allowed_extensions

    def _check_content(self, file_path: Path) -> None:
        """Check file content for dangerous patterns"""
        # Only check text files
        mime_type, _ = mimetypes.guess_type(str(file_path))

        # Skip non-text files
        if mime_type is None or not mime_type.startswith("text"):
            return

        # Read file content
        try:
            content = file_path.read_text(errors="ignore")
        except UnicodeDecodeError:
            # Binary file, skip content check
            return

        # Check for dangerous patterns
        self._check_for_executables(content, file_path)
        self._check_for_scripts(content, file_path)

    def _check_for_executables(self, content: str, file_path: Path) -> None:
        """Check for executable patterns in content"""
        dangerous_patterns = [
            r"eval\s*\(",  # eval()
            r"exec\s*\(",  # exec()
            r"os\.system\s*\(",  # os.system()
            r"subprocess\.",  # subprocess module
            r"__import__\s*\(",  # __import__()
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, content):
                raise FileTypeValidationError(f"Dangerous pattern found in {file_path.name}: {pattern}")

    def _check_for_scripts(self, content: str, file_path: Path) -> None:
        """Check for script patterns in content"""
        # Check for shebang
        if content.startswith("#!"):
            shebang = content.split("\n")[0].lower()

            if any(s in shebang for s in ["/bin/bash", "/bin/sh", "/usr/bin/env"]):
                raise FileTypeValidationError(f"Script file detected (shebang): {file_path.name}")

    def is_file_safe(self, file_path: Path) -> bool:
        """Check if file is safe without raising exceptions"""
        try:
            self.validate(file_path)
            return True
        except FileTypeValidationError:
            return False

    def get_allowed_extensions(self) -> list[str]:
        """Get list of allowed extensions"""
        return sorted(list(self.allowed_extensions))

    def get_dangerous_extensions(self) -> list[str]:
        """Get list of dangerous extensions"""
        return sorted(list(self.DANGEROUS_EXTENSIONS))
