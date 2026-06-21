"""Test fallback mode fix for ChromaDocumentIndexer."""

import sys

sys.path.insert(0, "apps/embedding_agent")

from chroma_indexer import CHROMA_AVAILABLE, ChromaDocumentIndexer

print(f"CHROMA_AVAILABLE: {CHROMA_AVAILABLE}")

# Создаем индексатор без chromadb (fallback mode)
indexer = ChromaDocumentIndexer(persist_directory="test_fallback")

# Проверяем, что self.store не None
print(f"self.store: {indexer.store}")
print(f"self.collection (property): {indexer.collection}")

# Проверяем, что можно вызвать add
try:
    doc_id = indexer.add_document("test text")
    print(f"SUCCESS: add_document worked, doc_id={doc_id}")
except AttributeError as e:
    print(f"FAILED: {e}")

# Проверяем search
try:
    results = indexer.search("test")
    print(f"SUCCESS: search worked, results={len(results)}")
except AttributeError as e:
    print(f"FAILED: {e}")

print("FALLBACK MODE TEST COMPLETED")
