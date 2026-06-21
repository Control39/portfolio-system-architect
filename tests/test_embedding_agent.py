#!/usr/bin/env python3
"""
Тесты для Embedding Agent
"""

import os
import tempfile
import unittest
from unittest.mock import patch

from apps.embedding_agent.embedder import ChromaDocumentIndexer
from apps.embedding_agent.indexer import DocumentIndexer
from src.vector_store.embedder import DocumentEmbedder


class TestDocumentEmbedder(unittest.TestCase):
    """Тесты для DocumentEmbedder"""

    def setUp(self):
        """Настройка теста"""
        self.embedder = DocumentEmbedder(model_name="all-MiniLM-L6-v2")

    def test_embed_single_text(self):
        """Тест встраивания одного текста"""
        text = "Hello world"
        embedding = self.embedder.embed(text)
        self.assertIsInstance(embedding, list)
        self.assertGreater(len(embedding), 0)

    def test_embed_empty_text(self):
        """Тест встраивания пустого текста"""
        embedding = self.embedder.embed("")
        self.assertEqual(embedding, [])

        embedding = self.embedder.embed("   ")
        self.assertEqual(embedding, [])

    def test_embed_batch(self):
        """Тест встраивания батча текстов"""
        texts = ["Hello", "World", "Test"]
        embeddings = self.embedder.embed_batch(texts)
        self.assertIsInstance(embeddings, list)
        self.assertEqual(len(embeddings), 3)
        for emb in embeddings:
            self.assertIsInstance(emb, list)
            self.assertGreater(len(emb), 0)

    def test_compute_similarity(self):
        """Тест вычисления схожести"""
        emb1 = [1.0, 0.0, 0.0]
        emb2 = [0.0, 1.0, 0.0]
        similarity = self.embedder.compute_similarity(emb1, emb2)
        self.assertIsInstance(similarity, float)
        self.assertGreaterEqual(similarity, 0.0)
        self.assertLessEqual(similarity, 1.0)

    def test_compute_similarity_empty(self):
        """Тест вычисления схожести с пустыми векторами"""
        similarity = self.embedder.compute_similarity([], [])
        self.assertEqual(similarity, 0.0)

    def test_get_sentence_embedding_dimension(self):
        """Тест получения размерности вектора"""
        dim = self.embedder.get_sentence_embedding_dimension()
        self.assertIsInstance(dim, int)
        self.assertGreater(dim, 0)


class TestDocumentIndexer(unittest.TestCase):
    """Тесты для DocumentIndexer"""

    def setUp(self):
        """Настройка теста"""
        self.embedder = DocumentEmbedder(model_name="all-MiniLM-L6-v2")
        self.indexer = DocumentIndexer(embedder=self.embedder)

    def test_add_document(self):
        """Тест добавления документа"""
        doc_id = self.indexer.add_document("Test document content")
        self.assertGreaterEqual(doc_id, 0)
        self.assertEqual(len(self.indexer.documents), 1)
        self.assertEqual(len(self.indexer.embeddings), 1)

    def test_add_document_empty(self):
        """Тест добавления пустого документа"""
        doc_id = self.indexer.add_document("")
        self.assertEqual(doc_id, -1)

    def test_add_document_with_metadata(self):
        """Тест добавления документа с метаданными"""
        metadata = {"source": "test", "author": "test"}
        doc_id = self.indexer.add_document("Test content", metadata=metadata)
        self.assertGreaterEqual(doc_id, 0)
        self.assertEqual(self.indexer.documents[0]["metadata"], metadata)

    def test_search(self):
        """Тест поиска документов"""
        # Добавляем несколько документов
        self.indexer.add_document("Machine learning algorithms")
        self.indexer.add_document("Deep neural networks")
        self.indexer.add_document("Data science techniques")

        # Выполняем поиск
        results = self.indexer.search("neural networks", top_k=2)
        self.assertIsInstance(results, list)
        self.assertLessEqual(len(results), 2)

        if results:
            result = results[0]
            self.assertIn("text", result)
            self.assertIn("score", result)
            self.assertIn("rank", result)

    def test_search_empty_index(self):
        """Тест поиска в пустом индексе"""
        results = self.indexer.search("test query")
        self.assertEqual(results, [])

    def test_chunk_text(self):
        """Тест разделения текста на части"""
        long_text = "This is a very long text. " * 50  # Create a long text
        chunks = DocumentIndexer._chunk_text(long_text, max_chunk_size=50)
        self.assertIsInstance(chunks, list)
        self.assertGreater(len(chunks), 0)
        for chunk in chunks:
            self.assertLessEqual(len(chunk), 100)  # Allow some buffer

    def test_get_stats(self):
        """Тест получения статистики"""
        stats = self.indexer.get_stats()
        self.assertIsInstance(stats, dict)
        self.assertIn("total_documents", stats)
        self.assertIn("total_embeddings", stats)
        self.assertIn("model_name", stats)
        self.assertEqual(stats["total_documents"], 0)

    def test_clear_index(self):
        """Тест очистки индекса"""
        self.indexer.add_document("Test document")
        self.indexer.clear()
        stats = self.indexer.get_stats()
        self.assertEqual(stats["total_documents"], 0)

    def test_save_and_load(self):
        """Тест сохранения и загрузки индекса"""
        with tempfile.NamedTemporaryFile(suffix=".pkl", delete=False) as tmp_file:
            temp_path = tmp_file.name

        try:
            # Добавляем документы
            self.indexer.add_document("Test document 1", metadata={"source": "test1"})
            self.indexer.add_document("Test document 2", metadata={"source": "test2"})

            # Сохраняем
            self.indexer.save(temp_path)

            # Создаем новый индекс и загружаем
            new_indexer = DocumentIndexer(embedder=self.embedder)
            new_indexer.load(temp_path)

            # Проверяем, что документы загрузились
            stats = new_indexer.get_stats()
            self.assertEqual(stats["total_documents"], 2)
        finally:
            # Удаляем временный файл
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_remove_document(self):
        """Тест удаления документа"""
        doc_id = self.indexer.add_document("Test document")
        self.assertGreaterEqual(doc_id, 0)

        # Удаляем документ
        result = self.indexer.remove_document(doc_id)
        self.assertTrue(result)

        # Проверяем, что документ помечен как None
        self.assertIsNone(self.indexer.documents[doc_id])

    def test_compact_index(self):
        """Тест компактизации индекса"""
        # Добавляем несколько документов
        doc_ids = []
        for i in range(3):
            doc_id = self.indexer.add_document(f"Test document {i}")
            doc_ids.append(doc_id)

        # Удаляем один документ
        self.indexer.remove_document(doc_ids[1])

        # Компактизируем
        self.indexer.compact()

        # Проверяем, что осталось 2 документа
        stats = self.indexer.get_stats()
        self.assertEqual(stats["total_documents"], 2)


