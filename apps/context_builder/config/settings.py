from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List
from pathlib import Path


class Settings(BaseSettings):
    """Настройки микросервиса context_builder"""

    # Сервис
    service_name: str = "context_builder"
    service_port: int = Field(default=8600, env="CONTEXT_BUILDER_PORT")
    debug: bool = Field(default=False, env="DEBUG")

    # Пути
    project_root: Path = Field(default=Path("/app"), env="PROJECT_ROOT")
    output_dir: Path = Field(default=Path("/tmp/contexts"), env="OUTPUT_DIR")

    # Настройки сканирования
    max_file_size_mb: int = Field(default=2, env="MAX_FILE_SIZE_MB")
    max_total_size_mb: int = Field(default=10, env="MAX_TOTAL_SIZE_MB")
    max_files: int = Field(default=500, env="MAX_FILES")

    # Настройки chunking
    enable_chunking: bool = Field(default=False, env="ENABLE_CHUNKING")
    max_tokens_per_chunk: int = Field(default=100000, env="MAX_TOKENS_PER_CHUNK")
    respect_gitignore: bool = Field(default=True, env="RESPECT_GITIGNORE")
    detect_binary: bool = Field(default=True, env="DETECT_BINARY")
    tokenizer_model: str = Field(default="deepseek", env="TOKENIZER_MODEL")

    # Rate limiting
    rate_limit_enabled: bool = Field(default=True, env="RATE_LIMIT_ENABLED")
    rate_limit_requests: int = Field(default=10, env="RATE_LIMIT_REQUESTS")
    rate_limit_period_seconds: int = Field(default=60, env="RATE_LIMIT_PERIOD_SECONDS")

    # Расширения по умолчанию
    default_extensions: List[str] = Field(
        default=[
            ".py",
            ".md",
            ".yaml",
            ".yml",
            ".json",
            ".txt",
            ".env",
            ".sh",
            ".sql",
            ".html",
            ".css",
            ".js",
            ".ts",
            ".vue",
            ".j2",
        ]
    )

    # Исключаемые директории
    excluded_dirs: List[str] = Field(
        default=[
            ".git",
            ".venv",
            "__pycache__",
            "node_modules",
            ".pytest_cache",
            ".mypy_cache",
            ".ruff_cache",
            "logs",
            "data",
            "backups",
            "old",
            ".idea",
            ".vscode",
            "dist",
            "build",
        ]
    )

    # Исключаемые файлы
    excluded_files: List[str] = Field(
        default=[".DS_Store", "Thumbs.db", ".env.local", "*.pyc", "*.pyo"]
    )

    class Config:
        extra = 'ignore'
        env_file = ".env"
        env_prefix = "CONTEXT_BUILDER_"


settings = Settings()

# Создаём директорию для выходных файлов
settings.output_dir.mkdir(parents=True, exist_ok=True)
