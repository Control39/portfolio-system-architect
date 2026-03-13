# Portfolio System Architect Improvements TODO
Status: CI/CD + Coverage + Grant In Progress (Plan Approved, Docker [✅], OpenAPI [✅], Deps [70%])

## Priority 1: Full Dockerization [✅]
- [✅] Create root docker-compose.yml (it-compass, cloud-reason, ml-model-registry, arch-compass, db sqlite)
- [✅] Add Dockerfiles: 02_MODULES/cloud-reason/, 02_MODULES/ml-model-registry/, 02_MODULES/arch-compass-framework/
- [✅] Update it-compass/Dockerfile to latest Python 3.12 + reqs
- [✅] Test: docker compose up -d (requires Docker Desktop running)

## Priority 2: OpenAPI Documentation [✅]
- [✅] Integrate FastAPI docs in cloud-reason/cloud_reason/api/endpoints.py (docs_url=\"/docs\")
- [✅] /docs + /redoc endpoints ready
- [ ] Add docs/API.md update if exists

## Priority 3: Update Dependencies [70%]
- [✅] Update requirements.txt (it-compass/cloud-reason/ml)
- [✅] Update root package.json (^ latest)
- [✅] Update project-config.yaml deps lists
- [ ] npm audit / pip check

## Priority 4: CI/CD Pipeline [0/10]
1. [ ] Create .github/workflows/ci.yml (lint, test matrix, docker-compose test)
2. [ ] Create .github/workflows/docker-build-push.yml (GHCR push)
3. [ ] Create .github/workflows/coverage.yml (badges)
4. [✅] Create root .coveragerc + module .coveragerc
5. [✅] Update requirements.txt: add pytest-cov==5.0.1, pytest-mock==3.14.1 (Python modules)
6. [ ] it-compass: enhance tests/ for 100% cov
7. [✅] cloud-reason: create tests/test_endpoints.py (TestClient)
8. [✅] ml-model-registry: create tests/test_api.py (pytest)
9. [✅] arch-compass: create tests/ for Pester
10. [✅] docker-compose.yml: add healthchecks

## Priority 5: Validation & 100% Coverage [ ]
- [ ] docker compose up --build & pytest --cov --cov-report=html
- [ ] GH Actions green

## Priority 6: SourceCraft Grant Prep [ ]
- [ ] Update grant-proposal.md + badges/metrics
- [ ] Root README.md badges/setup
- [ ] Clean duplicates, PDF export

Next: CI workflows (1-3)

