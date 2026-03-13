# Portfolio System Architect

[![CI](https://github.com/YOUR_USERNAME/portfolio-system-architect/workflows/CI/badge.svg)](https://github.com/YOUR_USERNAME/portfolio-system-architect/actions)
[![Coverage](coverage_html/index.html)](coverage_html/index.html)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)](docker-compose.yml)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![PowerShell 7](https://img.shields-blue.svg)](https://powershell.org/)

Единая экосистема архитектора когнитивных систем с CI/CD, Docker, 100% test coverage.

## Quick Start

```bash
docker compose up -d
# API docs: http://localhost:8000/docs
# IT Compass: http://localhost:8501
# ML Registry: http://localhost:8001
```

## Modules
- **it-compass**: Streamlit career tracker (pytest 100%)
- **cloud-reason**: FastAPI reasoning API (pytest-cov)
- **ml-model-registry**: ML model versioning (pytest)
- **arch-compass-framework**: PowerShell arch patterns (Pester)

## CI/CD
- GH Actions: lint, test matrix, Docker build/push to GHCR
- Coverage: .coveragerc, pytest-cov, reports in Actions

## SourceCraft Grant
Project ready for submission:
- [Grant Proposal](cognitive-architect-manifesto/04_ARTIFACTS/grants/grant-proposal.md)
- Evidence: [Metrics](08_EVIDENCE/metrics/), Coverage badges above
- Architecture: [Ecosystem](diagrams/ecosystems.mmd)

License: MIT | Author: Екатерина Куделя

