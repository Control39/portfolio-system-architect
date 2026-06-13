from typing import Literal

from pydantic import BaseModel, Field


class BuildContextRequest(BaseModel):
    """Запрос на сборку контекста"""

    paths: list[str] = Field(default=["./"], description="Пути для сканирования")
    structure_only: bool = Field(default=False, description="Только структура")
    include_stats: bool = Field(default=True, description="Включить статистику")
    format: Literal["markdown", "plain", "json"] = Field(default="markdown")

    # Динамические фильтры
    extensions: list[str] | None = Field(default=None, description="Доп. расширения")
    exclude_dirs: list[str] | None = Field(default=None, description="Доп. исключаемые директории")
    max_file_size_mb: int | None = Field(default=None, description="Макс. размер файла")


class BuildContextResponse(BaseModel):
    """Ответ на сборку контекста"""

    success: bool
    context: str | None = None
    error: str | None = None
    stats: dict | None = None
    file_path: str | None = None


class FilterConfigRequest(BaseModel):
    """Запрос на изменение фильтров"""

    add_extensions: list[str] | None = None
    remove_extensions: list[str] | None = None
    add_exclude_dirs: list[str] | None = None
    remove_exclude_dirs: list[str] | None = None


class FilterConfigResponse(BaseModel):
    """Ответ с текущими фильтрами"""

    extensions: list[str]
    excluded_dirs: list[str]
    excluded_files: list[str]
    max_file_size_mb: int
