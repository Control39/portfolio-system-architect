#!/usr/bin/env python
import json
import sys
from pathlib import Path

# Добавляем путь к src
sys.path.append(str(Path(__file__).parent.parent))

from src.embedding_agent.embedder import CodeEmbedder


def load_full_index(index_file: str):
    """Загружает полный индекс с эмбеддингами"""
    with open(index_file) as f:
        index_meta = json.load(f)

    # Здесь нужно загружать полные эмбеддинги из отдельного хранилища
    # Для демо будем переиндексировать при поиске
    return index_meta


def search_similar_code(query: str, indexer, embedder, top_k: int = 5):
    """Поиск похожего кода"""
    # Получаем эмбеддинг запроса
    query_embedding = embedder.embed(query)

    if not query_embedding:
        print("❌ Не удалось получить эмбеддинг запроса")
        return []

    # Вычисляем сходство со всеми чанками
    results = []
    for chunk in indexer.index:
        if "embedding" in chunk:
            similarity = embedder.compute_similarity(
                query_embedding, chunk["embedding"]
            )
            results.append((similarity, chunk))

    # Сортируем по убыванию сходства
    results.sort(reverse=True, key=lambda x: x[0])

    return results[:top_k]


def main():
    print("🔍 Поиск по кодовой базе с использованием семантических эмбеддингов")
    print("-" * 60)

    # Инициализируем компоненты
    embedder = CodeEmbedder(model_name="nomic-embed-text")

    # Загружаем или создаем индекс
    repo_path = Path(__file__).parent.parent
    index_file = repo_path / "data" / "embeddings" / "code_index.json"

    if not index_file.exists():
        print("❌ Индекс не найден. Сначала запустите build_index.py")
        print("   python scripts/build_index.py")
        return

    # Для демо используем простой подход - переиндексируем при поиске
    # В реальном проекте нужно сохранять эмбеддинги отдельно
    from src.embedding_agent.indexer import CodeIndexer

    indexer = CodeIndexer(embedder)

    print(
        "🔄 Переиндексация для поиска (в реальном проекте эмбеддинги будут загружаться из базы)..."
    )
    indexer.index_repository(repo_path, extensions=[".py", ".md"])

    print("\n✅ Готово к поиску!")
    print("=" * 60)

    while True:
        print("\n📝 Введите запрос (или 'exit' для выхода):")
        query = input("> ").strip()

        if query.lower() in ["exit", "quit", "q"]:
            break

        if not query:
            continue

        print("\n🔎 Ищем похожий код...")
        results = search_similar_code(query, indexer, embedder, top_k=5)

        if not results:
            print("Ничего не найдено")
            continue

        print(f"\n📊 Найдено {len(results)} результатов:")
        for i, (similarity, chunk) in enumerate(results, 1):
            print(f"\n--- Результат {i} (сходство: {similarity:.3f}) ---")
            print(f"📁 Файл: {chunk['file']}")
            print(f"📌 Тип: {chunk.get('type', 'unknown')}")
            if "name" in chunk:
                print(f"🏷️  Имя: {chunk['name']}")
            if "start_line" in chunk:
                print(f"📍 Строка: {chunk['start_line']}")
            print(f"\n📄 Содержимое:\n{chunk['content'][:300]}...")


if __name__ == "__main__":
    main()
