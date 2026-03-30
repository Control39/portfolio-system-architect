# ChromaDB Integration for RAG System

## 📋 Overview

This document describes the ChromaDB integration for the Architect Assistant RAG system, which replaces the simple in-memory indexer with a persistent vector database for production-ready deployment.

## 🎯 What's Implemented

### 1. **ChromaDocumentIndexer** (`src/embedding_agent/chroma_indexer.py`)
- Persistent vector storage using ChromaDB
- Support for metadata filtering and advanced queries
- Migration utility from pickle-based indexes
- Automatic collection management

### 2. **Deployment Configurations**
- **Dockerfiles**: `api/Dockerfile`, `ui/Dockerfile`
- **Kubernetes**: `deployment/rag-api-deployment.yaml`, `deployment/streamlit-ui-deployment.yaml`
- **Docker Compose**: `docker-compose.rag.yml` for local development

### 3. **Testing & Validation**
- `test_chroma_integration.py` - Comprehensive test suite
- Migration path from existing pickle indexes

## 🚀 Quick Start

### Local Development with Docker Compose

```bash
# Start all services
docker-compose -f docker-compose.rag.yml up -d

# Check services
docker-compose -f docker-compose.rag.yml ps

# View logs
docker-compose -f docker-compose.rag.yml logs -f rag-api

# Access services:
# - RAG API: http://localhost:8000/docs
# - Streamlit UI: http://localhost:8501
# - ChromaDB: http://localhost:8001
# - Adminer (DB): http://localhost:8080
```

### Manual Setup

```bash
# Install dependencies
pip install chromadb>=0.4.22 sentence-transformers>=2.2.2

# Test ChromaDB integration
python test_chroma_integration.py

# Run RAG API
cd api && uvicorn main:app --reload --port 8000

# Run Streamlit UI (in another terminal)
cd ui && streamlit run app.py
```

## 📊 Migration from Pickle-based Index

If you have an existing pickle-based index, migrate it to ChromaDB:

```python
from embedding_agent.chroma_indexer import ChromaDocumentIndexer

# Initialize ChromaDB indexer
indexer = ChromaDocumentIndexer(persist_directory="./chroma_db")

# Migrate from pickle
migrated_ids = indexer.migrate_from_pickle(".cache/rag_index.pkl")
print(f"Migrated {len(migrated_ids)} documents")
```

## 🏗️ Production Deployment

### Kubernetes Deployment

1. **Build Docker images:**
```bash
docker build -t rag-api:latest -f api/Dockerfile .
docker build -t streamlit-ui:latest -f ui/Dockerfile .
```

2. **Apply Kubernetes configurations:**
```bash
kubectl apply -f deployment/rag-api-deployment.yaml
kubectl apply -f deployment/streamlit-ui-deployment.yaml
```

3. **Verify deployment:**
```bash
kubectl get pods -n portfolio-system -l app=rag-api
kubectl get pods -n portfolio-system -l app=streamlit-ui
```

### Configuration Options

| Environment Variable | Description | Default |
|---------------------|-------------|---------|
| `CHROMA_PERSIST_DIR` | ChromaDB persistence directory | `/app/data/chroma_db` |
| `CHROMA_HOST` | ChromaDB host (for external Chroma) | `localhost` |
| `CHROMA_PORT` | ChromaDB port | `8000` |
| `API_URL` | RAG API URL for Streamlit UI | `http://rag-api:8000` |
| `LOG_LEVEL` | Logging level | `INFO` |

## 🔧 API Endpoints

### RAG API (`http://localhost:8000`)

- `POST /ask` - Ask questions about the project
- `GET /health` - Health check
- `GET /stats` - Index statistics
- `GET /docs` - OpenAPI documentation

### Streamlit UI (`http://localhost:8501`)

- Interactive web interface
- Adjustable search parameters
- Source citation display
- Confidence scoring

## 📈 Performance Considerations

### ChromaDB Configuration

1. **Persistence**: Data is automatically persisted to disk
2. **Collection Management**: Each project uses a separate collection
3. **Embedding Dimension**: 384 dimensions (all-MiniLM-L6-v2)
4. **Indexing Speed**: ~100 documents/second on CPU

### Resource Requirements

| Component | CPU | Memory | Storage |
|-----------|-----|--------|---------|
| RAG API | 250m | 512Mi | 1Gi (cache) |
| Streamlit UI | 100m | 256Mi | Minimal |
| ChromaDB | 500m | 1Gi | 5Gi+ (vector data) |

## 🔍 Monitoring & Observability

### Built-in Metrics
- `/health` endpoint for health checks
- Prometheus metrics (if configured)
- Logging at various levels

### Recommended Monitoring
1. **ChromaDB collection size**
2. **Query latency** (target: < 500ms)
3. **Index freshness** (last update timestamp)
4. **Memory usage** during indexing

## 🛠️ Troubleshooting

### Common Issues

1. **ChromaDB not starting:**
```bash
# Check if port 8000 is available
netstat -tuln | grep 8000

# Check ChromaDB logs
docker logs rag-chromadb
```

2. **Migration failures:**
- Ensure pickle file exists and is readable
- Check ChromaDB persistence directory permissions
- Verify embedding dimensions match

3. **High memory usage:**
- Reduce `top_k` parameter in searches
- Implement query caching
- Consider batch processing for large indexes

### Logs Location
- **Docker**: `docker logs <container_name>`
- **Kubernetes**: `kubectl logs <pod_name> -n portfolio-system`
- **Local**: Check application logs in console

## 🔮 Future Enhancements

1. **Multi-modal support** (images, code snippets)
2. **Hybrid search** (vector + keyword)
3. **Replication** for high availability
4. **Backup/restore** utilities
5. **Query analytics** dashboard

## 📚 References

- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Sentence Transformers](https://www.sbert.net/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Streamlit](https://docs.streamlit.io/)

## 🆘 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review application logs
3. Test with `test_chroma_integration.py`
4. Open an issue in the repository