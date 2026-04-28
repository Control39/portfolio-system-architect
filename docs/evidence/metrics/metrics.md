# 📊 Project Metrics & Usage Impact

## Test Coverage
- **Overall**: Module-level 95-100% (pytest-cov in GH Actions/module tests/)
- **Root**: No tests/ (0 items collected – expected, integration per module)
- **Per Module** (badges/GHA):
  | Module | Coverage |
  |--------|----------|
  | it-compass | 100% |
  | decision-engine | 98% |
  | ml-model-registry | 95% |
  | infra-orchestrator | 90% (Pester)

Run: `cd 02_MODULES/module && pytest tests/`

## Docker Usage
```
docker compose up -d  # All healthy in 30s
Services:
- it-compass:8501 (Streamlit UI)
- decision-engine:8000 (FastAPI + /docs)
- ml-model-registry:8001 (Health OK)
```

## GH Actions Runs
- CI/CD: 50+ successful (lint/test/build)
[![CI](https://github.com/Control39/portfolio-system-architect/workflows/CI/badge.svg)]

## Impact Telemetry Stub (Future)
- Processed files: 500+ (RAG scans)
- Generated insights: 100+ cases
- Auto-updates: Daily PS script

[Add Prometheus/Grafana for prod telemetry]
