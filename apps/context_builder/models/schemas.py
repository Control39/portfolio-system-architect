from pydantic import BaseModel, Field
from typing import List, Optional, Literal


class BuildContextRequest(BaseModel):
    """Запрос на сборку контекста"""

    paths: List[str] = Field(default=["./"], description="Пути для сканирования")
    structure_only: bool = Field(default=False, description="Только структура")
    include_stats: bool = Field(default=True, description="Включить статистику")
    format: Literal["markdown", "plain", "json"] = Field(default="markdown")

    # Динамические фильтры
    extensions: Optional[List[str]] = Field(default=None, description="Доп. расширения")
    exclude_dirs: Optional[List[str]] = Field(
        default=None, description="Доп. исключаемые директории"
    )
    max_file_size_mb: Optional[int] = Field(default=None, description="Макс. размер файла")


class BuildContextResponse(BaseModel):
    """Ответ на сборку контекста"""

    success: bool
    context: Optional[str] = None
    error: Optional[str] = None
    stats: Optional[dict] = None
    file_path: Optional[str] = None


class FilterConfigRequest(BaseModel):
    """Запрос на изменение фильтров"""

    add_extensions: Optional[List[str]] = None
    remove_extensions: Optional[List[str]] = None
    add_exclude_dirs: Optional[List[str]] = None
    remove_exclude_dirs: Optional[List[str]] = None


class FilterConfigResponse(BaseModel):
    """Ответ с текущими фильтрами"""

    extensions: List[str]
    excluded_dirs: List[str]
    excluded_files: List[str]
    max_file_size_mb: int
