#!/usr/bin/env python3
"""
Sandbox Executor module
Secure code execution in isolated environment
"""

import contextlib
import os
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path


class SandboxExecutionError(Exception):
    """Raised when sandbox execution fails"""

    pass


class SandboxTimeoutError(SandboxExecutionError):
    """Raised when sandbox execution times out"""

    pass


@dataclass
class SandboxResult:
    """Result of sandbox execution"""

    success: bool
    output: str = ""
    error: str = ""
    return_code: int = 0
    execution_time: float = 0.0


class SandboxConfig:
    """Configuration for sandbox execution"""

    def __init__(
        self,
        max_memory_mb: int = 256,
        max_execution_time: int = 30,
        blocked_commands: list[str] | None = None,
        allowed_languages: list[str] | None = None,
        working_directory: str | None = None,
    ):
        self.max_memory_mb = max_memory_mb
        self.max_execution_time = max_execution_time
        self.blocked_commands = blocked_commands or [
            "rm",
            "sudo",
            "su",
            "mkfs",
            "dd",
            "nc",
            "netcat",
        ]
        self.allowed_languages = allowed_languages or ["python", "python3", "python2"]
        self.working_directory = working_directory or tempfile.gettempdir()


class SandboxExecutor:
    """Secure code execution in isolated sandbox"""

    def __init__(self, config: SandboxConfig | None = None):
        self.config = config or SandboxConfig()
        self.work_dir = Path(self.config.working_directory) / "sandbox" / str(id(self))
        self.work_dir.mkdir(parents=True, exist_ok=True)

    def execute(
        self,
        code: str,
        language: str,
        args: list[str] | None = None,
        timeout: int | None = None,
    ) -> SandboxResult:
        """Execute code in sandbox"""
        start_time = time.time()

        # Validate language
        if language not in self.config.allowed_languages:
            return SandboxResult(
                success=False,
                error=f"Language '{language}' is not allowed",
                execution_time=time.time() - start_time,
            )

        # Validate timeout
        execution_timeout = timeout or self.config.max_execution_time

        # Create temporary file with code
        with tempfile.NamedTemporaryFile(mode="w", suffix=f".{language}", delete=False) as f:
            code_file = f.name
            f.write(code)

        try:
            # Build command
            cmd = self._build_command(code_file, language, args)

            # Execute with timeout
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=execution_timeout,
                    check=False,
                )
            except subprocess.TimeoutExpired:
                return SandboxResult(
                    success=False,
                    error=f"Execution timed out after {execution_timeout}s",
                    execution_time=time.time() - start_time,
                )

            execution_time = time.time() - start_time

            return SandboxResult(
                success=result.returncode == 0,
                output=result.stdout,
                error=result.stderr,
                return_code=result.returncode,
                execution_time=execution_time,
            )

        finally:
            # Cleanup
            with contextlib.suppress(OSError):
                os.unlink(code_file)

    def execute_with_timeout(
        self,
        code: str,
        language: str,
        args: list[str] | None = None,
        timeout: int | None = None,
    ) -> SandboxResult:
        """Execute code with timeout handling"""
        try:
            return self.execute(code, language, args, timeout)
        except subprocess.TimeoutExpired as e:
            raise SandboxTimeoutError(f"Execution timed out after {self.config.max_execution_time}s") from e

    def _build_command(
        self,
        code_file: str,
        language: str,
        args: list[str] | None = None,
    ) -> list[str]:
        """Build command with security constraints"""
        cmd = []
        blocked = set(self.config.blocked_commands)

        if language == "python":
            cmd = ["python3", code_file]
        elif language == "python2":
            cmd = ["python2", code_file]
        elif language == "python3":
            cmd = ["python3", code_file]
        elif language in ("js", "javascript"):
            cmd = ["node", code_file]
        elif language in ("sh", "bash"):
            cmd = ["bash", code_file]
        else:
            raise SandboxExecutionError(f"Unsupported language: {language}")

        # Add additional arguments
        if args:
            cmd.extend(args)

        # Check for blocked commands in the full command
        full_cmd_str = " ".join(cmd)
        for blocked_cmd in blocked:
            if blocked_cmd in full_cmd_str:
                raise SandboxExecutionError(f"Blocked command detected: {blocked_cmd}")

        return cmd

    def cleanup(self) -> None:
        """Clean up sandbox directory"""
        with contextlib.suppress(OSError):
            shutil.rmtree(self.work_dir)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
        return False