class TestChromaDocumentIndexer(unittest.TestCase):
    """Тесты для ChromaDocumentIndexer"""

    def setUp(self):
        """Настройка теста"""
        self.temp_dir = tempfile.mkdtemp()
        self.embedder = DocumentEmbedder(model_name="all-MiniLM-L6-v2")

    def tearDown(self):
        """Очистка после теста"""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch("apps.embedding_agent.embedder.CHROMA_AVAILABLE", False)
    def test_chroma_indexer_fallback_mode(self):
        """Тест ChromaDocumentIndexer в режиме fallback"""
        indexer = ChromaDocumentIndexer(persist_directory=self.temp_dir, embedder=self.embedder)

        # Проверяем, что используется fallback режим
        self.assertTrue(indexer._use_fallback_only)

        # Добавляем документ
        doc_id = indexer.add_document("Test document")
        self.assertIsNotNone(doc_id)
        self.assertNotEqual(doc_id, "")

        # Выполняем поиск
        results = indexer.search("test")
        self.assertIsInstance(results, list)

        # Проверяем статистику
        stats = indexer.get_stats()
        self.assertIn("total_documents", stats)
        self.assertTrue(stats["fallback_mode"])

    def test_add_document(self):
        """Тест добавления документа"""
        indexer = ChromaDocumentIndexer(persist_directory=self.temp_dir, embedder=self.embedder)

        doc_id = indexer.add_document("Test document content", metadata={"source": "test"})
        self.assertIsNotNone(doc_id)
        self.assertNotEqual(doc_id, "")

    def test_add_document_empty(self):
        """Тест добавления пустого документа"""
        indexer = ChromaDocumentIndexer(persist_directory=self.temp_dir, embedder=self.embedder)

        doc_id = indexer.add_document("")
        self.assertEqual(doc_id, "")

    def test_get_stats(self):
        """Тест получения статистики"""
        indexer = ChromaDocumentIndexer(persist_directory=self.temp_dir, embedder=self.embedder)

        stats = indexer.get_stats()
        self.assertIsInstance(stats, dict)
        self.assertIn("total_documents", stats)
        self.assertIn("embedding_model", stats)

    def test_close_connection(self):
        """Тест закрытия соединения"""
        indexer = ChromaDocumentIndexer(persist_directory=self.temp_dir, embedder=self.embedder)

        # Просто вызываем метод, чтобы убедиться, что он не вызывает ошибок
        indexer.close()


if __name__ == "__main__":
    unittest.main()
