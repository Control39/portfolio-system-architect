---
apply: Always
mode: Agent
---

## Repository Structure Rules

When analyzing or refactoring this repository:

### 1. **Exclude from analysis:**

**Virtual environments & cache:**
- `.venv/`, `venv/`, `env/` (Python virtual environments)
- `__pycache__/`, `*.pyc`, `*.pyo` (Python bytecode)
- `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/` (Tool cache)
- `node_modules/` (Node.js dependencies)

**Backup & archives:**
- `.archive/`, `.backup/`, `backups/` (Historical backups)
- `*.zip`, `*.tar.gz` (Archive files, except releases/)

**Generated artifacts:**
- `generated_routes/`, `cache/`, `reports/` (Runtime artifacts)
- `dist/`, `build/`, `out/` (Build outputs)
- `coverage/`, `htmlcov/` (Test coverage reports)
- `.coverage`, `.pytest/` (Test artifacts)

**IDE & editor:**
- `.vscode/`, `.idea/`, `*.swp`, `*.swo` (Editor configs, except shared settings)

**Logs & temp:**
- `logs/`, `*.log`, `tmp/`, `temp/` (Runtime logs and temp files)

---

### 2. **Depth limits:**

**Monolith services:** Maximum 3 levels
```
apps/monolith-service/
├── src/
├── tests/
└── README.md
```

**Microservices:** Maximum 5 levels
```
apps/microservice/
├── src/
│   ├── api/
│   ├── core/
│   └── services/
├── tests/
│   ├── unit/
│   └── integration/
├── docs/
├── Dockerfile
└── README.md
```

**No semantic duplication:**
- ❌ `career_development/career_development/`
- ✅ `career_development/src/`

**Standard app structure:**
- `src/` — Business logic
- `tests/` — Test suites
- `docs/` — Service-specific documentation (optional)
- `README.md` — Service overview

---

### 3. **Separation of concerns:**

**Infrastructure code →** `deployment/`, `docker/`, `k8s/`, `monitoring/`
- Docker Compose, Kubernetes manifests
- Terraform, Bicep, CloudFormation
- Prometheus, Grafana, Alertmanager

**Business logic →** `apps/*/src/`
- API endpoints
- Domain logic
- Data models
- Services

**Documentation →** `docs/` (central) + `apps/*/README.md` (brief)
- `docs/architecture/` — System architecture
- `docs/api/` — API documentation
- `docs/apps/` — Per-service documentation
- `apps/*/README.md` — Service overview (1-2 pages)

**Configuration →** `config/`, `settings/`, `.env.example`
- Environment templates
- Shared configurations
- Feature flags

**Scripts & automation →** `scripts/`, `Makefile*`
- Build scripts
- Deployment automation
- Development utilities

**Shared libraries →** `src/`, `libs/`, `packages/`
- Common utilities
- Shared models
- Base classes

---

### 4. **Naming conventions:**

**Directories:**
- `snake_case` for apps: `auth_service/`, `career_development/`
- `kebab-case` for infrastructure: `docker-compose/`, `k8s-manifests/`

**Files:**
- `snake_case` for Python: `user_model.py`, `auth_service.py`
- `kebab-case` for configs: `docker-compose.yml`, `.pre-commit-config.yaml`

**Branches:**
- `feature/description` — New features
- `fix/description` — Bug fixes
- `refactor/description` — Code refactoring
- `docs/description` — Documentation updates

---

### 5. **Quality gates:**

**Before commit:**
- [ ] No secrets in code (`.env`, API keys, passwords)
- [ ] No large files (>1MB without LFS)
- [ ] No merge conflict markers
- [ ] Pre-commit hooks pass

**Before merge:**
- [ ] Tests pass (unit + integration)
- [ ] Code coverage >80%
- [ ] Documentation updated
- [ ] No security vulnerabilities (bandit, pip-audit)

**Before release:**
- [ ] Changelog updated
- [ ] Version bumped (semver)
- [ ] Docker images built
- [ ] Deployment tested

---

### 6. **Exceptions:**

**Allowed deviations:**
- Legacy code in `.archive/` (documented migration plan)
- Generated code in `generated_*` (documented generation process)
- Deep nesting in `tests/` (up to 7 levels for complex test suites)

**Requires approval:**
- Adding new root-level directories
- Exceeding depth limits in core services
- Duplicating documentation across services

---

### 7. **Enforcement:**

**Automated:**
- Pre-commit hooks (format, lint, security)
- CI/CD checks (tests, coverage, vulnerabilities)
- Git hooks (branch naming, commit messages)

**Manual:**
- Code review (structure compliance)
- Architecture review (new services)
- Quarterly audits (technical debt)

---

## Quick Reference

| Check | Command |
|-------|---------|
| Find deep nesting | `find apps -type d -maxdepth 6` |
| Find duplicates | `fdupes -r apps/` |
| Check .gitignore | `git check-ignore -v <path>` |
| Audit structure | `python scripts/audit_structure.py` |
| Clean cache | `make clean` or `Remove-Item -Recurse __pycache__` |
