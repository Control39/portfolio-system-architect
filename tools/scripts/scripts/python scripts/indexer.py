import ast
import json
from pathlib import Path
from typing import Any

from .embedder import CodeEmbedder


class CodeIndexer:
    def __init__(self, embedder: CodeEmbedder, chunk_size: int = 1000):
        self.embedder = embedder
        self.chunk_size = chunk_size
        self.index = []

    def chunk_python_file(self, file_path: Path) -> list[dict[str, Any]]:
        """Разбивает Python файл на логические блоки"""
        chunks = []

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Пробуем разобрать AST
            try:
                tree = ast.parse(content)

                # Собираем функции
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        chunk = ast.unparse(node)
                        if len(chunk) <= self.chunk_size:
                            chunks.append({
                                "content": chunk,
                                "type": "function",
                                "name": node.name,
                                "file": str(file_path),
                                "start_line": node.lineno,
                            })

                    elif isinstance(node, ast.ClassDef):
                        chunk = ast.unparse(node)
                        if len(chunk) <= self.chunk_size:
                            chunks.append({
                                "content": chunk,
                                "type": "class",
                                "name": node.name,
                                "file": str(file_path),
                                "start_line": node.lineno,
                            })

            except SyntaxError:
                # Если AST не работает, разбиваем по строкам
                lines = content.split("\n")
                current_chunk = []
                current_size = 0

                for i, line in enumerate(lines):
                    if current_size + len(line) > self.chunk_size and current_chunk:
                        chunks.append({
                            "content": "\n".join(current_chunk),
                            "type": "lines",
                            "file": str(file_path),
                            "start_line": i - len(current_chunk) + 1,
                        })
                        current_chunk = [line]
                        current_size = len(line)
                    else:
                        current_chunk.append(line)
                        current_size += len(line)

                if current_chunk:
                    chunks.append({
                        "content": "\n".join(current_chunk),
                        "type": "lines",
                        "file": str(file_path),
                        "start_line": len(lines) - len(current_chunk) + 1,
                    })

            # Если нет чанков, берем весь файл
            if not chunks and len(content) <= self.chunk_size:
                chunks.append({
                    "content": content,
                    "type": "module",
                    "name": file_path.stem,
                    "file": str(file_path),
                    "start_line": 1,
                })

        except Exception as e:
            print(f"Ошибка при обработке {file_path}: {e}")

        return chunks

    def index_repository(self, repo_path: str, extensions: list[str] = [".py"]) -> list[dict[str, Any]]:
        """Индексирует весь репозиторий"""
        repo_path = Path(repo_path)
        all_chunks = []

        # Игнорируемые директории
        ignore_dirs = {".git", "__pycache__", "venv", "env", "node_modules", "data", "embeddings"}

        for ext in extensions:
            for file_path in repo_path.rglob(f"*{ext}"):
                # Проверяем, не в игнорируемой ли директории
                if any(part in ignore_dirs for part in file_path.parts):
                    continue

                print(f"Обработка: {file_path}")
                chunks = self.chunk_python_file(file_path)

                for chunk in chunks:
                    # Получаем эмбеддинг
                    embedding = self.embedder.embed(chunk["content"])
                    if embedding:
                        chunk["embedding"] = embedding
                        all_chunks.append(chunk)

        self.index = all_chunks
        return all_chunks

    def save_index(self, file_path: str):
        """Сохраняет индекс в JSON файл"""
        index_to_save = []
        for item in self.index:
            item_copy = item.copy()
            if "embedding" in item_copy:
                item_copy["embedding_shape"] = len(item_copy["embedding"])
                item_copy["embedding_sample"] = item_copy["embedding"][:5]
                del item_copy["embedding"]
            index_to_save.append(item_copy)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(index_to_save, f, indent=2, ensure_ascii=False)

        print(f"Индекс сохранен в {file_path}")
        print(f"Всего чанков: {len(self.index)}")

