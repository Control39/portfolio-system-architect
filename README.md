# Portfolio System Architect

This repository contains a comprehensive portfolio system for a Lead AI Systems Architect, demonstrating advanced capabilities in AI-driven career development, cloud reasoning, and system architecture.

<!-- Badges -->
<p align="center">
  <!-- Архитектура -->
  <img src="https://img.shields.io/badge/✅-Production--Ready-blue?style=for-the-badge" alt="Production Ready">
  <img src="https://img.shields.io/badge/✅-GitOps-orange?style=for-the-badge" alt="GitOps">
  <img src="https://img.shields.io/badge/✅-Observability-green?style=for-the-badge" alt="Observability">
</p>

<p align="center">
  <!-- Технические метрики (динамические) -->
  <img src="https://github.com/Control39/cognitive-systems-architecture/actions/workflows/ci.yml/badge.svg" alt="CI Status">
  <img src="https://codecov.io/gh/Control39/cognitive-systems-architecture/branch/main/graph/badge.svg" alt="Code Coverage">
  <img src="https://img.shields.io/github/last-commit/Control39/cognitive-systems-architecture?style=flat-square&logo=git" alt="Last Commit">
  <img src="https://img.shields.io/github/license/Control39/cognitive-systems-architecture?style=flat-square" alt="License">
</p>

<p align="center">
  <!-- Стек -->
  <img src="https://img.shields.io/badge/Kubernetes-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white" alt="Kubernetes">
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker">
  <img src="https://img.shields.io/badge/Prometheus-E6522C?style=for-the-badge&logo=prometheus&logoColor=white" alt="Prometheus">
  <img src="https://img.shields.io/badge/Grafana-F46800?style=for-the-badge&logo=grafana&logoColor=white" alt="Grafana">
</p>

---

## Project Structure

- `apps/` - Main application modules
- `src/` - Shared source code
- `tests/` - Test suites
- `docs/` - Documentation
- `deployment/` - Deployment configurations
- `diagrams/` - Architecture diagrams
- `scripts/` - Utility scripts
- `tools/` - Development tools

## Projects

This portfolio includes several projects, each demonstrating a unique aspect of system architecture and AI engineering:

| Project | Description | Status |
|---------|-------------|--------|
| **Arch-Compass-Framework** | PowerShell framework for architectural decision automation | Internal |
| **Cloud-Reason** | Reasoning API for systematic thinking with YandexGPT | Internal |
| **IT-Compass** | Skills tracking and burnout prevention system | Internal |
| **Career-Development** | AI‑driven career planning and roadmap generator | Internal |
| **ML-Model-Registry** | Versioned model registry with API and UI | Internal |
| **Portfolio-Organizer** | Automated portfolio organization and presentation | Internal |
| **System-Proof** | Formal verification of system architecture decisions | Internal |
| **Thought-Architecture** | Collection of cognitive architectural patterns | Internal |

For a detailed matrix of projects, see [Projects Matrix](docs/PROJECTS-MATRIX.md).

## Getting Started

1. Clone the repository
2. Install dependencies: `pip install -r requirements-dev.txt`
3. Set up environment variables
4. Run the application: `docker compose up -d`

## Docker

A `.dockerignore` file is included to optimize build performance by excluding unnecessary files:

```
__pycache__/
*.pyc
.git/
.venv/
node_modules/
*.log
.env
.coverage
htmlcov/
.pytest_cache/
dist/
build/
*.egg-info/
```

## Documentation for Employers

For a quick overview of the project's value and capabilities, see the [One-Pager](docs/EMPLOYER_ONE_PAGER.md) designed for technical leads and hiring managers. It highlights systemic thinking, AI orchestration, and **relevance for the Russian corporate sector** (Yandex, banks, IT integrators).

## Test Coverage

The project includes comprehensive test coverage:

- Unit tests for core components
- Integration tests for service interactions
- End-to-end tests for full workflows
- Code coverage is automatically measured and reported

