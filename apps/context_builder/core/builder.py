from pathlib import Path
from typing import List, Optional
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape
import json

from .scanner import ProjectScanner, FileInfo
from .token_counter import TokenCounter
from .chunker import ContextChunker
from ..config.settings import settings


class ContextBuilder:
    """Сборщик контекста"""

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root).resolve()
        self.scanner = ProjectScanner(
            self.project_root, respect_gitignore=settings.respect_gitignore
        )
        self.token_counter = TokenCounter(model=settings.tokenizer_model)

        # Jinja2 шаблон
        template_dir = Path(__file__).parent.parent / "templates"
        self.env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def build(
        self,
        subpath: Optional[str] = None,
        structure_only: bool = False,
        include_stats: bool = True,
        format: str = "markdown",
    ) -> str:
        """Собрать контекст"""

        files = list(self.scanner.scan(subpath))

        if format == "json":
            return self._build_json(files, structure_only)

        template = self.env.get_template("context_template.j2")

        total_size = sum(f.size for f in files)
        total_lines = sum(f.lines for f in files)
        token_stats = self.token_counter.estimate_for_text("\n".join([f.rel_path for f in files]))

        # Загружаем содержимое файлов (если нужно)
        files_with_content = []
        for file_info in files:
            if not structure_only:
                try:
                    with open(file_info.path, "r", encoding="utf-8") as f:
                        file_info.content = f.read()
                    files_with_content.append((file_info.rel_path, file_info.content))
                except Exception as e:
                    file_info.content = f"[ОШИБКА ЧТЕНИЯ: {e}]"
                    files_with_content.append((file_info.rel_path, file_info.content))

        context = {
            "generated_at": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "subpath": subpath,
            "structure_only": structure_only,
            "files": files,
            "stats": {
                "total_files": len(files),
                "total_size_mb": total_size / (1024 * 1024),
                "total_lines": total_lines,
                "extensions": self._count_extensions(files),
                "tokens": token_stats,
            }
            if include_stats
            else None,
        }

        return template.render(**context)

    def build_chunked(self, subpath: Optional[str] = None) -> List[dict]:
        """Собрать контекст с разбиением на части"""

        if not settings.enable_chunking:
            return []

        files = list(self.scanner.scan(subpath))

        # Загружаем содержимое всех файлов
        files_with_content = []
        for file_info in files:
            try:
                with open(file_info.path, "r", encoding="utf-8") as f:
                    content = f.read()
                files_with_content.append((file_info.rel_path, content))
            except Exception as e:
                files_with_content.append((file_info.rel_path, f"[ОШИБКА: {e}]"))

        # Разбиваем на части
        chunker = ContextChunker(max_tokens_per_chunk=settings.max_tokens_per_chunk)
        chunks = []

        for chunk in chunker.split(files_with_content):
            header = chunker.get_chunk_header(chunk)
            chunks.append(
                {
                    "index": chunk.index,
                    "total": chunk.total,
                    "content": header + chunk.content,
                    "files": chunk.files,
                    "tokens": chunk.tokens,
                    "size_mb": chunk.size_mb,
                }
            )

        return chunks

    def _build_json(self, files: List[FileInfo], structure_only: bool) -> str:
        """JSON формат"""
        result = {
            "generated_at": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "structure_only": structure_only,
            "total_files": len(files),
            "files": [],
        }

        for f in files:
            file_data = {
                "path": f.rel_path,
                "size": f.size,
                "lines": f.lines,
                "extension": f.extension,
                "modified": f.modified.isoformat(),
            }

            if not structure_only and hasattr(f, "content") and f.content:
                file_data["content"] = f.content

            result["files"].append(file_data)

        return json.dumps(result, indent=2, ensure_ascii=False)

    def _count_extensions(self, files: List[FileInfo]) -> dict:
        """Подсчёт расширений"""
        counts = {}
        for f in files:
            ext = f.extension or "no_extension"
            counts[ext] = counts.get(ext, 0) + 1
        return counts
