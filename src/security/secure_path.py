#!/usr/bin/env python3
"""
Secure Path module
Safe file path operations with security checks
"""

import re
from pathlib import Path


class PathSecurityError(Exception):
    """Raised when path operation is not secure"""

    pass


class SecurePath:
    """
    Secure path resolver with security checks

    Prevents path traversal attacks and ensures all paths
    remain within a defined base directory.

    Examples:
        >>> secure = SecurePath(Path("/home/user/project"))
        >>> safe_path = secure.resolve("subdir/file.txt")
        >>> secure.resolve("../../../etc/passwd")  # Raises PathSecurityError
    """

    # Dangerous patterns to block
    DANGEROUS_PATTERNS = [
        r"\.\./",  # Path traversal
        r"\.\.\\",  # Windows path traversal
        r"^/\.\.",  # Absolute path traversal
        r"^~",  # Home directory access
        r"^\$",  # Environment variable expansion
        r"`[^`]+`",  # Command substitution
        r"\$\([^)]+\)",  # Command substitution with $()
    ]

    # Allowed characters
    ALLOWED_CHARS = re.compile(r"^[a-zA-Z0-9_\-./\\@]+$")

    def __init__(self, base_path: str | Path, strict: bool = True):
        self.base_path = Path(base_path).resolve()
        self.strict = strict

        # Create base path if it doesn't exist
        self.base_path.mkdir(parents=True, exist_ok=True)

    def resolve(self, user_path: str | Path, strict: bool | None = None) -> Path:
        """
        Resolve a user-provided path safely

        Args:
            user_path: Path provided by user
            strict: Override strict mode

        Returns:
            Resolved path within base directory

        Raises:
            PathSecurityError: If path is not secure
        """
        if strict is None:
            strict = self.strict

        user_path_str = str(user_path)

        # Check for dangerous patterns
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, user_path_str, re.IGNORECASE):
                raise PathSecurityError(f"Path contains dangerous pattern: {pattern}")

        # Construct full path
        full_path = (self.base_path / user_path).resolve()

        # Check if path is within base
        if strict:
            try:
                full_path.relative_to(self.base_path)
            except ValueError as e:
                raise PathSecurityError(f"Path traversal detected: {user_path} -> {full_path}") from e

        # Check for symlinks pointing outside base
        if strict and self._is_symlink_outside_base(full_path):
            raise PathSecurityError(f"Symlink points outside base: {user_path}")

        return full_path

    def is_safe_path(self, user_path: str | Path) -> bool:
        """Check if a path is safe without raising exceptions"""
        try:
            self.resolve(user_path, strict=True)
            return True
        except PathSecurityError:
            return False

    def _is_symlink_outside_base(self, path: Path) -> bool:
        """Check if path or any parent is a symlink pointing outside base"""
        if not path.exists():
            return False

        # Check the path itself
        if path.is_symlink():
            resolved = path.resolve()
            try:
                resolved.relative_to(self.base_path)
            except ValueError:
                return True

        # Check all parents
        for parent in path.parents:
            if parent == self.base_path:
                break
            if parent.is_symlink():
                resolved = parent.resolve()
                try:
                    resolved.relative_to(self.base_path)
                except ValueError:
                    return True

        return False

    def join(self, *paths: str | Path) -> Path:
        """Join paths safely"""
        return self.resolve(str(Path(*paths)))

    def exists(self, user_path: str | Path) -> bool:
        """Check if a path exists (safely resolved)"""
        try:
            resolved = self.resolve(user_path)
            return resolved.exists()
        except PathSecurityError:
            return False

    def is_file(self, user_path: str | Path) -> bool:
        """Check if path is a file (safely resolved)"""
        try:
            resolved = self.resolve(user_path)
            return resolved.is_file()
        except PathSecurityError:
            return False

    def is_dir(self, user_path: str | Path) -> bool:
        """Check if path is a directory (safely resolved)"""
        try:
            resolved = self.resolve(user_path)
            return resolved.is_dir()
        except PathSecurityError:
            return False

    def safe_read(self, user_path: str | Path, encoding: str = "utf-8") -> str:
        """Read file content safely"""
        resolved = self.resolve(user_path)
        return resolved.read_text(encoding=encoding)

    def safe_write(self, user_path: str | Path, content: str, encoding: str = "utf-8") -> None:
        """Write file content safely"""
        resolved = self.resolve(user_path)
        resolved.parent.mkdir(parents=True, exist_ok=True)
        resolved.write_text(content, encoding=encoding)

    def safe_listdir(self, user_path: str | Path = ".") -> list[Path]:
        """List directory contents safely"""
        resolved = self.resolve(user_path)
        return list(resolved.iterdir())

    def safe_glob(self, pattern: str, path: str | Path = ".") -> list[Path]:
        """Glob pattern safely"""
        resolved = self.resolve(path)
        return list(resolved.glob(pattern))

    def relative_to_base(self, path: str | Path) -> Path:
        """Get path relative to base"""
        resolved = self.resolve(path)
        return resolved.relative_to(self.base_path)

    @property
    def root(self) -> Path:
        """Get the base path"""
        return self.base_path


def safe_path_join(base: str | Path, *parts: str | Path) -> Path:
    """Safely join path parts within base directory"""
    secure = SecurePath(base)
    return secure.join(*parts)


def is_path_within_base(base: str | Path, path: str | Path) -> bool:
    """Check if path is within base directory"""
    try:
        secure = SecurePath(base)
        secure.resolve(path, strict=True)
        return True
    except PathSecurityError:
        return False
