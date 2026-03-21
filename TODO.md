# Integration from my-ecosystem-CLONE Backups
Generated: 2026 by BLACKBOXAI

Status Legend:
- [ ] TODO
- [x] Done

## Preparation [1/2]
- [x] Create TODO.md
- [ ] Backup current state (git stash or branch)

## Priority 1: apps/arch-compass-framework/ [7/8]
- [x] Merge README.md (already rich)
- [x] Update ArchCompass.psm1/psd1 with full loader/manifest
- [x] Create src/core/ (logging/validation/config/commands ~4 psm1)
- [x] Create src/ai/ (OpenAIIntegration)
- [x] Create src/infrastructure/queues (git/deploy/rabbit full)
- [x] tests/ pester config + run-tests.ps1
- [ ] scripts/ tools/ docs/ (from backup)
- [ ] Test run

## Priority 2: apps/it-compass/ [3/6]
- [x] Add src/core/reasoning_integration.py
- [x] Union requirements.txt (chardet/path)
- [x] Add imported_cases/portfolio_gen.py
- [ ] Merge docs/ARCHITECTURE.md (RAG details)
- [ ] pytest tests/test_tracker.py
- [ ] Add examples/support full

## Priority 3: apps/cloud-reason/ [5/5]
- [x] Add src/utils (rate/error/session)
- [x] Add tests/test_rate_limiter
- [x] diagnostics/analyze_encoding.ps1
- [x] requirements union
- [x] Ready

## Priority 4: apps/portfolio-organizer/ [0/4]
- [ ] Create src/core/ integrations/ utils/ notifications/
- [ ] Add docs/ requirements.txt test_api.sh
- [ ] infrastructure/scripts

## Priority 5: apps/system-proof/ thought-architecture/ [0/4]
- [ ] system-proof: RAG ps1 extractors
- [ ] thought-architecture: cases tools SECURITY.md

## Cross-cutting [0/6]
- [ ] scripts/ all ps1/py (backup/migrate/fix_encoding/sync)
- [ ] docs/unified_plan/ ARCHITECTURE_MAP SYNC_PLAN
- [ ] Root .gitleaks.toml
- [ ] tools/ PS extractors
- [ ] Merge root README ARCHITECTURE.md (mermaid ecosystem)
- [ ] Update docker-compose deployment yamls (volumes/ports)

## Final Validation [0/4]
- [ ] docker-compose up --build (all apps)
- [ ] Full tests (pytest pester docker)
- [ ] git add . commit -m \"integrated backups\" push
- [ ] scripts/generate-site.sh mkdocs
