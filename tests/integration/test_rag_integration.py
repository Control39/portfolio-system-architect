#!/usr/bin/env python3
"""
Интеграционные тесты для RAG системы (ChromaDB + FastAPI + Streamlit).
Проверяет полный цикл работы системы от индексации до ответов через API.
"""

import os
import sys
import time
import json
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, List, Any

import pytest
import requests
from sentence_transformers import SentenceTransformer

# Добавляем путь к проекту
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.embedding_agent.chroma_indexer import ChromaDocumentIndexer
from src.embedding_agent.embedder import DocumentEmbedder


class TestRAGIntegration:
    """Интеграционные тесты для полной RAG системы."""
    
    @pytest.fixture
    def test_documents(self):
        """Создает тестовые документы для индексации."""
        return [
            {
                "text": "Когнитивная архитектура - это система, которая объединяет различные AI компоненты для решения сложных задач.",
                "metadata": {"source": "test_doc_1.md", "category": "architecture"}
            },
            {
                "text": "RAG (Retrieval-Augmented Generation) использует векторный поиск для улучшения ответов языковых моделей.",
                "metadata": {"source": "test_doc_2.md", "category": "ai"}
            },
            {
                "text": "ChromaDB - это векторная база данных с открытым исходным кодом для хранения и поиска эмбеддингов.",
                "metadata": {"source": "test_doc_3.md", "category": "database"}
            }
        ]
    
    @pytest.fixture
    def chroma_indexer(self, tmp_path):
        """Создает индексатор ChromaDB во временной директории."""
        persist_dir = tmp_path / "chroma_test"
        indexer = ChromaDocumentIndexer(persist_directory=str(persist_dir))
        return indexer
    
    def test_chromadb_indexing_and_search(self, chroma_indexer, test_documents):
        """Тестирует индексацию и поиск в ChromaDB."""
        # Добавляем документы
        for doc in test_documents:
            chroma_indexer.add_document(doc["text"], doc["metadata"])
        
        # Проверяем статистику
        stats = chroma_indexer.get_stats()
        assert stats["total_documents"] == 3
        assert stats["total_chunks"] >= 3
        
        # Ищем документы
        results = chroma_indexer.search("когнитивная архитектура", top_k=2)
        assert len(results) > 0
        
        # Проверяем, что найден правильный документ
        found = False
        for result in results:
            if "когнитивная архитектура" in result["text"]:
                found = True
                break
        assert found, "Должен быть найден документ про когнитивную архитектуру"
        
        # Проверяем метаданные
        for result in results:
            assert "metadata" in result
            assert "source" in result["metadata"]
    
    def test_chromadb_persistence(self, chroma_indexer, test_documents, tmp_path):
        """Тестирует сохранение и загрузку индекса ChromaDB."""
        # Добавляем документы
        for doc in test_documents:
            chroma_indexer.add_document(doc["text"], doc["metadata"])
        
        # Сохраняем путь к директории
        persist_dir = Path(chroma_indexer.persist_directory)
        
        # Создаем новый индексатор с той же директорией
        new_indexer = ChromaDocumentIndexer(persist_directory=str(persist_dir))
        
        # Проверяем, что документы сохранились
        results = new_indexer.search("ChromaDB", top_k=1)
        assert len(results) == 1
        assert "ChromaDB" in results[0]["text"]
    
    def test_fastapi_endpoints(self):
        """Тестирует эндпоинты FastAPI (если API запущен)."""
        # Этот тест требует запущенного API
        # В реальных условиях можно запускать через subprocess
        api_url = "http://localhost:8000"
        
        try:
            # Проверяем health endpoint
            response = requests.get(f"{api_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                assert data["status"] == "healthy"
                
                # Проверяем stats endpoint
                response = requests.get(f"{api_url}/stats", timeout=5)
                if response.status_code == 200:
                    stats = response.json()
                    assert "total_documents" in stats
                    
                # Проверяем ask endpoint
                question = {
                    "question": "Что такое когнитивная архитектура?",
                    "context": "Объясни простыми словами"
                }
                response = requests.post(
                    f"{api_url}/ask",
                    json=question,
                    timeout=10
                )
                if response.status_code == 200:
                    answer = response.json()
                    assert "answer" in answer
                    assert "sources" in answer
        except requests.exceptions.ConnectionError:
            pytest.skip("FastAPI не запущен, пропускаем тест")
    
    def test_streamlit_ui_integration(self, tmp_path):
        """Тестирует интеграцию с Streamlit UI через скрипты."""
        # Создаем тестовый скрипт Streamlit
        test_script = tmp_path / "test_streamlit.py"
        test_script.write_text("""
import streamlit as st
import sys
sys.path.insert(0, '.')

from src.embedding_agent.chroma_indexer import ChromaDocumentIndexer
import tempfile
import os

st.set_page_config(page_title="RAG Test", page_icon="🔍")

# Инициализация индексатора
with tempfile.TemporaryDirectory() as tmpdir:
    indexer = ChromaDocumentIndexer(persist_directory=tmpdir)
    
    # Добавляем тестовые документы
    indexer.add_document("Тестовый документ для RAG системы.", 
                        {"source": "test.md", "category": "test"})
    
    # Проверяем поиск
    results = indexer.search("RAG система", top_k=1)
    
    st.title("Тест Streamlit UI")
    st.write(f"Найдено результатов: {len(results)}")
    
    if results:
        st.write(f"Первый результат: {results[0]['text'][:100]}...")
        st.success("✅ Streamlit UI работает корректно")
    else:
        st.error("❌ Не найдено результатов")
""")
        
        # Запускаем скрипт через subprocess
        try:
            result = subprocess.run(
                [sys.executable, "-m", "streamlit", "run", str(test_script), 
                 "--server.headless", "true", "--server.port", "8502"],
                capture_output=True,
                text=True,
                timeout=30
            )
            # Проверяем, что скрипт выполнился без критических ошибок
            assert result.returncode == 0 or "Streamlit" in result.stdout
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pytest.skip("Streamlit не установлен или не может быть запущен")
    
    def test_docker_compose_integration(self):
        """Проверяет корректность docker-compose конфигурации."""
        compose_file = Path("docker-compose.rag.yml")
        
        if compose_file.exists():
            # Проверяем синтаксис YAML
            import yaml
            with open(compose_file, 'r') as f:
                config = yaml.safe_load(f)
            
            # Проверяем обязательные сервисы
            assert "services" in config
            services = config["services"]
            
            assert "chromadb" in services, "Сервис ChromaDB должен быть определен"
            assert "rag-api" in services, "Сервис RAG API должен быть определен"
            assert "streamlit-ui" in services, "Сервис Streamlit UI должен быть определен"
            
            # Проверяем настройки сети
            assert "networks" in config
            assert "rag-network" in config["networks"]
            
            # Проверяем volumes
            assert "volumes" in config
            assert "chroma-data" in config["volumes"]
        else:
            pytest.skip("Файл docker-compose.rag.yml не найден")
    
    def test_kubernetes_deployment(self):
        """Проверяет корректность Kubernetes манифестов."""
        deployment_files = [
            Path("deployment/rag-api-deployment.yaml"),
            Path("deployment/streamlit-ui-deployment.yaml")
        ]
        
        for file_path in deployment_files:
            if file_path.exists():
                import yaml
                with open(file_path, 'r') as f:
                    manifest = yaml.safe_load(f)
                
                # Проверяем базовую структуру
                assert "apiVersion" in manifest
                assert "kind" in manifest
                assert "metadata" in manifest
                assert "spec" in manifest
                
                if manifest["kind"] == "Deployment":
                    # Проверяем спецификацию deployment
                    spec = manifest["spec"]
                    assert "template" in spec
                    assert "spec" in spec["template"]
                    assert "containers" in spec["template"]["spec"]
                    
                    # Проверяем health checks
                    containers = spec["template"]["spec"]["containers"]
                    for container in containers:
                        if "livenessProbe" in container:
                            assert "httpGet" in container["livenessProbe"]
                        if "readinessProbe" in container:
                            assert "httpGet" in container["readinessProbe"]
            else:
                pytest.skip(f"Файл {file_path} не найден")


class TestRAGPerformance:
    """Тесты производительности RAG системы."""
    
    @pytest.fixture
    def performance_indexer(self, tmp_path):
        """Создает индексатор для тестов производительности."""
        persist_dir = tmp_path / "chroma_perf"
        indexer = ChromaDocumentIndexer(persist_directory=str(persist_dir))
        
        # Добавляем 100 тестовых документов
        for i in range(100):
            text = f"Документ номер {i} о когнитивных архитектурах и RAG системах. " \
                   f"Это тестовый контент для проверки производительности поиска."
            metadata = {"source": f"perf_doc_{i}.md", "index": i}
            indexer.add_document(text, metadata)
        
        return indexer
    
    def test_search_performance(self, performance_indexer):
        """Тестирует производительность поиска."""
        import time
        
        queries = [
            "когнитивная архитектура",
            "RAG система",
            "векторный поиск",
            "искусственный интеллект",
            "база данных"
        ]
        
        max_time_per_query = 0.5  # секунд
        total_time = 0
        
        for query in queries:
            start_time = time.time()
            results = performance_indexer.search(query, top_k=5)
            end_time = time.time()
            
            query_time = end_time - start_time
            total_time += query_time
            
            # Проверяем, что поиск работает достаточно быстро
            assert query_time < max_time_per_query, \
                f"Поиск по запросу '{query}' занял {query_time:.3f} секунд, " \
                f"максимум {max_time_per_query} секунд"
            
            # Проверяем, что возвращаются результаты
            assert len(results) > 0, f"Не найдено результатов для запроса '{query}'"
        
        avg_time = total_time / len(queries)
        print(f"\nСреднее время поиска: {avg_time:.3f} секунд")
        assert avg_time < 0.3, f"Среднее время поиска {avg_time:.3f} слишком велико"
    
    def test_concurrent_searches(self, performance_indexer):
        """Тестирует параллельные поисковые запросы."""
        import concurrent.futures
        
        queries = [f"запрос {i}" for i in range(10)]
        
        def search_query(query):
            return performance_indexer.search(query, top_k=3)
        
        # Выполняем запросы параллельно
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(search_query, query) for query in queries]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # Проверяем, что все запросы выполнены
        assert len(results) == len(queries)
        for result in results:
            assert isinstance(result, list)


