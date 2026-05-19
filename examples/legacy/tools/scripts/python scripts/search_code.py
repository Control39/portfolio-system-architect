import json

import requests
from sklearn.metrics.pairwise import cosine_similarity


def get_embedding(text):
    response = requests.post(
        "http://localhost:11434/api/embeddings",
        json={
            "model": "nomic-embed-text",
            "prompt": text,
        },
    )
    return response.json()["embedding"]


def search_code(query, index_file="code_index.json"):
    # Загружаем индекс
    with open(index_file) as f:
        index_data = json.load(f)

    # Получаем эмбеддинг запроса
    query_embedding = get_embedding(query)

    # Ищем похожие
    results = []
    for item in index_data:
        # В реальном проекте здесь нужно загружать полные эмбеддинги
        # Для примера просто считаем, что они сохранены
        if "embedding" in item:
            sim = cosine_similarity(
                [query_embedding],
                [item["embedding"]],
            )[0][0]
            results.append((sim, item["file"], item["content_preview"]))

    # Сортируем по релевантности
    results.sort(reverse=True)

    for sim, file, preview in results[:5]:
        print(f"\n📁 {file} (сходство: {sim:.2f})")
        print(f"📝 {preview}...")


if __name__ == "__main__":
    query = input("Что ищем в коде? ")
    search_code(query)
