# ML Model Registry

FastAPI API for ML model versioning/storage.

## Quickstart
```bash
cd 02_MODULES/ml-model-registry
python -m src.api.main
```

## OpenAPI Docs
- **Live**: http://localhost:8001/docs
- **Endpoints**:
  | Method | Path | Description |
  |--------|------|-------------|
  | POST | /models | Upload model |
  | GET | /models/{id} | Get version |
  | GET | /health | Status |

**Coverage**: pytest 95%. SQLite backend.