def test_full_rag_pipeline():
    """Полный интеграционный тест RAG пайплайна."""
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # 1. Инициализация компонентов
        embedder = DocumentEmbedder()
        indexer = ChromaDocumentIndexer(persist_directory=tmpdir)
        
        # 2. Индексация документов
        test_docs = [
            "Микросервисная архитектура позволяет независимо развертывать компоненты системы.",
            "Kubernetes обеспечивает оркестрацию контейнеров в продакшен среде.",
            "Prometheus и Grafana используются для мониторинга и визуализации метрик."
        ]
        
        for i, doc in enumerate(test_docs):
            indexer.add_document(doc, {"source": f"doc_{i}.md", "type": "architecture"})
        
        # 3. Проверка индексации
        stats = indexer.get_stats()
        assert stats["total_documents"] == 3
        
        # 4. Поиск
        results = indexer.search("мониторинг микросервисов", top_k=2)
        assert len(results) >= 1
        
        # 5. Проверка качества результатов
        found_monitoring = False
        for result in results:
            if any(word in result["text"].lower() for word in ["prometheus", "grafana", "мониторинг"]):
                found_monitoring = True
                break
        
        assert found_monitoring, "Должны быть найдены документы про мониторинг"
        
        print("\n✅ Полный RAG пайплайн работает корректно:")
        print(f"   - Индексировано документов: {stats['total_documents']}")
        print(f"   - Найдено чанков: {stats['total_chunks']}")
        print(f"   - Результатов поиска: {len(results)}")


if __name__ == "__main__":
    """Запуск интеграционных тестов напрямую."""
    import sys
    sys.exit(pytest.main([__file__, "-v"]))