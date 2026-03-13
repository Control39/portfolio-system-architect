import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.embedding_agent.embedder import CodeEmbedder

def test_embedder():
    """Тестирование работы эмбеддера"""
    embedder = CodeEmbedder()
    
    test_cases = [
        ("def hello(): print('world')", "простая функция"),
        ("class Test: pass", "простой класс"),
        ("import numpy as np", "импорт библиотеки")
    ]
    
    print("Тестирование эмбеддера...")
    for code, description in test_cases:
        embedding = embedder.embed(code)
        assert embedding, f"Не удалось получить эмбеддинг для {description}"
        assert len(embedding) > 0, f"Пустой эмбеддинг для {description}"
        print(f"✅ {description}: {len(embedding)} размер")
    
    print("🎉 Все тесты пройдены!")

if __name__ == "__main__":
    test_embedder()