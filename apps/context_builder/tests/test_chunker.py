# apps/context_builder/tests/test_chunker.py
from apps.context_builder.core.chunker import ContextChunker, Chunk


def test_chunker_splits_large_content():
    chunker = ContextChunker(max_tokens_per_chunk=10)
    files = [
        ("file1.txt", "word " * 20),
        ("file2.txt", "hello world"),
    ]
    chunks = list(chunker.split(files))
    assert len(chunks) >= 1
    for chunk in chunks:
        assert isinstance(chunk, Chunk)
        assert chunk.tokens <= 10
        assert chunk.index >= 1


def test_chunker_preserves_file_boundaries():
    chunker = ContextChunker(max_tokens_per_chunk=1000)
    files = [(f"file{i}.txt", "content " * 5) for i in range(3)]
    chunks = list(chunker.split(files))
    assert len(chunks) == 1
    assert chunks[0].total == 1


def test_chunk_header_format():
    chunker = ContextChunker(max_tokens_per_chunk=1000)
    chunk = Chunk(
        index=1,
        total=3,
        content="...",
        files=["a.py", "b.py"],
        tokens=150,
        size_mb=0.1
    )
    header = chunker.get_chunk_header(chunk)
    assert "ЧАСТЬ 1 ИЗ 3" in header
    assert "- a.py" in header
    assert "- b.py" in header