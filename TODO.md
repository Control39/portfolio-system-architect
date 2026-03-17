# TODO: Fix SourceCraft Warnings (blackboxai/fix-review-issues)
Status: Approved by user | In Progress by BlackboxAI

## ✅ Completed (Cleanup Phase)
- [x] Remove IDE/sync/temp/duplicates (91f9337)
- [x] Replace test secrets v1 (c910c1f)

## 🔄 In Progress (Security/Duplicates Fix)
1. [x] List & git rm duplicate psm1/ps1 files (StructuredLogger-1/11/111, SecretManager-1 removed)
2. [x] Re-edit tests for remaining hardcoded secrets (SecretManager multiline fixed)
3. [ ] Fix docker-compose.yml passwords → ${VAR} + .env.example
4. [ ] Audit/remove unused exports (InputValidator.psm1 etc.)
5. [ ] git add/commit/push "fix: resolve security bot + duplicates"
6. [ ] Run Invoke-SecurityScan verify clean

## ⏳ Pending (Future PRs)
- benchmark_services.py/healthcheck.py: fix empty except
- Migrate-Structure.ps1: clean patterns
- Enhance primitive tests
