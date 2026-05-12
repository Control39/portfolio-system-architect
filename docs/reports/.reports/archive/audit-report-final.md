# Repository Audit Report

**Date**: 2026-05-05 18:11:14 UTC
**Repository**: `C:\Users\Z\DeveloperEnvironment\projects\portfolio-system-architect`

## Summary

**Overall Score**: 97.0/114.0 (85.09%)

### Category Scores

| Category | Score | Total | Percentage |
|----------|-------|-------|------------|
| documentation | 19.0 | 19.0 | 100.00% |
| security | 19.0 | 28.0 | 67.86% |
| structure | 34.0 | 38.0 | 89.47% |
| cicd | 13.0 | 14.0 | 92.86% |
| code_quality | 12.0 | 15.0 | 80.00% |

## Checks

| Status | Category | Check | Path | Details |
|--------|----------|-------|------|---------|
| ✅ PASS | documentation | Essential documentation files exist | `README.md` | File exists: README.md |
| ⚠️ WARNING | documentation | Essential documentation files exist | `README.ru.md` | Russian README missing (optional) |
| ✅ PASS | documentation | Essential documentation files exist | `CONTRIBUTING.md` | File exists: CONTRIBUTING.md |
| ✅ PASS | documentation | Essential documentation files exist | `CODE_OF_CONDUCT.md` | File exists: CODE_OF_CONDUCT.md |
| ✅ PASS | documentation | Essential documentation files exist | `CHANGELOG.md` | File exists: CHANGELOG.md |
| ✅ PASS | documentation | Essential documentation files exist | `ARCHITECTURE.md` | File exists: ARCHITECTURE.md |
| ✅ PASS | documentation | Essential documentation files exist | `LICENSE` | File exists: LICENSE |
| ✅ PASS | documentation | Essential documentation files exist | `SECURITY.md` | File exists: SECURITY.md |
| ✅ PASS | documentation | Essential documentation files exist | `docs` | Directory exists: docs |
| ✅ PASS | documentation | Essential documentation files exist | `docs/architecture/decisions` | ADR directory exists |
| ✅ PASS | documentation | README contains key sections | `README.md` | README contains '# ' |
| ✅ PASS | documentation | README contains key sections | `README.md` | README contains '## ' |
| ✅ PASS | documentation | README contains key sections | `README.md` | README contains '```' |
| ✅ PASS | documentation | README contains key sections | `README.md` | README contains 'https://' |
| ⚠️ WARNING | documentation | README contains key sections | `README.md` | README missing 'Has images' |
| ⚠️ WARNING | documentation | README contains key sections | `README.md` | README missing 'Has installation section' |
| ⚠️ WARNING | documentation | README contains key sections | `README.md` | README missing 'Has usage section' |
| ✅ PASS | documentation | README contains key sections | `README.md` | README contains 'Contributing' |
| ✅ PASS | documentation | README contains key sections | `README.md` | README contains 'License' |
| ✅ PASS | security | Essential security files and configurations | `SECURITY.md` | File exists: SECURITY.md |
| ✅ PASS | security | Essential security files and configurations | `.gitignore` | File exists: .gitignore |
| ❌ FAIL | security | Essential security files and configurations | `.secrets.baseline` | File missing: .secrets.baseline |
| ✅ PASS | security | Essential security files and configurations | `config/tools/.secrets.baseline` | File exists: config/tools/.secrets.baseline |
| ❌ FAIL | security | Essential security files and configurations | `.bandit.yml` | File missing: .bandit.yml |
| ✅ PASS | security | Essential security files and configurations | `config/tools/.bandit.yml` | File exists: config/tools/.bandit.yml |
| ❌ FAIL | security | Essential security files and configurations | `.trivyignore` | File missing: .trivyignore |
| ✅ PASS | security | Essential security files and configurations | `config/tools/.trivyignore` | File exists: config/tools/.trivyignore |
| ❌ FAIL | security | Essential security files and configurations | `.pre-commit-config.yaml` | File missing: .pre-commit-config.yaml |
| ✅ PASS | security | Essential security files and configurations | `config/tools/.pre-commit-config.yaml` | File exists: config/tools/.pre-commit-config.yaml |
| ❌ FAIL | security | Essential security files and configurations | `.pre-commit-config.yaml` | File missing: .pre-commit-config.yaml |
| ✅ PASS | security | Essential security files and configurations | `config/tools/.pre-commit-config.yaml` | File exists: config/tools/.pre-commit-config.yaml |
| ❌ FAIL | security | Essential security files and configurations | `.pre-commit-config.yaml` | File missing for content check: .pre-commit-config.yaml |
| ✅ PASS | security | Essential security files and configurations | `deployment/secrets` | Directory exists: deployment/secrets |
| ✅ PASS | security | Essential security files and configurations | `deployment/secrets/sealed-secrets` | Sealed‑secrets directory exists |
| ⚠️ WARNING | security | Essential security files and configurations | `.env.example` | .env.example missing |
| ✅ PASS | security | Essential security files and configurations | `.gitignore` | Keyword '.env' found in .gitignore |
| ✅ PASS | security | Essential security files and configurations | `.gitignore` | .gitignore excludes .env |
| ✅ PASS | security | Dependency security scanning configured | `requirements-dev.txt` | File exists: requirements-dev.txt |
| ❌ FAIL | security | Dependency security scanning configured | `requirements-dev.txt` | Keyword 'pip-audit' not found in requirements-dev.txt |
| ⚠️ WARNING | security | Dependency security scanning configured | `requirements-dev.txt` | pip‑audit not in dev requirements |
| ❌ FAIL | security | Dependency security scanning configured | `.bandit.yml` | File missing: .bandit.yml |
| ✅ PASS | security | Dependency security scanning configured | `config/tools/.bandit.yml` | File exists: config/tools/.bandit.yml |
| ✅ PASS | security | Dependency security scanning configured | `.bandit.yml or config/tools/.bandit.yml` | Bandit config exists |
| ❌ FAIL | security | Dependency security scanning configured | `.trivyignore` | File missing: .trivyignore |
| ✅ PASS | security | Dependency security scanning configured | `config/tools/.trivyignore` | File exists: config/tools/.trivyignore |
| ✅ PASS | security | Dependency security scanning configured | `.trivyignore or config/tools/.trivyignore` | Trivy ignore file exists |
| ✅ PASS | security | Dependency security scanning configured | `.github/workflows` | Security workflows found: ['security-scan.yml'] |
| ✅ PASS | structure | Repository follows standard structure | `apps` | Applications directory exists |
| ✅ PASS | structure | Repository follows standard structure | `src` | Source code directory exists |
| ✅ PASS | structure | Repository follows standard structure | `tests` | Tests directory exists |
| ✅ PASS | structure | Repository follows standard structure | `docs` | Documentation directory exists |
| ✅ PASS | structure | Repository follows standard structure | `deployment` | Deployment configurations exists |
| ✅ PASS | structure | Repository follows standard structure | `docker` | Docker configurations exists |
| ✅ PASS | structure | Repository follows standard structure | `monitoring` | Monitoring configurations exists |
| ✅ PASS | structure | Repository follows standard structure | `scripts` | Utility scripts exists |
| ✅ PASS | structure | Repository follows standard structure | `tools` | Development tools exists |
| ✅ PASS | structure | Repository follows standard structure | `config` | Configuration files exists |
| ⚠️ WARNING | structure | Repository follows standard structure | `config/tools/pytest.ini` | Pytest configuration missing from config/ |
| ✅ PASS | structure | Repository follows standard structure | `config/tools/.bandit.yml` | Bandit security configuration exists in config/ |
| ✅ PASS | structure | Repository follows standard structure | `config/tools/.pre-commit-config.yaml` | Pre-commit hooks configuration exists in config/ |
| ⚠️ WARNING | structure | Repository follows standard structure | `config/ci-cd/mkdocs.yml` | MkDocs configuration missing from config/ |
| ✅ PASS | structure | Repository follows standard structure | `config/ci-cd/azure.yaml` | Azure deployment configuration exists in config/ |
| ⚠️ WARNING | structure | Repository follows standard structure | `config/docker/docker-compose.yml` | Docker Compose configuration missing from config/ |
| ⚠️ WARNING | structure | Repository follows standard structure | `.` | Potential clutter in root: $null, .coverage, .gitleaksignore |
| ❌ FAIL | structure | Files and directories follow naming conventions | `docs\_drafts\Миграция `cloud_reason` → `decision_engine` — восстановление ядра и устранение техдолга.md` | File name contains space: docs\_drafts\Миграция `cloud_reason` → `decision_engine` — восстановление ядра и устранение техдолга.md |
| ❌ FAIL | structure | Files and directories follow naming conventions | `.venv\Lib\site-packages\setuptools\launcher manifest.xml` | File name contains space: .venv\Lib\site-packages\setuptools\launcher manifest.xml |
| ❌ FAIL | structure | Files and directories follow naming conventions | `.venv\Lib\site-packages\setuptools\script (dev).tmpl` | File name contains space: .venv\Lib\site-packages\setuptools\script (dev).tmpl |
| ❌ FAIL | structure | Files and directories follow naming conventions | `.venv\Lib\site-packages\setuptools\_vendor\jaraco\text\Lorem ipsum.txt` | File name contains space: .venv\Lib\site-packages\setuptools\_vendor\jaraco\text\Lorem ipsum.txt |
| ⚠️ WARNING | structure | Files and directories follow naming conventions | `$null` | File name contains special characters: $null |
| ⚠️ WARNING | structure | Files and directories follow naming conventions | `scripts\dev\$logPath` | File name contains special characters: scripts\dev\$logPath |
| ⚠️ WARNING | structure | Files and directories follow naming conventions | `.venv\Lib\site-packages\setuptools\script (dev).tmpl` | File name contains special characters: .venv\Lib\site-packages\setuptools\script (dev).tmpl |
| ⚠️ WARNING | structure | Files and directories follow naming conventions | `.venv\Lib\site-packages\tzdata\zoneinfo\GMT+0` | File name contains special characters: .venv\Lib\site-packages\tzdata\zoneinfo\GMT+0 |
| ⚠️ WARNING | structure | Files and directories follow naming conventions | `.venv\Lib\site-packages\tzdata\zoneinfo\Etc\GMT+0` | File name contains special characters: .venv\Lib\site-packages\tzdata\zoneinfo\Etc\GMT+0 |
| ⚠️ WARNING | structure | Files and directories follow naming conventions | `.venv\Lib\site-packages\tzdata\zoneinfo\Etc\GMT+1` | File name contains special characters: .venv\Lib\site-packages\tzdata\zoneinfo\Etc\GMT+1 |
| ⚠️ WARNING | structure | Files and directories follow naming conventions | `.venv\Lib\site-packages\tzdata\zoneinfo\Etc\GMT+10` | File name contains special characters: .venv\Lib\site-packages\tzdata\zoneinfo\Etc\GMT+10 |
| ⚠️ WARNING | structure | Files and directories follow naming conventions | `.venv\Lib\site-packages\tzdata\zoneinfo\Etc\GMT+11` | File name contains special characters: .venv\Lib\site-packages\tzdata\zoneinfo\Etc\GMT+11 |
| ⚠️ WARNING | structure | Files and directories follow naming conventions | `.venv\Lib\site-packages\tzdata\zoneinfo\Etc\GMT+12` | File name contains special characters: .venv\Lib\site-packages\tzdata\zoneinfo\Etc\GMT+12 |
| ⚠️ WARNING | structure | Files and directories follow naming conventions | `.venv\Lib\site-packages\tzdata\zoneinfo\Etc\GMT+2` | File name contains special characters: .venv\Lib\site-packages\tzdata\zoneinfo\Etc\GMT+2 |
| ⚠️ WARNING | structure | Files and directories follow naming conventions | `.venv\Lib\site-packages\tzdata\zoneinfo\Etc\GMT+3` | File name contains special characters: .venv\Lib\site-packages\tzdata\zoneinfo\Etc\GMT+3 |
| ⚠️ WARNING | structure | Files and directories follow naming conventions | `.venv\Lib\site-packages\tzdata\zoneinfo\Etc\GMT+4` | File name contains special characters: .venv\Lib\site-packages\tzdata\zoneinfo\Etc\GMT+4 |
| ⚠️ WARNING | structure | Files and directories follow naming conventions | `.venv\Lib\site-packages\tzdata\zoneinfo\Etc\GMT+5` | File name contains special characters: .venv\Lib\site-packages\tzdata\zoneinfo\Etc\GMT+5 |
| ⚠️ WARNING | structure | Files and directories follow naming conventions | `.venv\Lib\site-packages\tzdata\zoneinfo\Etc\GMT+6` | File name contains special characters: .venv\Lib\site-packages\tzdata\zoneinfo\Etc\GMT+6 |
| ⚠️ WARNING | structure | Files and directories follow naming conventions | `.venv\Lib\site-packages\tzdata\zoneinfo\Etc\GMT+7` | File name contains special characters: .venv\Lib\site-packages\tzdata\zoneinfo\Etc\GMT+7 |
| ⚠️ WARNING | structure | Files and directories follow naming conventions | `.venv\Lib\site-packages\tzdata\zoneinfo\Etc\GMT+8` | File name contains special characters: .venv\Lib\site-packages\tzdata\zoneinfo\Etc\GMT+8 |
| ⚠️ WARNING | structure | Files and directories follow naming conventions | `.venv\Lib\site-packages\tzdata\zoneinfo\Etc\GMT+9` | File name contains special characters: .venv\Lib\site-packages\tzdata\zoneinfo\Etc\GMT+9 |
| ✅ PASS | cicd | CI/CD pipelines configured | `.github/workflows` | GitHub Actions workflows found: 30 |
| ✅ PASS | cicd | CI/CD pipelines configured | `.github/workflows` | Workflow 'ci' present |
| ✅ PASS | cicd | CI/CD pipelines configured | `.github/workflows` | Workflow 'test' present |
| ✅ PASS | cicd | CI/CD pipelines configured | `.github/workflows` | Workflow 'security' present |
| ✅ PASS | cicd | CI/CD pipelines configured | `.github/workflows` | Workflow 'deploy' present |
| ✅ PASS | cicd | CI/CD pipelines configured | `docker-compose.yml` | File exists: docker-compose.yml |
| ✅ PASS | cicd | CI/CD pipelines configured | `docker-compose.yml` | Docker Compose file exists |
| ✅ PASS | cicd | CI/CD pipelines configured | `deployment/k8s` | Directory exists: deployment/k8s |
| ✅ PASS | cicd | CI/CD pipelines configured | `deployment/k8s` | Kubernetes manifests exist |
| ✅ PASS | cicd | CI/CD pipelines configured | `Makefile` | File exists: Makefile |
| ✅ PASS | cicd | CI/CD pipelines configured | `Makefile` | Makefile exists |
| ❌ FAIL | cicd | CI/CD pipelines configured | `.pre-commit-config.yaml` | File missing: .pre-commit-config.yaml |
| ✅ PASS | cicd | CI/CD pipelines configured | `config/tools/.pre-commit-config.yaml` | File exists: config/tools/.pre-commit-config.yaml |
| ✅ PASS | cicd | CI/CD pipelines configured | `config/tools/.pre-commit-config.yaml` | Pre‑commit config exists |
| ✅ PASS | code_quality | Code quality tools configured | `pyproject.toml` | File exists: pyproject.toml |
| ✅ PASS | code_quality | Code quality tools configured | `pyproject.toml` | Keyword 'ruff' found in pyproject.toml |
| ✅ PASS | code_quality | Code quality tools configured | `pyproject.toml` | Ruff configured in pyproject.toml |
| ✅ PASS | code_quality | Code quality tools configured | `pyproject.toml` | Keyword 'black' found in pyproject.toml |
| ✅ PASS | code_quality | Code quality tools configured | `pyproject.toml` | Black configured |
| ✅ PASS | code_quality | Code quality tools configured | `pyproject.toml` | Keyword 'isort' found in pyproject.toml |
| ✅ PASS | code_quality | Code quality tools configured | `pyproject.toml` | isort configured |
| ❌ FAIL | code_quality | Code quality tools configured | `pyrightconfig.json` | File missing: pyrightconfig.json |
| ✅ PASS | code_quality | Code quality tools configured | `config/tools/pyrightconfig.json` | File exists: config/tools/pyrightconfig.json |
| ✅ PASS | code_quality | Code quality tools configured | `pyrightconfig.json or config/tools/pyrightconfig.json` | Pyright config exists |
| ❌ FAIL | code_quality | Code quality tools configured | `.editorconfig` | File missing: .editorconfig |
| ⚠️ WARNING | code_quality | Code quality tools configured | `.editorconfig` | .editorconfig missing |
| ❌ FAIL | code_quality | Code quality tools configured | `.pre-commit-config.yaml` | File missing: .pre-commit-config.yaml |
| ✅ PASS | code_quality | Code quality tools configured | `config/tools/.pre-commit-config.yaml` | File exists: config/tools/.pre-commit-config.yaml |
| ✅ PASS | code_quality | Code quality tools configured | `config/tools/.pre-commit-config.yaml` | Pre‑commit includes quality hooks |

