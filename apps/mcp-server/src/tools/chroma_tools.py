#!/usr/bin/env python3
"""
ChromaDB Tools для MCP Server

Инструменты для работы с векторной базой ChromaDB.
"""

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP


def init_chroma_tools(mcp_server: FastMCP, project_root: Path) -> None:
    """Инициализация инструментов ChromaDB"""

    chroma_path = project_root / "chroma_data"

    @mcp_server.tool() # noqa: F821
    def chroma_get_collections() -> List[str]:
    def chroma_get_collections() -> List[str]:
        """
        Получение списка коллекций ChromaDB

        Возвращает:
            Список названий коллекций
        """
        try:
            import chromadb
            client = chromadb.PersistentClient(path=str(chroma_path))
            collections = client.list_collections()
            return [col.name for col in collections]

        except ImportError:
            return ["error: chromadb not installed"]
        except Exception as e:
            return [f"error: {str(e)}"]

    @mcp.tool()
    def chroma_query(
        collection_name: str, query_text: str, n_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Векторный поиск в коллекции ChromaDB

        Аргументы:
            collection_name: Название коллекции
            query_text: Текст запроса
            n_results: Количество результатов (по умолчанию 5)

        Возвращает:
            Список результатов с документами и метаданными
        """
        try:
            import chromadb
            client = chromadb.PersistentClient(path=str(chroma_path))
            collection = client.get_collection(collection_name)

            results = collection.query(query_texts=[query_text], n_results=n_results)

            formatted_results = []
            if results and results["documents"] and results["documents"][0]:
                for i, doc in enumerate(results["documents"][0]):
                    result = {
                        "document": doc,
                        "distance": results["distances"][0][i] if "distances" in results else None,
                        "metadata": results["metadatas"][0][i] if "metadatas" in results else None,
                    }
                    if results.get("ids"):
                        result["id"] = results["ids"][0][i]
                    formatted_results.append(result)

            return formatted_results

        except ImportError:
            return [{"error": "chromadb not installed"}]
        except Exception as e:
            return [{"error": f"query error: {str(e)}"}]

    @mcp.tool()
    def chroma_add_document(
        collection_name: str,
        document: str,
        metadata: Optional[Dict[str, Any]] = None,
        document_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Добавление документа в коллекцию ChromaDB

        Аргументы:
            collection_name: Название коллекции
            document: Текст документа
            metadata: Метаданные (опционально)
            document_id: ID документа (опционально, генерируется если не указан)

        Возвращает:
            Статус операции
        """
        try:
            import chromadb
            client = chromadb.PersistentClient(path=str(chroma_path))

            # Создаём коллекцию если не существует
            try:
                collection = client.get_collection(collection_name)
            except Exception:
                collection = client.create_collection(collection_name)

            # Генерируем ID если не указан
            import hashlib

            doc_id = document_id or hashlib.md5(document.encode()).hexdigest()

            collection.add(documents=[document], metadatas=[metadata or {}], ids=[doc_id])

            return {"status": "success", "collection": collection_name, "id": doc_id}

        except ImportError:
            return {"status": "error", "message": "chromadb not installed"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    @mcp.tool()
    def chroma_get_collection_info(collection_name: str) -> Dict[str, Any]:
        """
        Получение информации о коллекции

        Аргументы:
            collection_name: Название коллекции

        Возвращает:
            Информация о коллекции (количество документов и т.д.)
        """
        try:
            import chromadb

            client = chromadb.PersistentClient(path=str(chroma_path))

            try:
                collection = client.get_collection(collection_name)
                count = collection.count()

                return {
                    "name": collection_name,
                    "document_count": count,
                    "total_chunks": count,
                    "status": "exists",
                }
            except Exception:
                return {"name": collection_name, "status": "not_found"}

        except ImportError:
            return {"error": "chromadb not installed"}
        except Exception as e:
            return {"error": str(e)}
