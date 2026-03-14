# Docker Fixes TODO (from Gordon chat - approved plan)
## Progress Tracker

- [x] 1. Update 02_MODULES/it-compass/requirements.txt (pytest-cov==7.0.0, fixed nonexistent 5.1.1)
- [x] 2. Update TODO-red-flags.md (add Docker subsection, marks)
- [x] 3. Update TODO.md (add to Red Flags section)
- [ ] 4. docker compose down && docker compose up --build -d
- [ ] 5. docker compose logs -f arch-compass (monitor ~5-10min Windows)
- [ ] 6. docker ps (verify healthy ports 8000/8001/8501)
- [x] Healthchecks removed/never present (docker-compose.yml clean)
- [x] pytest-cov ml-model-registry fixed (7.0.0)

**Status**: 2/8 complete. After all: Docker stable.

**Demo ports**:
- cloud-reason: http://localhost:8000
- ml-model-registry: http://localhost:8001
- it-compass: http://localhost:8501