## Recommendations

### Critical Issues
- **Essential security files and configurations** (`.secrets.baseline`): File missing: .secrets.baseline
- **Essential security files and configurations** (`.bandit.yml`): File missing: .bandit.yml
- **Essential security files and configurations** (`.trivyignore`): File missing: .trivyignore
- **Essential security files and configurations** (`.pre-commit-config.yaml`): File missing: .pre-commit-config.yaml
- **Essential security files and configurations** (`.pre-commit-config.yaml`): File missing: .pre-commit-config.yaml
- **Essential security files and configurations** (`.pre-commit-config.yaml`): File missing for content check: .pre-commit-config.yaml
- **Dependency security scanning configured** (`requirements-dev.txt`): Keyword 'pip-audit' not found in requirements-dev.txt
- **Dependency security scanning configured** (`.bandit.yml`): File missing: .bandit.yml
- **Dependency security scanning configured** (`.trivyignore`): File missing: .trivyignore
- **Files and directories follow naming conventions** (`docs\_drafts\Миграция `cloud_reason` → `decision_engine` — восстановление ядра и устранение техдолга.md`): File name contains space: docs\_drafts\Миграция `cloud_reason` → `decision_engine` — восстановление ядра и устранение техдолга.md

### Suggested Improvements
- **Essential documentation files exist** (`README.ru.md`): Russian README missing (optional)
- **README contains key sections** (`README.md`): README missing 'Has images'
- **README contains key sections** (`README.md`): README missing 'Has installation section'
- **README contains key sections** (`README.md`): README missing 'Has usage section'
- **Essential security files and configurations** (`.env.example`): .env.example missing
- **Dependency security scanning configured** (`requirements-dev.txt`): pip‑audit not in dev requirements
- **Repository follows standard structure** (`config/tools/pytest.ini`): Pytest configuration missing from config/
- **Repository follows standard structure** (`config/ci-cd/mkdocs.yml`): MkDocs configuration missing from config/
- **Repository follows standard structure** (`config/docker/docker-compose.yml`): Docker Compose configuration missing from config/
- **Repository follows standard structure** (`.`): Potential clutter in root: $null, .coverage, .gitleaksignore

---
*Generated by Repository Audit Tool*