![Test Coverage](https://img.shields.io/codecov/c/github/Control39/cognitive-systems-architecture?token=codecov_token)

Coverage reports are generated in HTML format and available in the `htmlcov/` directory after running tests.

## GitOps & CI/CD

The project implements a modern GitOps workflow with automated security gates, container scanning, and Kubernetes deployment.

- **CI Pipeline**: Security scanning (detect‑secrets, safety, pip‑audit, Trivy), linting, testing, Docker builds, and GitOps deployment.
- **GitOps**: Kubernetes manifests are managed with Kustomize and automatically applied via Argo CD or GitHub Actions.
- **Secrets Management**: Encrypted secrets using Sealed Secrets / SOPS.

For detailed instructions, see [GitOps Guide](docs/DEVOPS_GITOPS_GUIDE.md).

## Repository Audit Tool

This repository includes an **automated audit tool** that evaluates the maturity of the codebase against three levels (Base, Professional, Enterprise) with 70+ checkpoints.

### Features

- **Python CLI** (`tools/repo_audit/audit.py`) – run manually or in CI.
- **GitHub Actions workflow** – automatically audits on push/PR and posts results.
- **AI Skill for SourceCraft** – interact via chat: `@repo-audit проверить репозиторий`.
- **Customizable checklists** – YAML‑based, easy to extend.
- **Auto‑fix** – can automatically create missing files, fix formatting, etc.

### Usage

```bash
# Run audit for 'base' level
python -m tools.repo_audit.audit --level base --output markdown

# Run for all levels with auto‑fix
python -m tools.repo_audit.audit --level base,professional,enterprise --auto-fix
```

### Integration

- **CI/CD**: The audit runs in GitHub Actions; see `.github/workflows/repo-audit.yml`.
- **AI Skill**: Configured in `.sourcecraft/skills/repo-audit.yml`.
- **Configuration**: Settings are in `pyproject.toml` under `[tool.repo-audit]`.

For full documentation, see [Repo Audit Guide](docs/repo-audit-guide.md).

## Relevance for Russian Corporate Sector

This portfolio is designed to meet the specific needs of **Yandex**, **Russian banks (Sberbank, Tinkoff, VTB)**, and **IT integrators (Krok, IBS, Lanit)**:

- **Yandex Cloud** – uses Kubernetes, Docker, cloud‑native patterns directly applicable to Yandex Cloud’s container services.
- **Yandex GPT** – integration with Yandex’s LLM for AI skills (see `.sourcecraft/skills/`).
- **Security & compliance** – network policies, PodSecurityPolicies, secrets management, SAST/DAST that meet strict financial sector standards.
- **Legacy modernization** – shows how to incrementally migrate monolithic systems to microservices with AI‑assisted refactoring.

The **systemic thinking** and **AI orchestration** demonstrated here are exactly what Russian enterprises need to accelerate digital transformation while maintaining reliability and security.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🏆 Production Readiness Checklist

| Категория | Статус | Документация |
|-----------|--------|--------------|
| **Тестирование** | ✅ | Unit (pytest), Integration, E2E, Load (Locust) |
| **CI/CD** | ✅ | GitHub Actions + Kustomize + GitOps |
| **Безопасность** | ✅ | Sealed Secrets, ротация в `docs/secrets.md` |
| **Окружения** | ✅ | dev / staging / prod overlays |
| **Мониторинг** | ✅ | Prometheus + Grafana + AlertManager |
| **Disaster Recovery** | ✅ | Бэкапы, восстановление, DR Runbook |
| **Документация** | ✅ | MkDocs, авто-генерация, аудит |

See: https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions

**Documentation:**
- API Docs: https://Control39.github.io/cognitive-systems-architecture/
- Scaling Plan: [docs/scaling-plan.md](docs/scaling-plan.md)
- GitOps Guide: [docs/DEVOPS_GITOPS_GUIDE.md](docs/DEVOPS_GITOPS_GUIDE.md)
- Security: [docs/security/SECRETS-MANAGEMENT.md](docs/security/SECRETS-MANAGEMENT.md)
- Repo Audit: [docs/repo-audit-guide.md](docs/repo-audit-guide.md)

**Monitoring (Grafana/Prometheus):**
```
docker compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d prometheus grafana
```
Grafana: http://localhost:3000 (admin/admin)
Prometheus: http://localhost:9090
