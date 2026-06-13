from collections.abc import Generator
from dataclasses import dataclass

from .token_counter import TokenCounter


@dataclass
class Chunk:
    """Часть контекста"""

    index: int
    total: int
    content: str
    files: list[str]
    tokens: int
    size_mb: float


class ContextChunker:
    """Разбивает большой контекст на части"""

    def __init__(self, max_tokens_per_chunk: int = 100000):
        self.max_tokens = max_tokens_per_chunk
        self.token_counter = TokenCounter()

    def split(self, files_with_content: list[tuple[str, str]]) -> Generator[Chunk, None, None]:
        """
        Разбивает контекст на части по границам файлов.
        """
        chunks = []
        current_chunk_files = []
        current_content = []
        current_tokens = 0

        for file_path, content in files_with_content:
            file_header = f"\n{'=' * 80}\nФАЙЛ: {file_path}\n{'=' * 80}\n"
            file_full = file_header + content
            file_tokens = self.token_counter.count(file_full)

            # Если один файл больше chunk'а — пропускаем с предупреждением
            if file_tokens > self.max_tokens:
                print(f"⚠️ Файл слишком большой: {file_path} ({file_tokens} токенов)")
                continue

            # Если текущий chunk переполнится — отдаём его
            if current_tokens + file_tokens > self.max_tokens and current_chunk_files:
                yield Chunk(
                    index=len(chunks) + 1,
                    total=0,
                    content="".join(current_content),
                    files=current_chunk_files.copy(),
                    tokens=current_tokens,
                    size_mb=len("".join(current_content)) / (1024 * 1024),
                )
                chunks.append(
                    {
                        "files": current_chunk_files.copy(),
                        "content": "".join(current_content),
                        "tokens": current_tokens,
                    }
                )
                current_chunk_files = []
                current_content = []
                current_tokens = 0

            current_chunk_files.append(file_path)
            current_content.append(file_full)
            current_tokens += file_tokens

        # Последний chunk
        if current_chunk_files:
            chunks.append(
                {
                    "files": current_chunk_files,
                    "content": "".join(current_content),
                    "tokens": current_tokens,
                }
            )

        # Заполняем total
        total = len(chunks)
        for i, chunk_data in enumerate(chunks):
            yield Chunk(
                index=i + 1,
                total=total,
                content=chunk_data["content"],
                files=chunk_data["files"],
                tokens=chunk_data["tokens"],
                size_mb=len(chunk_data["content"]) / (1024 * 1024),
            )

    def get_chunk_header(self, chunk: Chunk) -> str:
        """Возвращает заголовок для LLM"""
        files_list = "\n".join(f"  - {f}" for f in chunk.files)
        return f"""
{"=" * 80}
⚠️ ЧАСТЬ {chunk.index} ИЗ {chunk.total} ⚠️
{"=" * 80}
Контекст проекта разбит на {chunk.total} части.

Файлы в этой части ({len(chunk.files)} шт.):
{files_list}

{"=" * 80}
"""
