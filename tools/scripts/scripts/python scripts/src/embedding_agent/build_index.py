#!/usr/bin/env python
import sys
from pathlib import Path

# Добавляем путь к src
sys.path.append(str(Path(__file__).parent.parent))

from src.embedding_agent.embedder import CodeEmbedder
from src.embedding_agent.indexer import CodeIndexer


def main():
    print("🚀 Начинаем индексацию кодовой базы...")

    # Инициализируем компоненты
    embedder = CodeEmbedder(model_name="nomic-embed-text")
    indexer = CodeIndexer(embedder)

    # Индексируем текущий репозиторий
    repo_path = Path(__file__).parent.parent
    print(f"📁 Репозиторий: {repo_path}")

    chunks = indexer.index_repository(repo_path, extensions=[".py", ".md"])

    print(f"\n✅ Проиндексировано {len(chunks)} чанков")

    # Сохраняем индекс
    index_file = repo_path / "data" / "embeddings" / "code_index.json"
    index_file.parent.mkdir(parents=True, exist_ok=True)
    indexer.save_index(str(index_file))

    print("\n📊 Статистика по типам чанков:")
    types = {}
    for chunk in indexer.index:
        chunk_type = chunk.get("type", "unknown")
        types[chunk_type] = types.get(chunk_type, 0) + 1

    for t, count in types.items():
        print(f"  {t}: {count}")


if __name__ == "__main__":
    main()
