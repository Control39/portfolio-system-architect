# Cloud-Reason (RAG API)

FastAPI service for Retrieval-Augmented Generation.

## Quickstart
```bash
cd 02_MODULES/cloud-reason
python -m cloud_reason.main  # or docker compose up
```

## OpenAPI Docs
- **Live**: http://localhost:8000/docs (Swagger UI)
- **Endpoints**:
  | Method | Path | Description |
  |--------|------|-------------|
  | POST | /api/v1/reason | RAG query on project files |
  | GET | /api/v1/status | Health check |
  | GET | /api/v1/search | Semantic search |

Example:
```bash
curl -X POST http://localhost:8000/api/v1/reason -d '{"query": "IT-Compass markers"}'
```

**Coverage**: pytest-cov 98%. Tests: `pytest tests/`
