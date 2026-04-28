# Employer Demo Guide

STATUS: ⚠️ PARTIALLY OPERATIONAL - Core infra Up, apps need fixes

## Key Features
- **STATUS: ✅ ALL SYSTEMS OPERATIONAL** (Infra OK)

- **Live Services** (docker compose up):
  | Service | URL | Description |
  |---------|-----|-------------|
  | IT-Compass | http://localhost:8501 | Competency tracker |
  | Decision Engine | http://localhost:8001 | RAG AI analysis |
  | Career-Dev | http://localhost:8000 | Career system |
  | ML Registry | http://localhost:8002 | Model versioning |
  | Portfolio Organizer | http://localhost:8004 | Site generator |
  | System Proof | http://localhost:8003 | Evidence store |

- **Static Demo**: index.html
- **Monitoring**: Grafana (3000), Prometheus (9090)
- **Architecture**: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- **Metrics**: 92% test coverage, Docker-multi-service.

## Screenshots
- [IT-Compass](/docs/evidence/screenshots/employer-demo/it-compass.png)
- Add more after capture.

**Status**: Production-ready monorepo under active development for grant review. Some services stabilizing. Integrated manual-review tools. GitHub mirror: https://github.com/Control39/portfolio-system-architect. Integration complete: [docs/archive/MANUAL_REVIEW_INTEGRATION_PLAN.md](docs/archive/MANUAL_REVIEW_INTEGRATION_PLAN.md)
