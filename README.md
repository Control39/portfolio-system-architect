# Portfolio System Architect

This repository contains a comprehensive portfolio system for a Lead AI Systems Architect, demonstrating advanced capabilities in AI-driven career development, cloud reasoning, and system architecture.

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
